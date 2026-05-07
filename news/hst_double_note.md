## 🔬 HST Dual Note — Double Eigenfunction Benchmark

hst_dual_benchmark.csv

HST Dual Note maps shapes in 2D spectral space (φ₁, φ₂) instead of 1D.
This resolves the left/right symmetry ambiguity of single-eigenfunction mapping.

### Results — 99 FAUST pairs, GPU backend

| Method | Geo error | vs Random ZoomOut |
|--------|-----------|-------------------|
| Random → ZoomOut | 0.352 | baseline |
| HST Single Note | 0.129 | wins 67/99 |
| **HST Dual Note** | **0.120** | **wins 61/99** |

### As Initializer — Single vs Dual

| Refinement | Random init | Single init | Dual init | Single better? |
|------------|------------|-------------|-----------|----------------|
| ZoomOut | 0.349 | **0.194** | 0.204 | ✅ Yes |
| FMaps | 0.295 | **0.138** | 0.223 | ✅ Yes |

### Key Findings

- Dual Note achieves **lower geo error as standalone** — 0.120 vs 0.129 (+7.1%)
- As initializer for ZoomOut and FMaps, **Single Note gives better results**
- The two roles are complementary, not contradictory:
  - Need fast standalone mapping → **use Dual Note**
  - Need to initialize ZoomOut/FMaps → **use Single Note**
- Instability on difficult pairs: second eigenfunction not always aligned with lateral axis

<img width="1000" height="600" alt="Graph_HTS_dual_note_GE" src="https://github.com/user-attachments/assets/a59822ba-afe6-4708-8b13-e33a76a903cf" />
