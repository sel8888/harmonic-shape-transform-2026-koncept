"""
HST Spectral Core v1.1 — Harmonic Shape Transform
Funkční implementace s cotangent Laplaceovou maticí, mass maticí,
eigenfunkcemi (harmonickými nótami), normalizací a HST mapováním.

Author: Pavel Krahulík
License: GPL-3.0

Závislosti: numpy, scipy, matplotlib, trimesh (pip install numpy scipy matplotlib trimesh)
"""

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import matplotlib.tri as mtri


# ─────────────────────────────────────────────
# 1. SESTAVENÍ COTANGENT LAPLACEOVY MATICE
# ─────────────────────────────────────────────

def cotan(a, b):
    """Kotangens úhlu mezi vektory a, b."""
    cos_ab = np.dot(a, b)
    sin_ab = np.linalg.norm(np.cross(a, b))
    return cos_ab / (sin_ab + 1e-12)


def build_laplacian_and_mass(vertices, faces):
    """
    Sestaví cotangent Laplaceovu matici L a diagonální mass matici M
    pro trojúhelníkovou síť.

    Parametry
    ----------
    vertices : (n, 2) nebo (n, 3) pole vrcholů
    faces    : (m, 3) pole trojúhelníků (indexy)

    Vrací
    ------
    L : scipy sparse (n, n) — cotangent Laplacian (pozitivně semidefinitní)
    M : scipy sparse (n, n) diagonální — mass matice (plocha okolí vrcholu)
    """
    n = len(vertices)
    verts = vertices if vertices.shape[1] == 3 else np.column_stack([vertices, np.zeros(n)])

    L_data, L_row, L_col = [], [], []
    M_diag = np.zeros(n)

    for tri in faces:
        i, j, k = tri
        vi, vj, vk = verts[i], verts[j], verts[k]

        # Plocha trojúhelníku
        area = 0.5 * np.linalg.norm(np.cross(vj - vi, vk - vi))
        M_diag[i] += area / 3.0
        M_diag[j] += area / 3.0
        M_diag[k] += area / 3.0

        # Kotangenty protilehlých úhlů pro každou hranu
        # Hrana j-k: protilehlý úhel u vrcholu i
        cot_i = cotan(vj - vi, vk - vi)
        # Hrana i-k: protilehlý úhel u vrcholu j
        cot_j = cotan(vi - vj, vk - vj)
        # Hrana i-j: protilehlý úhel u vrcholu k
        cot_k = cotan(vi - vk, vj - vk)

        # Symetrické příspěvky: w_ij = (cot_k) / 2
        for (a, b, w) in [(i, j, cot_k), (j, k, cot_i), (i, k, cot_j)]:
            wh = w * 0.5
            L_data += [-wh, -wh, wh, wh]
            L_row  += [a, b, a, b]
            L_col  += [b, a, a, b]

    L = sp.csr_matrix((L_data, (L_row, L_col)), shape=(n, n))
    M = sp.diags(np.maximum(M_diag, 1e-12))
    return L, M


# ─────────────────────────────────────────────
# 2. VÝPOČET HARMONICKÝCH NÓT
# ─────────────────────────────────────────────

def compute_harmonic_notes(vertices, faces, n_notes=8):
    """
    Spočítá harmonické nóty — normalizované Laplaceovy eigenfunkce.

    Parametry
    ----------
    vertices : (n, 2|3) pole vrcholů
    faces    : (m, 3) pole trojúhelníků
    n_notes  : počet eigenfunkcí (nót) k výpočtu

    Vrací
    ------
    eigenvalues  : (n_notes,) vlastní čísla (frekvence nót)
    eigenvectors : (n_vertices, n_notes) normalizované harmonické nóty
    """
    L, M = build_laplacian_and_mass(vertices, faces)

    # Regularizace pro numerickou stabilitu
    eps = 1e-9
    L_reg = L + eps * sp.eye(len(vertices))

    # Zobecněný problém vlastních čísel: L u = λ M u
    # 'SM' = Smallest Magnitude — nejnižší frekvence (globální tvar)
    eigenvalues, eigenvectors = eigsh(
        L_reg, k=n_notes, M=M, which='SM', tol=1e-6, maxiter=2000
    )

    # Seřazení podle velikosti vlastního čísla
    idx = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Normalizace každé nóty: L2 norma přes mass matici = 1
    for i in range(n_notes):
        u = eigenvectors[:, i]
        norm = np.sqrt(u @ M @ u)
        eigenvectors[:, i] = u / (norm + 1e-12)

    return eigenvalues, eigenvectors


