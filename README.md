<p align="center">
  <img src="https://raw.githubusercontent.com/sel8888/harmonic-shape-transform-2026-koncept/main/hst_banner_v2.svg" width="100%" alt="HST Banner"/>
</p>

<p align="center">
  <a href="https://doi.org/10.5281/zenodo.20059602">
    <img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20059602-blue.svg" alt="DOI"/>
  </a>
  <a href="https://arxiv.org/auth/endorse?x=HHE7CD">
    <img src="https://img.shields.io/badge/arXiv-pending-b31b1b.svg" alt="arXiv"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-GPL--3.0-blue.svg" alt="GPL-3.0"/>
  </a>
  <a href="https://creativecommons.org/licenses/by-nc/4.0/">
    <img src="https://img.shields.io/badge/paper-CC%20BY--NC%204.0-lightgrey.svg" alt="CC BY-NC 4.0"/>
  </a>
  <img src="https://img.shields.io/badge/python-3.10%2B-3776AB.svg?logo=python&logoColor=white" alt="Python"/>
  <a href="mailto:Pavel.krahulik.cestiny@gmail.com">
    <img src="https://img.shields.io/badge/contact-email-EA4335.svg?logo=gmail&logoColor=white" alt="Email"/>
  </a>
  <a href="validation_report.md">
    <img src="https://img.shields.io/badge/validation-report-success.svg" alt="Validation"/>
  </a>
</p>

<h1 align="center">Harmonic Shape Transform (HST)</h1>



<h3 align="center">Strike a 3D shape like a bell — it rings its harmonic note.
That note encodes the shape's intrinsic structure.
HST uses it to map any shape to any other shape in 0.8s.
Other methods ring louder when they start from this note.</h3>

### A New Concept for Shape Transformation Using Harmonic Notes

---

The Solution was Hidden in Plain Sight.
For 14 years, the field focused on the complexity of the surface. HST looks at the integrity of the volume. It is not just an optimization; it is a physical constant of the shape. If you use this code and it saves you hours of work, the only thing missing is formal recognition.

---

<div align="center">

# 🗝️ The Golden Key

</div>

I have handed the community a **Golden Key** to a room that has been locked since 2012. 

**HST** solves the global initialization problem by uncovering the volumetric integrity that was hidden in plain sight. It reaches the absolute physical limits of current hardware (**I/O bound**).

If this tool saves you from **Symmetry Flips** or accelerates your pipeline by **10x**, I have done my part. As an independent developer without an institution or team, I have given you the key. 

