## Full FAUST GPU Benchmark — 99 Pairs (RTX 4070)

### Results

| Method | Mean geo error | Time | vs CPU |
|--------|---------------|------|--------|
| HST Note | 0.129 | 0.844s | — |
| Random → ZoomOut (GPU) | 0.349 | 6.98s | **6.1×** |
| HST Note → ZoomOut (GPU) | **0.195** | 7.82s | **6.1×** |

- Random → ZoomOut wins: **0/99 pairs** (identical to CPU benchmark)
- HST init improvement: **41.5%** average (median 51.0%)
- HST Note wins: **66/99 pairs**

### Total Benchmark Time (99 pairs)

| Scenario | Time |
|----------|------|
| CPU — HST only | 1.3 min |
| CPU — HST + ZoomOut | 142 min |
| **GPU — HST + ZoomOut** | **13 min** |

GPU reduces full pipeline time from **142 minutes to 13 minutes** — 
an 11× speedup with identical accuracy.

<img width="2380" height="740" alt="hst_gpu_final" src="https://github.com/user-attachments/assets/0ed44b8c-c171-4e70-ba2b-962e97392178" />

### Analysis

The GPU acceleration comes entirely from the ZoomOut nearest-neighbor
search component. For each ZoomOut iteration, the algorithm must find
the closest point in k-dimensional spectral space for all 6890 vertices
simultaneously. This is a highly parallelizable operation — exactly the
type of workload where GPU excels.

The functional map matrix C is computed on CPU in float64 for numerical
accuracy. Only the nearest-neighbor distance computation is offloaded to
GPU in float64, which provides the speedup without sacrificing precision.

Eigenvectors remain on CPU because scipy ARPACK sparse solver computes
only k=2 eigenvectors directly. GPU full eigendecomposition (eigh) would
compute all 6890 eigenvectors — fundamentally slower for small k regardless
of GPU speed.

### Consistency

GPU results are fully consistent with CPU benchmark:
- Same geo error values (float64 precision preserved)
- Same winner distribution (Random→ZoomOut never wins)
- Same HST init improvement (~42%)

This confirms that GPU acceleration does not introduce any numerical
artifacts or changes in result quality.

> **Note:** To the best of the author's knowledge, this may be the first
> publicly documented GPU-accelerated benchmark of spectral shape
> correspondence (HST + ZoomOut) on the FAUST dataset using a pure Python
> implementation (CuPy + scipy). The official ZoomOut implementation
> (Melzi et al., 2019) is MATLAB-only with no GPU support. Existing Python
> ports of ZoomOut are CPU-only. This benchmark represents an independent
> contribution to the reproducibility and accessibility of spectral shape
> matching methods.

### Hardware Note

Tested on NVIDIA RTX 4070 (12GB VRAM, CUDA 12.9, Compute Capability 8.9).
CuPy 14.0.1 with nvidia-cusolver-cu12.
CPU: scipy 1.17.1, ARPACK sparse eigensolver.

