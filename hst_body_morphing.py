"""
HST Body Morphing v1.0 — Harmonic Shape Transform
Mapování mužské → ženské postavy přes harmonické nóty.

Author: Pavel Krahulík
License: GPL-3.0

Závislosti: numpy, scipy, matplotlib
  pip install numpy scipy matplotlib
"""

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D




def cotan(a, b):
    return np.dot(a, b) / (np.linalg.norm(np.cross(a, b)) + 1e-12)


def build_laplacian_and_mass(vertices, faces):
    n = len(vertices)
    L_data, L_row, L_col = [], [], []
    M_diag = np.zeros(n)
    for tri in faces:
        i, j, k = tri
        vi, vj, vk = vertices[i], vertices[j], vertices[k]
        area = 0.5 * np.linalg.norm(np.cross(vj - vi, vk - vi))
        if area < 1e-12:
            continue
        M_diag[i] += area / 3
        M_diag[j] += area / 3
        M_diag[k] += area / 3
        ci = cotan(vj - vi, vk - vi)
        cj = cotan(vi - vj, vk - vj)
        ck = cotan(vi - vk, vj - vk)
        for (a, b, w) in [(i, j, ck), (j, k, ci), (i, k, cj)]:
            wh = w * 0.5
            L_data += [-wh, -wh, wh, wh]
            L_row  += [a, b, a, b]
            L_col  += [b, a, a, b]
    L = sp.csr_matrix((L_data, (L_row, L_col)), shape=(n, n))
    M = sp.diags(np.maximum(M_diag, 1e-12))
    return L, M




def compute_harmonic_notes(vertices, faces, n_notes=6):
    L, M = build_laplacian_and_mass(vertices, faces)
    evals, evecs = eigsh(L, k=n_notes, M=M, sigma=0.0, which='LM',
                         tol=1e-5, maxiter=8000)
    idx = np.argsort(evals)
    evals = evals[idx]
    evecs = evecs[:, idx]
    for i in range(n_notes):
        u = evecs[:, i]
        norm = np.sqrt(u @ M @ u)
        evecs[:, i] = u / (norm + 1e-12)
    return evals, evecs


def normalize_to_01(v):
    return (v - v.min()) / (v.max() - v.min() + 1e-12)



def hst_map(vertices_a, note_a, vertices_b, note_b):
    mapped = np.zeros_like(vertices_a)
    residuals = np.zeros(len(vertices_a))
    for i, val in enumerate(note_a):
        j = np.argmin(np.abs(note_b - val))
        mapped[i] = vertices_b[j]
        residuals[i] = abs(note_b[j] - val)
    return mapped, residuals


# ─────────────────────────────────────────────
# 4. GENERÁTORY POSTAV
# ─────────────────────────────────────────────

def make_figure(profile_func, n_phi=36, n_h=70):
    """
    Vytvoří 3D postavu jako těleso rotace podle profilu.

    profile_func(h) → radius pro výšku h ∈ [0, 1]
      h=0 = nohy, h=1 = hlava
    """
    verts = []
    for j in range(n_h):
        h = j / (n_h - 1)
        r = profile_func(h)
        for i in range(n_phi):
            phi = 2 * np.pi * i / n_phi
            verts.append([r * np.cos(phi), r * np.sin(phi), h * 2.0 - 1.0])
    verts = np.array(verts)

    faces = []
    for j in range(n_h - 1):
        for i in range(n_phi):
            a = j * n_phi + i
            b = j * n_phi + (i + 1) % n_phi
            c = (j + 1) * n_phi + i
            d = (j + 1) * n_phi + (i + 1) % n_phi
            faces += [[a, b, c], [b, d, c]]

    # Uzavření spodku a vrchu
    cb = len(verts)
    verts = np.vstack([verts, [[0, 0, -1.0]]])
    for i in range(n_phi):
        faces.append([cb, (i + 1) % n_phi, i])

    ct = len(verts)
    verts = np.vstack([verts, [[0, 0, 1.0]]])
    top = (n_h - 1) * n_phi
    for i in range(n_phi):
        faces.append([ct, top + i, top + (i + 1) % n_phi])

    return np.array(verts), np.array(faces)


def male_profile(h):
    """Mužský profil — širší ramena, užší boky."""
    if h < 0.08:   return 0.12 + h * 0.8
    elif h < 0.15: return 0.18
    elif h < 0.45: return 0.16 + 0.04 * np.sin(np.pi * (h - 0.15) / 0.3)
    elif h < 0.52: return 0.22        # boky — mužské úzké
    elif h < 0.58: return 0.20        # pas
    elif h < 0.72: return 0.21        # hrudník
    elif h < 0.82: return 0.28        # ramena — široká
    elif h < 0.92: return 0.10        # krk
    else:          return 0.18 - (h - 0.92) * 0.8