def normalize_to_01(vec):
    """Normalizuje vektor do [0, 1] pro mapování."""
    vmin, vmax = vec.min(), vec.max()
    return (vec - vmin) / (vmax - vmin + 1e-12)


# ─────────────────────────────────────────────
# 3. HST MAPOVÁNÍ
# ─────────────────────────────────────────────

def hst_map(vertices_a, note_a, vertices_b, note_b):
    """
    Harmonic Shape Transform: namapuje body tvaru A na tvar B
    přes normalizované hodnoty harmonických nót.

    Pro každý bod x ∈ A najde bod y ∈ B takový, že
    f̃_B(y) ≈ f̃_A(x)   (stejná hodnota normalizované nóty)

    Parametry
    ----------
    vertices_a : (n, d) body tvaru A
    note_a     : (n,) harmonická nóta na A (normalizovaná do [0,1])
    vertices_b : (m, d) body tvaru B
    note_b     : (m,) harmonická nóta na B (normalizovaná do [0,1])

    Vrací
    ------
    mapped_points : (n, d) body na tvaru B odpovídající bodům A
    residuals     : (n,) rozdíly hodnot nót (chyba mapování)
    """
    mapped = np.zeros_like(vertices_a)
    residuals = np.zeros(len(vertices_a))

    for i, val_a in enumerate(note_a):
        diffs = np.abs(note_b - val_a)
        j_best = np.argmin(diffs)
        mapped[i] = vertices_b[j_best]
        residuals[i] = diffs[j_best]

    return mapped, residuals


# ─────────────────────────────────────────────
# 4. GENERÁTORY TESTOVACÍCH SÍTÍ (2D)
# ─────────────────────────────────────────────

def make_disk_mesh(n=20):
    """Disk (kruh) — pravidelná trojúhelníková síť."""
    pts = []
    for i in range(n):
        for j in range(n):
            x = (i / (n-1)) * 2 - 1
            y = (j / (n-1)) * 2 - 1
            if x*x + y*y <= 0.9:
                pts.append([x, y])
    verts = np.array(pts)
    tri = mtri.Triangulation(verts[:, 0], verts[:, 1])
    return verts, tri.triangles


def make_ellipse_mesh(n=20, a=0.9, b=0.5):
    """Elipsa s poloosami a, b."""
    pts = []
    for i in range(n):
        for j in range(n):
            x = (i / (n-1)) * 2 - 1
            y = (j / (n-1)) * 2 - 1
            if (x/a)**2 + (y/b)**2 <= 1:
                pts.append([x, y])
    verts = np.array(pts)
    tri = mtri.Triangulation(verts[:, 0], verts[:, 1])
    return verts, tri.triangles


def make_square_mesh(n=20):
    """Čtverec."""
    pts = []
    for i in range(n):
        for j in range(n):
            x = (i / (n-1)) * 2 - 1
            y = (j / (n-1)) * 2 - 1
            if abs(x) <= 0.85 and abs(y) <= 0.85:
                pts.append([x, y])
    verts = np.array(pts)
    tri = mtri.Triangulation(verts[:, 0], verts[:, 1])
    return verts, tri.triangles


# ─────────────────────────────────────────────
# 5. VIZUALIZACE
# ─────────────────────────────────────────────

