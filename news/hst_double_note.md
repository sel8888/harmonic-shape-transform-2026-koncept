## 🔬 HST Dual Note — Double Eigenfunction Benchmark

HST Dual Note maps shapes in 2D spectral space (φ₁, φ₂) instead of 1D.
This resolves the left/right symmetry ambiguity of single-eigenfunction mapping.

### Results — 99 FAUST pairs, GPU backend

| Method | Geo error | vs Single Note | vs Random ZoomOut |
|--------|-----------|----------------|-------------------|
| HST Single Note | 0.129 | baseline | wins 67/99 |
| **HST Dual Note** | **0.120** | **+7.1% better** | wins 61/99 |

### As Initializer — Single vs Dual

| Refinement | Random init | Single init | Dual init | Single better? |
|------------|------------|-------------|-----------|----------------|
| ZoomOut | 0.349 | **0.194** | 0.204 | ✅ Yes |
| FMaps | 0.295 | **0.138** | 0.223 | ✅ Yes |

### Key Findings

- Dual Note is **better as standalone** — wins on 61/99 pairs (+7.1%)
- Dual Note is **worse as initializer** — Single Note preferred for ZoomOut and FMaps
- Instability on difficult pairs: second eigenfunction not always aligned with lateral axis
- Single Note remains the recommended universal initializer

<img width="1000" height="600" alt="Graph_HTS_dual_note_GE" src="https://github.com/user-attachments/assets/a59822ba-afe6-4708-8b13-e33a76a903cf" />
