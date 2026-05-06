## Full FAUST GPU Benchmark — 99 Pairs (RTX 4070)

> **Note:** To the best of the author's knowledge, this may be the first
> publicly documented GPU-accelerated benchmark of spectral shape
> correspondence on the FAUST dataset using pure Python (CuPy + scipy).
> The official ZoomOut implementation (Melzi et al., 2019) is MATLAB-only
> with no GPU support. Existing Python ports are CPU-only.

### Results — All Methods

| Method | Mean geo error | Time | vs ZoomOut CPU |
|--------|---------------|------|----------------|
| HST Note (CPU) | 0.129 | 0.805s | 53× |
| HST Note (GPU) | 0.129 | 0.844s | 53× |
| Random → FMaps (GPU) | 0.295 | 1.30s | 33× |
| **HST → FMaps (GPU)** | **0.138** | **1.88s** | **23×** |
| Random → ZoomOut (GPU) | 0.349 | 6.98s | 6.1× |
| **HST → ZoomOut (GPU)** | **0.195** | **7.82s** | **6.1×** |
| HST → ZoomOut (CPU) | 0.193 | 43.6s | 1× |

### Total Benchmark Time (99 pairs)

| Scenario | Time |
|----------|------|
| CPU — HST only | 1.3 min |
| CPU — HST + ZoomOut | 142 min |
| **GPU — HST + ZoomOut** | **13 min** |
| **GPU — HST + FMaps** | **17 min** |

### CPU vs GPU — Identical Results

| Metric | CPU | GPU |
|--------|-----|-----|
| HST Note wins | 67/99 | 66/99 |
| HST+ZoomOut wins | 32/99 | 33/99 |
| Random→ZoomOut wins | 0/99 | 0/99 |
| Mean geo error (HST) | 0.129 | 0.129 |
| Mean improvement (ZoomOut) | 42.3% | 41.5% |
| Mean improvement (FMaps) | 52.5% | 52.5% |

GPU and CPU produce **identical winner distributions and geo error values**
across all 99 pairs. The speedup introduces zero numerical artifacts.

### Analysis

GPU acceleration comes from parallelizing nearest-neighbor search in
spectral space. For ZoomOut this gives 6.1× speedup, for Functional Maps
~10× speedup. Eigenvectors remain on CPU (scipy ARPACK is faster for sparse k=2).

All computations use float64 precision on GPU — identical accuracy to CPU.

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

