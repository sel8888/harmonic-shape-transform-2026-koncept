import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt

def create_shape_field(shape_type, size=200):
    """
    Vytvoří doménu (tvar) a vypočítá na ní skalární pole (f).
    Odpovídá sekci 7.1 a 7.2 patentové přihlášky.
    """
    grid = np.zeros((size, size))
    center = size // 2
    
    if shape_type == "circle": # Shape A
        y, x = np.ogrid[:size, :size]
        mask = (x - center)**2 + (y - center)**2 <= (size//3)**2
    else: # Shape B (Square)
        mask = np.zeros((size, size), dtype=bool)
        mask[size//4:3*size//4, size//4:3*size//4] = True
        
    grid[mask] = 1
    # Výpočet skalárního pole f (zde pomocí distance transform) [cite: 100]
    field = distance_transform_edt(grid)
    return field, mask

def normalize_field(field, mask):
    """
    Normalizace pole do rozsahu [0, 1].
    Odpovídá sekci 7.3 a Claim 2[cite: 106, 109, 150].
    """
    f_min, f_max = field[mask].min(), field[mask].max()
    normalized = np.zeros_like(field)
    normalized[mask] = (field[mask] - f_min) / (f_max - f_min)
    return normalized

# 1. Definice tvarů a polí (Claim 1a) [cite: 147]
field_a, mask_a = create_shape_field("circle")
field_b, mask_b = create_shape_field("square")

# 2. Normalizace polí (Claim 1b) [cite: 148]
norm_a = normalize_field(field_a, mask_a)
norm_b = normalize_field(field_b, mask_b)

# 3. Vizualizace HST (Claim 3 & 4) [cite: 151, 152]
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Zobrazení izočar (Level Sets) - to jsou ty tvé "noty" [cite: 22, 125]
levels = [0.2, 0.5, 0.8]
cp1 = axes[0].contour(norm_a, levels=levels, colors='white')
axes[0].imshow(norm_a, cmap='viridis')
axes[0].set_title("Shape A (Circle) - Normalized Field")

cp2 = axes[1].contour(norm_b, levels=levels, colors='white')
axes[1].imshow(norm_b, cmap='magma')
axes[1].set_title("Shape B (Square) - Normalized Field")

plt.suptitle("Harmonic Shape Transform: Matching by Normalized Values")
plt.show()

# Příklad mapování (Claim 1c): Najdeme bod na čtverci, který odpovídá středu kruhu [cite: 149]
val_at_center_a = norm_a[100, 100] # Hodnota 1.0 (střed)
matches_in_b = np.where(np.isclose(norm_b, val_at_center_a, atol=0.01))
print(f"Bod se skalární hodnotou {val_at_center_a:.2f} z kruhu mapuje na {len(matches_in_b[0])} bodů ve čtverci.")
