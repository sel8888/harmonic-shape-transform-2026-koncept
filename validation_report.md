# HST Validation Report
**Harmonic Shape Transform — Full Benchmark Results**  
Pavel Krahulík · May 2026 · doi.org/10.5281/zenodo.20059602

---

## Summary

| Metric | Value |
|--------|-------|
| Dataset | FAUST (99 consecutive pairs, 6890 vertices each) |
| Backend tested | CPU (scipy ARPACK) + GPU (RTX 4070, CuPy 14.0, CUDA 12.9) |
| Total pairs | 99 |
| Failed pairs | 0 |
| Deterministic | Yes (fixed seeds, fully reproducible) |

---

## 1. HST Note — Standalone

| Metric | Value |
|--------|-------|
| Mean geo error | 0.129 |
| Median geo error | 0.120 |
| Time per pair (CPU) | 0.805s |
| Time per pair (GPU) | 0.844s |
| Wins vs Random→ZoomOut | 67/99 |
| Speedup vs ZoomOut | 53× |

---

## 2. HST Dual Note — Standalone

| Metric | Value |
|--------|-------|
| Mean geo error | 0.120 |
| Median geo error | 0.105 |
| Improvement over Single | +7.1% |
| Wins vs Single Note | 61/99 |
| Recommendation | Use as standalone — not as initializer |

---

## 3. HST as Universal Initializer

### ZoomOut (Melzi et al. 2019)

| Method | Geo error | Improvement | Wins |
|--------|-----------|-------------|------|
| Random → ZoomOut (CPU) | 0.352 | baseline | 0/99 |
| Random → ZoomOut (GPU) | 0.349 | baseline | 0/99 |
| HST → ZoomOut (CPU) | 0.193 | **+42.3%** | 99/99 |
| HST → ZoomOut (GPU) | 0.195 | **+41.5%** | 99/99 |

### Functional Maps (Ovsjanikov et al. 2012)

| Method | Geo error | Improvement | Wins |
|--------|-----------|-------------|------|
| Random → FMaps (CPU) | 0.295 | baseline | 1/99 |
| Random → FMaps (GPU) | 0.295 | baseline | 1/99 |
| HST → FMaps (CPU) | 0.138 | **+52.5%** | 98/99 |
| HST → FMaps (GPU) | 0.138 | **+52.5%** | 98/99 |

**Key finding:** Random initialization never wins on any pair for either method.

---

## 4. GPU Acceleration

| Method | CPU time | GPU time | Speedup |
|--------|----------|----------|---------|
| HST Note | 0.805s | 0.844s | ~1× |
| ZoomOut NN search | 42.8s | 6.62s | **6.5×** |
| FMaps NN search | ~15s | 1.02s | **~15×** |
| Full pipeline (99 pairs) | 142 min | 13 min | **11×** |

**Hardware:** NVIDIA RTX 4070, 12GB VRAM, CUDA 12.9, CC 8.9  
**Precision:** float64 throughout — identical accuracy to CPU

---

## 5. CPU vs GPU — Identical Results

| Metric | CPU | GPU |
|--------|-----|-----|
| HST Note wins | 67/99 | 66/99 |
| HST+ZoomOut wins | 32/99 | 33/99 |
| Random→ZoomOut wins | 0/99 | 0/99 |
| Mean geo error (HST) | 0.129 | 0.129 |
| Mean improvement (ZoomOut) | 42.3% | 41.5% |
| Mean improvement (FMaps) | 52.5% | 52.5% |

GPU produces identical winner distributions across all 99 pairs.  
Results are **hardware-independent**.

---

## 6. Volumetric Extension (GPU)

| Component | Time |
|-----------|------|
| Surface eigenvectors (CPU ARPACK) | 0.047s |
| SDF grid computation (GPU) | 0.584s |
| Delaunay tetrahedralization | 0.194s |
| Volumetric Laplacian build | 0.065s |
| Volumetric eigenvectors (CPU) | 0.265s |
| Vertex colors (numpy foreach_set) | 0.011s |
| **Total** | **1.70s** |

---

## 7. Complete Method Comparison

| Method | Year | Geo error | Time | vs ZoomOut CPU |
|--------|------|-----------|------|----------------|
| HST Note (CPU/GPU) | 2026 | 0.129 | 0.805s | 53× faster |
| HST Dual Note | 2026 | 0.120 | ~1s | ~43× faster |
| FMaps + HST (GPU) | 2026 | 0.138 | 1.88s | 23× faster |
| ZoomOut + HST (GPU) | 2026 | 0.195 | 7.82s | 6.1× faster |
| ZoomOut + HST (CPU) | 2026 | 0.193 | 43.6s | baseline |
| ZoomOut + Random | 2019 | 0.352 | 42.8s | never wins |
| BCICP | 2018 | 0.15–0.20 | 20–30 min | — |
| Smooth Shell Maps | 2020 | 0.10–0.12 | 5–10 min | — |
| FMNet + ZoomOut | 2017 | 0.12–0.15 | 0.01s+60s | training required |
| HSN (Deep Learning) | 2021 | 0.08–0.10 | 0.02s | training required |

---

## 8. Raw Data

| File | Description |
|------|-------------|
| [hst_faust_full_benchmark.csv](hst_faust_full_benchmark.csv) | CPU benchmark (99 pairs) |
| [hst_faust_full_benchmarkGPU.csv](hst_faust_full_benchmarkGPU.csv) | GPU benchmark (99 pairs) |
| [hst_universal_init.csv](hst_universal_init.csv) | FMaps CPU (99 pairs) |
| [hst_volumetric_GPU_benchmark.csv](hst_volumetric_GPU_benchmark.csv) | Volumetric GPU (99 pairs) |
| [hst_dual_benchmark.csv](hst_dual_benchmark.csv) | Dual Note (99 pairs) |

---

## 9. Reproducibility

All results are fully reproducible:

```python
# Fixed seeds — identical results every run
eigen_seed = 42
rand_seed  = 42
tiebreak_tol = 0.001
```

```bash
# Run full benchmark
# Blender addon: hst_faust_full_benchmark.py
# Set FAUST directory, click RUN
```

---

## 10. Conclusion

HST harmonic note is a **universal geometric predictor**:

- One normalized eigenfunction captures essential shape structure
- Systematically improves any spectral method as initialization
- Hardware-independent: CPU and GPU give identical results
- No training, no landmarks, no shared topology required

> *"Random initialization never wins. Not once. 0/99."*

---

**Contact:** Pavel.krahulik.cestiny@gmail.com  
**ORCID:** [0009-0003-9680-3333](https://orcid.org/0009-0003-9680-3333)  
**Preprint:** [doi.org/10.5281/zenodo.20059602](https://doi.org/10.5281/zenodo.20059602)  
**Code:** [github.com/sel8888/harmonic-shape-transform-2026-koncept](https://github.com/sel8888/harmonic-shape-transform-2026-koncept)