def visualize_hst(verts_a, faces_a, verts_b, faces_b,
                  note_a, note_b, mapped, residuals,
                  name_a="A", name_b="B"):
    """
    4-panelová vizualizace:
      1. Harmonická nóta na tvaru A
      2. Harmonická nóta na tvaru B
      3. HST mapování (čáry A→B)
      4. Histogram reziduálů
    """
    fig, axes = plt.subplots(1, 4, figsize=(18, 4.5))
    fig.suptitle("Harmonic Shape Transform (HST)", fontsize=13, fontweight='normal', y=1.01)
    cmap = 'coolwarm'

    # Panel 1 — nóta na A
    ax = axes[0]
    tc_a = ax.tripcolor(verts_a[:, 0], verts_a[:, 1], faces_a,
                        facecolors=np.mean(note_a[faces_a], axis=1),
                        cmap=cmap, shading='flat')
    ax.triplot(verts_a[:, 0], verts_a[:, 1], faces_a, color='gray', lw=0.2, alpha=0.3)
    plt.colorbar(tc_a, ax=ax, fraction=0.046)
    ax.set_title(f"harmonická nóta φ_A\n({name_a})", fontsize=10)
    ax.set_aspect('equal'); ax.axis('off')

    # Panel 2 — nóta na B
    ax = axes[1]
    tc_b = ax.tripcolor(verts_b[:, 0], verts_b[:, 1], faces_b,
                        facecolors=np.mean(note_b[faces_b], axis=1),
                        cmap=cmap, shading='flat')
    ax.triplot(verts_b[:, 0], verts_b[:, 1], faces_b, color='gray', lw=0.2, alpha=0.3)
    plt.colorbar(tc_b, ax=ax, fraction=0.046)
    ax.set_title(f"harmonická nóta φ_B\n({name_b})", fontsize=10)
    ax.set_aspect('equal'); ax.axis('off')

    # Panel 3 — mapování A→B
    ax = axes[2]
    ax.scatter(verts_a[:, 0] - 1.5, verts_a[:, 1], c=note_a, cmap=cmap, s=10, zorder=3)
    ax.scatter(verts_b[:, 0] + 1.5, verts_b[:, 1], c=note_b, cmap=cmap, s=10, zorder=3)
    n_lines = min(80, len(verts_a))
    step = max(1, len(verts_a) // n_lines)
    for i in range(0, len(verts_a), step):
        xa = verts_a[i, 0] - 1.5
        ya = verts_a[i, 1]
        xb = mapped[i, 0] + 1.5
        yb = mapped[i, 1]
        color = plt.cm.coolwarm(note_a[i])
        ax.plot([xa, xb], [ya, yb], color=color, alpha=0.35, lw=0.7)
    ax.set_title(f"HST mapování\n{name_a} → {name_b}", fontsize=10)
    ax.set_aspect('equal'); ax.axis('off')

    # Panel 4 — histogram reziduálů
    ax = axes[3]
    ax.hist(residuals, bins=30, color='#378add', edgecolor='white', linewidth=0.5)
    ax.set_title("reziduály mapování\n|φ̃_B(y) − φ̃_A(x)|", fontsize=10)
    ax.set_xlabel("chyba", fontsize=9)
    ax.set_ylabel("počet bodů", fontsize=9)
    mean_res = np.mean(residuals)
    ax.axvline(mean_res, color='#d85a30', lw=1.2, linestyle='--', label=f'průměr: {mean_res:.4f}')
    ax.legend(fontsize=8)
    ax.spines[['top', 'right']].set_visible(False)

    plt.tight_layout()
    plt.savefig("hst_result.png", dpi=150, bbox_inches='tight')
    print("Výsledek uložen jako hst_result.png")
    plt.show()


# ─────────────────────────────────────────────
# 6. HLAVNÍ DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("HST Spectral Core v1.1")
    print("======================")

    # --- Tvar A: disk ---
    print("\n[1/4] Sestavuji síť pro tvar A (disk)...")
    verts_a, faces_a = make_disk_mesh(n=22)
    print(f"      {len(verts_a)} vrcholů, {len(faces_a)} trojúhelníků")

    # --- Tvar B: elipsa ---
    print("[2/4] Sestavuji síť pro tvar B (elipsa)...")
    verts_b, faces_b = make_ellipse_mesh(n=22)
    print(f"      {len(verts_b)} vrcholů, {len(faces_b)} trojúhelníků")

    # --- Harmonické nóty ---
    print("[3/4] Počítám harmonické nóty (Laplaceovy eigenfunkce)...")
    evals_a, evecs_a = compute_harmonic_notes(verts_a, faces_a, n_notes=6)
    evals_b, evecs_b = compute_harmonic_notes(verts_b, faces_b, n_notes=6)

    # Použijeme druhou nótu (index 1) — první je triviální konstanta
    note_idx = 1
    note_a = normalize_to_01(evecs_a[:, note_idx])
    note_b = normalize_to_01(evecs_b[:, note_idx])

    print(f"      Vlastní čísla A: {np.round(evals_a, 4)}")
    print(f"      Vlastní čísla B: {np.round(evals_b, 4)}")

    # --- HST mapování ---
    print("[4/4] Provádím HST mapování disk → elipsa...")
    mapped, residuals = hst_map(verts_a, note_a, verts_b, note_b)
    print(f"      Průměrný reziduál: {np.mean(residuals):.5f}")
    print(f"      Max reziduál:      {np.max(residuals):.5f}")

    # --- Vizualizace ---
    print("\nVizualizuji výsledky...")
    visualize_hst(verts_a, faces_a, verts_b, faces_b,
                  note_a, note_b, mapped, residuals,
                  name_a="disk", name_b="elipsa")
