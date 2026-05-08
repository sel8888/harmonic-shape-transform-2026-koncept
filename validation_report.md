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
| Dataset | FAUST (99 consecutive pairs, 6890 vertices each) |
| Backend tested | CPU (scipy ARPACK) + GPU (RTX 4070, CuPy 14.0, CUDA 12.9) |
| Total pairs | 99 |
| Failed pairs | 0 |
| Deterministic | Yes (fixed seeds, fully reproducible) |

</td>
<td width="50%" valign="top">

## 1. HST Note — Standalone

| Metric | Value |
|--------|-------|
| Mean geo error | 0.129 |
| Median geo error | 0.120 |
| Time per pair (CPU) | 0.805s |
| Time per pair (GPU) | 0.844s |
| Wins vs Random→ZoomOut | 67/99 |
| Speedup vs ZoomOut | 53× |

</td>
</tr>
</table>

---

## 2. HST Dual Note — Standalone

<table>
<tr>
<td width="50%" valign="top">

| Metric | Value |
|--------|-------|
| Mean geo error | 0.120 |
| Median geo error | 0.105 |
| Improvement over Single | +7.1% |
| Wins vs Single Note | 61/99 |
| Recommendation | Use as standalone — not as initializer |

</td>
<td width="50%" valign="top">

## 3. HST as Universal Initializer

### ZoomOut (Melzi et al. 2019)

| Method | Geo error | Improvement | Wins |
|--------|-----------|-------------|------|
| Random → ZoomOut (CPU) | 0.352 | baseline | 0/99 |
| Random → ZoomOut (GPU) | 0.349 | baseline | 0/99 |
| HST → ZoomOut (CPU) | 0.193 | **+42.3%** | 99/99 |
| HST → ZoomOut (GPU) | 0.195 | **+41.5%** | 99/99 |

</td>
</tr>
</table>

---

<table>
<tr>
<td width="50%" valign="top">

### Functional Maps (Ovsjanikov