def female_profile(h):
    """Ženský profil — širší boky, užší pas, užší ramena."""
    if h < 0.08:   return 0.10 + h * 0.7
    elif h < 0.15: return 0.15
    elif h < 0.45: return 0.14 + 0.05 * np.sin(np.pi * (h - 0.15) / 0.3)
    elif h < 0.55: return 0.26        # boky — ženské široké
    elif h < 0.62: return 0.16        # pas — výrazný
    elif h < 0.72: return 0.20        # hrudník
    elif h < 0.80: return 0.22        # ramena — užší
    elif h < 0.92: return 0.09        # krk
    else:          return 0.17 - (h - 0.92) * 0.7


# ─────────────────────────────────────────────
# 5. VIZUALIZACE
# ─────────────────────────────────────────────

def visualize(vm, fm, vf, ff, note_m1, note_f1, note_m2, note_f2,
              mapped, residuals):
    fig = plt.figure(figsize=(22, 12))
    fig.suptitle('HST: mužská → ženská postava — harmonické nóty a mapování',
                 fontsize=13)

    # Nóta k=1 muž
    ax1 = fig.add_subplot(241, projection='3d')
    ax1.scatter(vm[:, 0], vm[:, 1], vm[:, 2], c=note_m1, cmap='coolwarm', s=6)
    ax1.set_title('nóta k=1\nmuž (hlava↔nohy)', fontsize=9)
    ax1.axis('off'); ax1.view_init(elev=10, azim=45)

    # Nóta k=1 žena
    ax2 = fig.add_subplot(242, projection='3d')
    ax2.scatter(vf[:, 0], vf[:, 1], vf[:, 2], c=note_f1, cmap='coolwarm', s=6)
    ax2.set_title('nóta k=1\nžena (hlava↔nohy)', fontsize=9)
    ax2.axis('off'); ax2.view_init(elev=10, azim=45)

    # Nóta k=2 muž
    ax3 = fig.add_subplot(243, projection='3d')
    ax3.scatter(vm[:, 0], vm[:, 1], vm[:, 2], c=note_m2, cmap='RdYlBu', s=6)
    ax3.set_title('nóta k=2\nmuž (boční symetrie)', fontsize=9)
    ax3.axis('off'); ax3.view_init(elev=10, azim=45)

    # Nóta k=2 žena
    ax4 = fig.add_subplot(244, projection='3d')
    ax4.scatter(vf[:, 0], vf[:, 1], vf[:, 2], c=note_f2, cmap='RdYlBu', s=6)
    ax4.set_title('nóta k=2\nžena (boční symetrie)', fontsize=9)
    ax4.axis('off'); ax4.view_init(elev=10, azim=45)

    # Mapování — pohled zepředu
    ax5 = fig.add_subplot(245, projection='3d')
    ax5.scatter(vm[:, 0] - 1.2, vm[:, 1], vm[:, 2],
                c=note_m1, cmap='coolwarm', s=5, alpha=0.5)
    ax5.scatter(vf[:, 0] + 1.2, vf[:, 1], vf[:, 2],
                c=note_f1, cmap='coolwarm', s=5, alpha=0.5)
    step = max(1, len(vm) // 80)
    for i in range(0, len(vm), step):
        j = np.argmin(np.abs(note_f1 - note_m1[i]))
        col = plt.cm.coolwarm(note_m1[i])
        ax5.plot([vm[i, 0] - 1.2, vf[j, 0] + 1.2],
                 [vm[i, 1], vf[j, 1]],
                 [vm[i, 2], vf[j, 2]],
                 color=col, alpha=0.2, lw=0.5)
    ax5.set_title(f'HST mapování muž→žena\nmean res={np.mean(residuals):.4f}',
                  fontsize=9)
    ax5.axis('off'); ax5.view_init(elev=10, azim=90)

    # Mapování — pohled zboku
    ax6 = fig.add_subplot(246, projection='3d')
    ax6.scatter(vm[:, 0] - 1.2, vm[:, 1], vm[:, 2],
                c=note_m1, cmap='coolwarm', s=5, alpha=0.5)
    ax6.scatter(vf[:, 0] + 1.2, vf[:, 1], vf[:, 2],
                c=note_f1, cmap='coolwarm', s=5, alpha=0.5)
    for i in range(0, len(vm), step):
        j = np.argmin(np.abs(note_f1 - note_m1[i]))
        col = plt.cm.coolwarm(note_m1[i])
        ax6.plot([vm[i, 0] - 1.2, vf[j, 0] + 1.2],
                 [vm[i, 1], vf[j, 1]],
                 [vm[i, 2], vf[j, 2]],
                 color=col, alpha=0.2, lw=0.5)
    ax6.set_title('HST mapování\npohled zboku', fontsize=9)
    ax6.axis('off'); ax6.view_init(elev=10, azim=0)

    # Profily
    ax7 = fig.add_subplot(247)
    h_vals = np.linspace(0, 1, 200)
    rm = [male_profile(h) for h in h_vals]
    rf = [female_profile(h) for h in h_vals]
    z_vals = np.array(h_vals) * 2 - 1
    ax7.plot(rm, z_vals, color='#378add', lw=2, label='muž')
    ax7.plot([-r for r in rm], z_vals, color='#378add', lw=2)
    ax7.plot(rf, z_vals, color='#d85a30', lw=2, label='žena')
    ax7.plot([-r for r in rf], z_vals, color='#d85a30', lw=2)
    ax7.fill_betweenx(z_vals, rm, rf, alpha=0.15, color='purple',
                      label='rozdíl proporcí')
    ax7.axhline(0.52 * 2 - 1, color='gray', lw=0.5, ls=':', alpha=0.5)
    ax7.text(0.3, 0.52 * 2 - 1 + 0.03, 'boky', fontsize=7, color='gray')
    ax7.axhline(0.80 * 2 - 1, color='gray', lw=0.5, ls=':', alpha=0.5)
    ax7.text(0.3, 0.80 * 2 - 1 + 0.03, 'ramena', fontsize=7, color='gray')
    ax7.set_title('profily postav\n(průřez)', fontsize=9)
    ax7.set_xlabel('radius'); ax7.set_ylabel('výška')
    ax7.legend(fontsize=8)
    ax7.spines[['top', 'right']].set_visible(False)

    # Histogram reziduálů
    ax8 = fig.add_subplot(248)
    ax8.hist(residuals, bins=35, color='#7f77dd', edgecolor='white', lw=0.3)
    ax8.axvline(np.mean(residuals), color='#d85a30', lw=1.5, ls='--',
                label=f'průměr: {np.mean(residuals):.4f}')
    ax8.set_title('reziduály mapování\nmuž→žena', fontsize=9)
    ax8.set_xlabel('|φ̃_žena − φ̃_muž|')
    ax8.set_ylabel('počet bodů')
    ax8.legend(fontsize=8)
    ax8.spines[['top', 'right']].set_visible(False)

    plt.tight_layout()
    plt.savefig('hst_body_morphing.png', dpi=150, bbox_inches='tight')
    print('Výsledek uložen jako hst_body_morphing.png')
    plt.show()


# ─────────────────────────────────────────────
# 6. HLAVNÍ DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("HST Body Morphing v1.0")
    print("======================")

    print("\n[1/4] Generuji postavy...")
    vm, fm = make_figure(male_profile,   n_phi=36, n_h=70)
    vf, ff = make_figure(female_profile, n_phi=36, n_h=70)
    print(f"      Mužská:  {len(vm)} vrcholů, {len(fm)} trojúhelníků")
    print(f"      Ženská:  {len(vf)} vrcholů, {len(ff)} trojúhelníků")

    print("[2/4] Počítám harmonické nóty...")
    evals_m, evecs_m = compute_harmonic_notes(vm, fm)
    evals_f, evecs_f = compute_harmonic_notes(vf, ff)
    print(f"      Muž:  λ = {np.round(evals_m, 4)}")
    print(f"      Žena: λ = {np.round(evals_f, 4)}")

    note_m1 = normalize_to_01(evecs_m[:, 1])  # osa hlava↔nohy
    note_f1 = normalize_to_01(evecs_f[:, 1])
    note_m2 = normalize_to_01(evecs_m[:, 2])  # boční symetrie
    note_f2 = normalize_to_01(evecs_f[:, 2])

    print("[3/4] HST mapování muž → žena...")
    mapped, residuals = hst_map(vm, note_m1, vf, note_f1)
    print(f"      Průměrný reziduál: {np.mean(residuals):.5f}")
    print(f"      Max reziduál:      {np.max(residuals):.5f}")

    print("[4/4] Vizualizuji...")
    visualize(vm, fm, vf, ff, note_m1, note_f1, note_m2, note_f2,
              mapped, residuals)
