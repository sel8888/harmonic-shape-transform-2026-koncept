# HST Framework: Empirical Validation & Spectral Stability

[![Status: Research-Pass](https://img.shields.io/badge/Status-Research--Pass-success)](https://github.com/your-username/your-repo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 1. Research Overview
This report documents the rigorous validation of the **Harmonic Shape Transform (HST)** framework. By utilizing the **FAUST dataset** (6,890-vertex human manifolds), we tested the limits of spectral correspondence across non-isometric poses.

---

## 2. Quantitative Results (FAUST Benchmark)

| Mode | Eigenmodes ($k$) | Precision | Residual | Status |
| :--- | :---: | :---: | :---: | :--- |
| **HST_NOTE** | 1 | **98.98%** | 0.010196 | ✅ **PASS (Ideal)** |
| **HKS (Heat Kernel)** | 30 | **95.93%** | 0.040711 | ✅ **PASS (Robust)** |
| **FAUST SPECTRAL** | 19 | 50.47% | 0.495331 | ⚠️ **WARNING** |

---

## 3. Key Findings

### 🧬 HST_NOTE: The Semantic DNA
With a precision of **98.98%**, the "Harmonic Note" ($k=1$) proves to be an incredibly stable semantic anchor. 
* **Invariance:** Complete robustness against $SE(3)$ transformations (Rotation, Translation, Scale).
* **Efficiency:** Achieves near-perfect alignment with minimal computational cost.

### 🔥 HKS: Pose Stability
By substituting raw eigenfunctions with **Heat Kernel Signatures**, we achieved **95.93%** precision on highly deformed meshes. 
* **Diffusion:** HKS effectively filters high-frequency noise caused by joint movement.
* **Consistency:** Maintains correspondence where traditional spectral methods fail due to sign-flipping.

### 📉 The Spectral Limit (FAUST Benchmark)
The **50.47%** result in pure spectral mode confirms the phenomenon of **Eigenspace Degeneracy**. This occurs when high-frequency eigenfunctions "scatter" due to significant pose changes. This result defines the boundary where HST transitions from raw spectral data to stable scalar fields (HKS).

---

## 4. How to Reproduce
1. Open **Blender** with the HST Addon installed.
2. Load the source and target meshes from the **FAUST dataset**.
3. Run the validation suite:
   - Select `Mode: HST_NOTE` for semantic check.
   - Select `Mode: HKS` for pose-robust validation.
4. Review the generated **HST VALIDATION REPORT** in the console.

---

## 5. Acknowledgments & References
* **Dataset:** Bogo, F. et al. "FAUST: Dataset and evaluation for 3D mesh registration."

---
*© 2026 Pavel Krahulík. Independent Research Project.*
