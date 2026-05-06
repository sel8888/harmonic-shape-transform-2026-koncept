# HST GPU Benchmark — Findings

**Hardware:** NVIDIA RTX 4070 (12GB VRAM, CUDA 12.9, CC 89)  
**Dataset:** FAUST tr_reg_000 → tr_reg_001 (6890 vertices)  
**Date:** May 2026

---

## Results

| Component | CPU | GPU | Speedup |
|-----------|-----|-----|---------|
| Eigenvectors (k=2) | 0.650s | 2.637s | 0.2× |
| HST mapping | 0.806s | 0.732s | 1.1× |
| **Total** | **~0.8s** | **~3.4s** | **0.2×** |

**Conclusion: CPU is faster than GPU for FAUST-scale meshes (6890 vertices).**

---

## Why GPU Does Not Help Here

**Eigenvectors** — scipy ARPACK is a sparse solver computing only k=2
eigenvectors. The GPU implementation (CuPy `linalg.eigh`) computes all
6890 eigenvectors and is inherently slower for small k.

**HST mapping** — 6890 nearest-neighbor lookups is too small to
compensate for CPU→GPU→CPU data transfer overhead.
GPU parallelism becomes advantageous at millions of operations.

---

## When GPU Would Help

GPU acceleration is expected to provide significant speedup for:

- Meshes with **100k+ vertices** where ARPACK also becomes slow
- **Batch processing** of hundreds of pairs in parallel
- **ZoomOut with large k_final** (k=200+) where NN search dominates

---

## Recommendation

For FAUST-scale benchmarks (6890 vertices), **CPU is the optimal backend.**
The HST addon automatically falls back to CPU — no configuration needed.

GPU support remains available in the addon for future testing on larger meshes.
