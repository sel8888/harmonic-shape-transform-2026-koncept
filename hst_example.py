import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix, lil_matrix
from scipy.sparse.linalg import eigsh

def compute_harmonic_notes(mask, n_notes=5):
    """
    Vypočítá vlastní funkce Laplaceova operátoru na masce tvaru.
    Odpovídá Claimu 6: Harmonic Note Transform.
    """
    rows, cols = mask.shape
    # Mapování indexů pixelů uvnitř tvaru na matici
    pixels = np.argwhere(mask)
    pixel_to_idx = {tuple(p): i for i, p in enumerate(pixels)}
    n = len(pixels)
    
    # Sestavení diskrétní Laplaceovy matice (L)
    L = lil_matrix((n, n))
    for i, (r, c) in enumerate(pixels):
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        count = 0
        for nr, nc in neighbors:
            if (nr, nc) in pixel_to_idx:
                L[i, pixel_to_idx[(nr, nc)]] = 1
                count += 1
        L[i, i] = -count  # Diagonála (počet sousedů)

    # Výpočet vlastních čísel a funkcí (eigsh pro symetrické řídké matice)
    # Hledáme nejmenší vlastní čísla (SM = Smallest Magnitude)
    eigenvalues, eigenfunctions = eigsh(L.tocsr(), k=n_notes, which='SM')
    
    return eigenvalues, eigenfunctions, pixels

# 1. Příprava tvaru (např. Genus 1 - Donut/Ring pro Claim 4)
size = 60
mask = np.zeros((size, size), dtype=bool)
y, x = np.ogrid[:size, :size]
center = size // 2
# Donut
mask_outer = (x - center)**2 + (y - center)**2 <= (size//2.5)**2
mask_inner = (x - center)**2 + (y - center)**2 <= (size//6)**2
mask = mask_outer ^ mask_inner 

# 2. Výpočet harmonických nót (Claim 6)
n_notes = 6
evals, evecs, pixels = compute_harmonic_notes(mask, n_notes=n_notes)

# 3. Vizualizace první nenulové harmonické nóty (Fiedler vector / 1. mód)
# Poznámka: Index 0 je obvykle konstantní funkce (triviální řešení)
note_idx = 1 
field = np.zeros((size, size))
for i, (r, c) in enumerate(pixels):
    field[r, c] = evecs[i, note_idx]

# Normalizace pro HST (Claim 2)
f_min, f_max = field[mask].min(), field[mask].max()
normalized_note = (field - f_min) / (f_max - f_min)

plt.figure(figsize=(8, 6))
plt.imshow(normalized_note, cmap='RdBu_r')
plt.colorbar(label="Normalized Harmonic Value (0.0 - 1.0)")
plt.title(f"Harmonic Note # {note_idx} on Genus-1 Shape\n(Topology-Independent Identity)")
plt.show()
