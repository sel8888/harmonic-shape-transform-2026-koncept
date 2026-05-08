# HST Validation Report
**Harmonic Shape Transform — Full Benchmark Results**  
Pavel Krahulík · May 2026 · doi.org/10.5281/zenodo.20059602

---

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
| CUDA version | 12.9 |
| CuPy version | 14.0 |
| GPU VRAM | 12GB |
| Precision | float64 throughout |
| Reproducible | 100% |

</td>
</tr>
</table>

---

## 1. HST Note & Dual Note — Standalone

<table>
<tr>
<td width="50%" valign="top">

### Single Note
| Metric | Value |
|--------|-------|
| Mean geo error | 0.129 |
| Median geo error | 0.120 |
| Time (CPU) | 0.805s |
| Time (GPU) | 0.844s |
| Wins vs Random→ZoomOut | 67/99 |
| Speedup vs ZoomOut | 53× |

</td>
<td width="50%" valign="top">

### Dual Note
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

## 2. HST as Universal Initializer

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

## 3. GPU Acceleration & CPU vs GPU

<table>
<tr>
<td width="50%" valign="top">

### Speedup

| Method | CPU | GPU | Speedup |
|--------|-----|-----|---------|
| HST Note | 0.805s | 0.844s | ~1× |
| ZoomOut NN | 42.8s | 6.62s | **6.5×** |
| FMaps NN | ~15s | 1.02s | **~15×** |
| Full pipeline | 142 min | 13 min | **11×** |

</td>
<td width="50%" valign="top">

### Identical Results

| Metric | CPU | GPU |
|--------|-----|-----|
| HST Note wins | 67/99 | 66/99 |
| HST+ZoomOut wins | 32/99 | 33/99