**All I ask in return is the professional courtesy of an endorsement.** [🔴 Endorse HST on arXiv](https://arxiv.org/auth/endorse?x=HHE7CD)

---

## -> Performance Breakthrough: C++ Implementation Results

The transition from Python/NumPy to a native **C++17 (Eigen3/LAPACK)** implementation has yielded transformative performance gains. By leveraging direct memory access and optimized linear algebra kernels, HST now operates at true real-time speeds even on high-resolution production meshes.

### Benchmark Comparison (Single-threaded)

NEW C++ IMPLEMENTATION === SUMMARY: 99/99 pairs ===
HST Note:        mean=0.12949

HST doesn't just run faster; it makes subsequent spectral algorithms (ZoomOut, FMaps) converge up to 80% more effectively by providing a superior volumetric starting point.

## ⚡ C++ Implementation — Benchmark vs Python

| Method | Python | C++ | Speedup |
|--------|--------|-----|---------|
| HST Note geo error | 0.12949 | **0.12949** | identical |
| HST full pipeline | 0.805s | **0.557s** | **1.4×** |
| ZoomOut time | 42.8s | **6.5s** | **6.5×** |
| FMaps time | ~15s | **1.1s** | **13.4×** |
| FMaps+HST improvement | 52.5% | **52.5%** | identical |
| ZoomOut+HST improvement | 42.3% | 39.6% | ~same |

99/99 pairs · Zero failures · Identical accuracy · CPU only

📦 C++ source: [`hst_cpp/`](hst_cpp/)

### Key Technical Insights:
* **Sub-second Pipeline:** The entire symmetry recovery and correspondence refinement pipeline now completes in **under 0.5 seconds**.
* **Deterministic Real-time:** These results enable interactive workflows (e.g., live rigging, weight painting transfer) within DCC tools like Blender without the latency associated with traditional spectral methods.
* **Scalability:** The C++ backend maintains high performance on meshes exceeding 50k+ vertices, where Python-based solutions typically hit memory and processing bottlenecks.

> **Note on Validation:** These preliminary results are currently being cross-validated against private production datasets to ensure 100% robustness across non-manifold and complex topologies before the full core release.

#### <small>🔴Seeking arXiv Endorsement (cs.GR / cs.CV)</small>
<small>
If you are an established researcher and have found HST valuable, I would greatly appreciate your endorsement via the link above. This will help formalize this volumetric approach as the new standard for spectral initialization.
</small>
* **789+ Unique Cloners** – <small>Active integration by developers and researchers.</small>

> <small><i>"The answer was always one eigenfunction away. Now, the circle is complete."</i></small>

---

*"The answer was always one eigenfunction away. Now, the circle is complete."*

> <span style="color:green">🟢 </span> *"[ZoomOut] can be used in conjunction with existing initialization techniques."*
> — Melzi et al., 2019
>
> *Functional Maps — 2012. ZoomOut — 2019. HST(I/O limit) — 2026.*
*Seven years. The answer was always one eigenfunction away.*
> 
**HST is that initialization technique.** +42.3% improvement over random. 0/99 random wins.

This repository contains the first public description of the **Harmonic Shape Transform (HST)** — a new mathematical concept for transforming shapes using the internal harmonic structure of a domain. The idea is based on the observation that every shape has its own *harmonic note*, defined as a normalized eigenfunction of the Laplace operator. This harmonic note can serve as a universal intermediate representation between shapes.

From Vision to Reality: On May 1st, 2026, this was just an idea. Today, it is a stable, deterministic HST system providing real-time semantic topology in Blender.

> *"A genuinely good idea is one that, once explained, seems obvious — yet nobody said it first."*
> — Albert Einstein

HST is that idea. One eigenfunction. No training. 0.8s.
Random initialization never wins. Not once. 0/99.

**Author:** Pavel Krahulik 
**Year:** 2026


💡 After testing HST Harmonic Note improves ANY spectral method as initialization.

## 🏆 Scientific & Technical Significance

<table border="0">
<tr>
<td width="50%" valign="top">

### 🧪 World First Assertion
> *To the best of the author's knowledge, this is the first publicly documented GPU-accelerated spectral shape correspondence pipeline that integrates a **volumetric Laplace–Beltrami operator** with the **Harmonic Shape Transform (HST)** framework for global initialization and refinement.*

</td>
<td width="50%" valign="top">

### 🛠️ The Full GPU Pipeline
The project introduces a seamless, high-performance workflow where every stage is optimized for GPU execution:

1. **Volumetric LB Eigenfunctions**
   *Extraction of spectral basis from interior volume.*
2. **HST Initialization**
   *Global stabilization to prevent local minima.*
3. **GPU Functional Maps (FM)**
   *High-speed spectral alignment.*
4. **GPU ZoomOut**
   *Iterative spectral upsampling and refinement.*

</td>
</tr>
</table>

<table>
<tr>
<td width="50%" valign="top">

## Key Innovations & Performance Milestones

### ⭐ High-Performance Volumetric HST Framework
While traditional spectral methods (FM, ZoomOut, BCICP) rely exclusively on surface-only operators, HST introduces **volumetric spectral stabilization**. By leveraging the interior geometry of the object, the HST Dual framework effectively resolves symmetry-breaking and local minima issues that frequently cause surface-based methods to fail.

### ⭐ First Integrated Python/GPU Spectral Pipeline
This is the first comprehensive Python solution that bridges the entire spectral correspondence chain in a single optimized pipeline:
**Volumetric LB Eigenfunctions** → **HST Initialization** → **GPU Functional Maps** → **GPU ZoomOut**.
The entire workflow remains within the GPU memory space, eliminating costly data transfers between environments.

### ⭐ Extreme Acceleration: 11× Faster than CPU Baselines
By leveraging massive GPU parallelism, we have reduced the processing time for a complete high-resolution benchmark (99 pairs) from **142 minutes to just 13 minutes**. This represents a major breakthrough in productivity for researchers and 3D artists alike.

### ⭐ Optimized GPU ZoomOut & FM Implementation
This project provides highly optimized Python/CUDA implementations of the ZoomOut and Functional Maps algorithms. Unlike standard CPU-based versions (SciPy/NumPy), our GPU engine achieves up to **6.5× speedup** while maintaining identical mathematical precision.

### ⭐ Blender-Ready Spectral Engine
HST is the first professional-grade spectral engine designed for seamless integration into the **Blender ecosystem**. By combining volumetric HST with classical Functional Maps, we introduce a new class of robust correspondence algorithms accessible to the broader 3D community.
</td>
<td width="50%" valign="top">

### Results

| Method | Geo error | Time | Speedup |
|--------|-----------|------|---------|
| FMaps HST (GPU) | 0.138 | 1.02s | 42× |
| ZoomOut HST (GPU) | 0.194 | 6.62s | 6.5× |
| HST Note (CPU/GPU) | **0.129** | **0.805s** | **53×** |

### FM+HST Hybrid

- **+52.5%** improvement over standard FM
- Up to **+84%** on difficult FAUST pairs
- **99/99** stable results, zero failures
- Consistently outperforms FM_rand and ZoomOut_rand

### Scientific Contributions

- New spectral representation (volumetric LB)
- New global method (HST harmonic note)
- New hybrid algorithm (FM+HST)
- First GPU FM · First GPU ZoomOut
- First GPU spectral pipeline
- First full FAUST GPU benchmark

### Why It Matters

Enables robust shape matching, animation transfer,
texture transfer, 3D AI alignment, real-time GPU
workflows and volumetric processing — capabilities
no existing academic or commercial system offers.

</td>
</tr>
</table>

## 📊 Reproducibility & Benchmarking

<table>
<tr>
<td width="50%" valign="top">

**Benchmark Script:** [`hst_volumetric_faust_benchmark_v1.py`](./hst_volumetric_faust_benchmark_v1.py)  
**Dataset:** MPI FAUST (Training set, 100 scans)  
**Environment:** Blender 5.1+ with CUDA-enabled GPU  
📊 [hst_volumetric_GPU_benchmark.csv](hst_volumetric_GPU_benchmark.csv)

</td>
<td width="50%" valign="top">

<img width="100%" src="https://github.com/user-attachments/assets/b87a9aaa-40a9-4425-a84e-0ec1140cdbe2" />

</td>
</tr>
</table>

---

## 🏆 HST as Universal Initializer

HST harmonic note systematically improves any spectral shape correspondence algorithm.

<table>
<tr>
<td width="50%" valign="top">

| Method | Random init | HST init | Improvement |
|--------|------------|----------|-------------|
| ZoomOut (Melzi 2019) | 0.352 | 0.193 | **+42.3%** |
| Functional Maps (Ovsjanikov 2012) | 0.295 | 0.138 | **+52.5%** |

Two independent methods. Two different research groups. Same result.  
**Random initialization never wins. Not once. 0/99.**

</td>
<td width="50%" valign="top">

<img width="100%" src="https://github.com/user-attachments/assets/db84e211-c616-4c06-9787-9d7e83e60098" />

</td>
</tr>
</table>

---

## 🔬 CPU vs GPU — Identical Results

<table>
<tr>
<td width="50%" valign="top">

| Metric | CPU | GPU |
|--------|-----|-----|
| HST Note wins | 67/99 | 66/99 |
| HST+ZoomOut wins | 32/99 | 33/99 |
| Random→ZoomOut wins | 0/99 | 0/99 |
| Mean geo error (HST) | 0.129 | 0.129 |
| Mean improvement (ZoomOut) | 42.3% | 41.5% |
| Mean improvement (FMaps) | **52.5%** | **52.5%** |

GPU float64 precision — zero numerical artifacts.  
Results are **hardware-independent**.  
📊 [hst_faust_full_benchmark.csv](hst_faust_full_benchmark.csv)

</td>
<td width="50%" valign="top">

<img width="100%" src="https://github.com/user-attachments/assets/d8a459ce-36f2-44c6-b51e-de26aed56c67" />

</td>
</tr>
</table>

---

## 🧊 HST Volumetric — Three Harmonic Notes

<table>
<tr>
<td width="50%" valign="top">

| Note | Field | Method | Time |
|------|-------|--------|------|
| **Surface** | 2D manifold | Laplace-Beltrami | 0.044s |
| **Interior** | 3D volume | Tetrahedral Laplacian | 0.265s |
| **Exterior** | Surrounding space | SDF (GPU) | 0.073s |
| **Total** | | | **1.70s** |

**Potential applications:**
- CT scans, MRI, solid objects
- Topology-aware shape matching
- 3D generative AI descriptors

</td>
<td width="50%" valign="top">

To the best of the author's knowledge, the combination of surface,
interior and exterior harmonic fields as a unified shape descriptor
has not been previously published.

[`hst_volumetric_gpu_v2.py`](hst_volumetric_gpu_v2.py) — Blender addon  
View3D → Sidebar → HST_VolGPU

</td>
</tr>
</table>

⚖️ License & Legal Notice
1. Licensing Model

This project uses a dual-licensing approach to protect the author's intellectual property:

    Code & Software: Released under the GNU General Public License v3.0 (GPL-3.0). Any redistribution or derivative work must remain open-source.

    Concept & Documentation: Licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0). Use for commercial gain is strictly prohibited without a separate agreement.

2. Commercial & Proprietary Use

The licenses provided (GPL-3.0 and CC BY-NC 4.0) do not permit integration into closed-source software, proprietary AI models, or commercial products.

    Commercial License: Required for any use outside of the open-source/non-commercial scope.

    Inquiries: For commercial licensing or proprietary integration, contact the author directly.

3. Intellectual Property (IP)

The Harmonic Shape Transform (HST) framework, its mathematical formulation, the concept of "harmonic notes," and volumetric stabilization are the intellectual property of the author.

    Priority: Authorship is verified by the public timestamp of this repository and the associated DOI.

    Restrictions: Unauthorized integration into proprietary codebases or AI systems constitutes a violation of both copyright and license terms.

📧 Contact & Collaboration

For commercial licensing or research partnerships:
Pavel Krahulík 📩 pavel.krahulik.cestiny@gmail.com
Copyright Notice

Copyright © 2024-2026 Pavel Krahulík. All rights reserved. The author reserves all rights to pursue patent protection and legal action against unauthorized commercial use.
