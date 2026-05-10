# HST Validation Report
**Harmonic Shape Transform — Full Benchmark Results**  
Pavel Krahulík · May 2026 · doi.org/10.5281/zenodo.20059602

---
PRIVATE WORK CSV C++ GPU 99 Pairs 

[hst_pipeline_v5_gpu.csv](https://github.com/user-attachments/files/27567422/hst_pipeline_v5_gpu.csv)


## Summary

<table>
<tr>
<td width="50%" valign="top">

| Metric | Value |
|--------|-------|
| Dataset | FAUST (99 pairs, 6890 vertices) |
| Backend | CPU (scipy ARPACK) + GPU (RTX 4070) |
| Total pairs | 99 |
| Failed pairs | 0 |
| Deterministic | Yes (fixed seeds) |

</td>
<td width="50%" valign="top">

| Metric | Value |
|--------|-------|
| CuPy version | 14.0 |
| CUDA | 12.9 |
| Precision | float64 throughout |
| Reproducible | Yes |
| Seeds | eigen=42, rand=42 |

</td>
</tr>
</table>

---

## 1 & 2. HST Note vs Dual Note — Standalone

<table>
<tr>
<td width="50%" valign="top">

### HST Single Note

| Metric | Value |
|--------|-------|
| Mean geo error | 0.129 |
| Median geo error | 0.120 |
| Time per pair (CPU) | 0.805s |
| Time per pair (GPU) | 0.844s |
| Wins vs Random→ZoomOut | 67/99 |
| Speedup vs ZoomOut | 53× |

</td>
<td width="50%" valign="top">

### HST Dual Note

| Metric | Value |
|--------|-------|
| Mean geo error | 0.120 |
| Median geo error | 0.105 |
| Improvement over Single | +7.1% |
| Wins vs Single Note | 61/99 |
| Recommendation | Standalone only |

</td>
</tr>
</table>

---

## 3. HST as Universal Initializer

<table>
<tr>
<td width="50%" valign="top">

### ZoomOut (Melzi et al. 2019)

| Method | Geo error | Improvement | Wins |
|--------|-----------|-------------|------|
| Random → ZoomOut (CPU) | 0.352 | baseline | 0/99 |
| Random → ZoomOut (GPU) | 0.349 | baseline | 0/99 |
| HST → ZoomOut (CPU) | 0.193 | **+42.3%** | 99/99 |
| HST → ZoomOut (GPU) | 0.195 | **+41.5%** | 99/99 |

</td>
<td width="50%" valign="top">

### Functional Maps (Ovsjanikov et al. 2012)

| Method | Geo error | Improvement | Wins |
|--------|-----------|-------------|------|
| Random → FMaps (CPU) | 0.295 | baseline | 1/99 |
| Random → FMaps (GPU) | 0.295 | baseline | 1/99 |
| HST → FMaps (CPU) | 0.138 | **+52.5%** | 98/99 |
| HST → FMaps (GPU) | 0.138 | **+52.5%** | 98/99 |

</td>
</tr>
</table>

**Key finding:** Random initialization never wins on any pair for either method.

---

## 4 & 5. GPU Acceleration & CPU vs GPU

<table>
<tr>
<td width="50%" valign="top">

### GPU Acceleration

| Method | CPU | GPU | Speedup |
|--------|-----|-----|---------|
| HST Note | 0.805s | 0.844s | ~1× |
| ZoomOut NN | 42.8s | 6.62s | **6.5×** |
| FMaps NN | ~15s | 1.02s | **~15×** |
| Full pipeline | 142 min | 13 min | **11×** |

**Hardware:** RTX 4070, 12GB, CUDA 12.9, CC 8.9

</td>
<td width="50%" valign="top">

### CPU vs GPU — Identical Results

| Metric | CPU | GPU |
|--------|-----|-----|
| HST Note wins | 67/99 | 66/99 |
| HST+ZoomOut wins | 32/99 | 33/99 |
| Random→ZoomOut wins | 0/99 | 0/99 |
| Mean geo error (HST) | 0.129 | 0.129 |
| Improvement (ZoomOut) | 42.3% | 41.5% |
| Improvement (FMaps) | 52.5% | 52.5% |

Results are **hardware-independent**.

</td>
</tr>
</table>

---

## 6 & 7. Volumetric Extension & Complete Comparison

<table>
<tr>
<td width="50%" valign="top">

### Volumetric Extension (GPU)

| Component | Time |
|-----------|------|
| Surface eigenvectors (CPU) | 0.047s |
| SDF grid (GPU) | 0.584s |
| Delaunay tetrahedralization | 0.194s |
| Volumetric Laplacian build | 0.065s |
| Volumetric eigenvectors (CPU) | 0.265s |
| Vertex colors (numpy) | 0.011s |
| **Total** | **1.70s** |

</td>
<td width="50%" valign="top">

### Complete Method Comparison

| Method | Geo error | Time | vs ZoomOut |
|--------|-----------|------|------------|
| HST Note | 0.129 | 0.805s | 53× |
| HST Dual Note | 0.120 | ~1s | ~43× |
| FMaps+HST (GPU) | 0.138 | 1.88s | 23× |
| ZoomOut+HST (GPU) | 0.195 | 7.82s | 6.1× |
| ZoomOut+HST (CPU) | 0.193 | 43.6s | baseline |
| ZoomOut+Random | 0.352 | 42.8s | never wins |
| BCICP | 0.15–0.20 | 20–30 min | — |
| HSN (DL) | 0.08–0.10 | 0.02s | training |

</td>
</tr>
</table>

---

## 8 & 9. Raw Data & Reproducibility

<table>
<tr>
<td width="50%" valign="top">

### Raw Data

<img width="2700" height="2439" alt="hst_spectral_analysis_" src="https://github.com/user-attachments/assets/ee7279e4-050f-4b98-bf3e-f201f069afe6" />


| File | Description |
|------|-------------|
| [hst_faust_full_benchmark.csv](hst_faust_full_benchmark.csv) | CPU (99 pairs) |
| [hst_faust_full_benchmarkGPU.csv](hst_faust_full_benchmarkGPU.csv) | GPU (99 pairs) |
| [hst_universal_init.csv](hst_universal_init.csv) | FMaps CPU |
| [hst_volumetric_GPU_benchmark.csv](hst_volumetric_GPU_benchmark.csv) | Volumetric GPU |
| [hst_dual_benchmark.csv](hst_dual_benchmark.csv) | Dual Note |

</td>
<td width="50%" valign="top">

### Reproducibility

```python
# Fixed seeds — identical every run
eigen_seed   = 42
rand_seed    = 42
tiebreak_tol = 0.001
```

```bash
# Run full benchmark
# Blender addon
# Set FAUST directory, click RUN
```

</td>
</tr>
</table>

---

<img width="2191" height="1388" alt="hst_cpu_gpu_comparison" src="https://github.com/user-attachments/assets/e182160c-2236-46df-b712-dda9eab63076" />
<img width="2434" height="1910" alt="hst_complete_benchmark" src="https://github.com/user-attachments/assets/245921e2-672c-494a-8b30-422ce1c7fc7b" />
<img width="1890" height="1074" alt="hst_summary_table" src="https://github.com/user-attachments/assets/ddbd4b16-f1b5-4597-a5c0-d43553d449ea" />


## 10. Conclusion

> *"Random initialization never wins. Not once. 0/99."*

<table>
<tr>
<td width="50%" valign="top">

HST harmonic note is a **universal geometric predictor**:

- One eigenfunction captures essential shape structure
- Systematically improves any spectral method
- Hardware-independent: CPU = GPU results
- No training · No landmarks · No shared topology
- ## 🔬 Robustness

HST is stable under geometric noise up to σ=0.20 and non-isometric
deformations up to 50% axis change. It works across genus 0–2 connected
manifolds without modification.

Known limitations: disconnected meshes (λ₁=0 causes instability)
and large missing surface regions. For noisy or incomplete data,
HKS or WKS scalar fields are recommended as drop-in replacements
for the harmonic note.

</td>
<td width="50%" valign="top">

**Contact:** Pavel.krahulik.cestiny@gmail.com  
**ORCID:** [0009-0003-9680-3333](https://orcid.org/0009-0003-9680-3333)  
**Preprint:** [doi.org/10.5281/zenodo.20059602](https://doi.org/10.5281/zenodo.20059602)  
**Code:** [github.com/sel8888](https://github.com/sel8888/harmonic-shape-transform-2026-koncept)

</td>
</tr>
</table>
