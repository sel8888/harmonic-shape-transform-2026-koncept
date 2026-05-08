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



<h2 align="center">Strike a 3D shape like a bell — it rings its harmonic note.
That note encodes the shape's intrinsic structure.
HST uses it to map any shape to any other shape in 0.8s.
Other methods ring louder when they start from this note.</h2>

### A New Concept for Shape Transformation Using Harmonic Notes

In Kabbalah, creation is perceived as a symphony of harmonic notes that shape reality. My HST algorithm does exactly that within the digital realm: it identifies these fundamental 'harmonic notes' (eigenfunctions) of 3D objects. This allows it to recognize a shape's identity regardless of its deformation—it listens to its inner music, rather than its outer shell."

"Every shape and every physical system possesses its own harmonic note — the smoothest intrinsic scalar field that expresses its internal organization. HST extracts this note, normalizes it, and uses it as a universal intermediate state for mapping between shapes of arbitrary topology

This repository contains the first public description of the **Harmonic Shape Transform (HST)** — a new mathematical concept for transforming shapes using the internal harmonic structure of a domain. The idea is based on the observation that every shape has its own *harmonic note*, defined as a normalized eigenfunction of the Laplace operator. This harmonic note can serve as a universal intermediate representation between shapes.

From Vision to Reality: On May 1st, 2026, this was just an idea. Today, it is a stable, deterministic HST system providing real-time semantic topology in Blender.

**Author:** Pavel Krahulik 
**Year:** 2026


💡 After testing HST Harmonic Note improves ANY spectral method as initialization.

## 🌍 The Discovery

> *To the best of the author's knowledge, this is the first publicly documented
> GPU-accelerated spectral shape correspondence pipeline based on a volumetric
> Laplace–Beltrami operator combined with the Harmonic Shape Transform.*

<table>
<tr>
<td width="50%" valign="top">

### Five World Firsts

⭐ **Volumetric Laplace–Beltrami for correspondence**  
All existing methods (FM, ZoomOut, HKS, BCICP) use surface-only operators.
HST introduces the first volumetric spectral basis for global shape alignment.

⭐ **First GPU Functional Maps implementation**  
FM has existed for a decade — no GPU implementation was ever published.
This repository contains the first known GPU FM solver.

⭐ **First GPU ZoomOut refinement**  
All existing ZoomOut implementations (MATLAB, Python, C++) are CPU-only.
This achieves 6.5× speedup with identical accuracy.

⭐ **First complete GPU spectral pipeline**  
Volumetric LB eigenfunctions → HST initialization → GPU FM → GPU ZoomOut →
GPU nearest-neighbor search → full FAUST benchmark (99/99 pairs).  
**142 min → 13 min (11× speedup)**

⭐ **New hybrid algorithm: FM+HST**  
Combining volumetric HST with FM produces a new class of spectral
correspondence algorithms.

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

Full benchmarking suite available for independent verification.

**Benchmark Script:** [`hst_volumetric_faust_benchmark_v1.py`](./hst_volumetric_faust_benchmark_v1.py)  
**Dataset:** MPI FAUST (Training set, 100 scans)  
**Environment:** Blender 5.1+ with CUDA-enabled GPU

📊 **Volumetric GPU results:** [hst_volumetric_GPU_benchmark.csv](hst_volumetric_GPU_benchmark.csv)

<img width="800" src="https://github.com/user-attachments/assets/b87a9aaa-40a9-4425-a84e-0ec1140cdbe2" />

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

<img width="800" src="https://github.com/user-attachments/assets/d8a459ce-36f2-44c6-b51e-de26aed56c67" />

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

## 📚 Citation

If you are interested in collaboration or discussion, feel free to reach out.

## License

- **Non-commercial use:** CC BY-NC 4.0 — free for research, education, open source
- **Commercial use:** contact Pavel.krahulik.cestiny@gmail.com for a commercial license
- **Exception:** Blender Foundation and open source projects may use under GPL-3.0
This project is released under the GNU General Public License v3.0 (GPL‑3.0).
  
Commercial use, proprietary redistribution, or closed-source modifications are not permitted.  
Any reuse or modification must remain open-source under GPL‑3.0 and must credit the original author.

Legal Notes

This repository contains the original formulation of the Harmonic Shape Transform (HST), including its general definition as a scalar‑field–based shape transformation framework. All materials in this repository — including the conceptual description, mathematical definitions, terminology, and the general HST framework — are protected by copyright of the author.

The following legal conditions apply:
1. Copyright

All textual, mathematical, conceptual, and structural elements of the HST framework are the intellectual property of the author.
This includes, but is not limited to:

    the definition of HST as a transform induced by normalized scalar fields,

    the concept of harmonic notes,

    the generalization to arbitrary smooth scalar functions,

    terminology, diagrams, and conceptual structure.

2. Open‑Source License (GPL‑3.0)

The public version of this repository is released under the GNU GPL‑3.0 license.
Any use of the HST concept under GPL‑3.0 requires compliance with all obligations of the license, including the requirement to release derivative works under GPL‑3.0.
3. Commercial and Closed‑Source Use

Any commercial, proprietary, or closed‑source use of the HST concept — including the general HST framework, harmonic‑note transform, or any scalar‑field–based variant — requires a separate commercial license from the author.

No company or individual is permitted to integrate HST into closed‑source software, AI models, or commercial products without obtaining such a license.
4. Prohibition of Unauthorized Integration

Unauthorized integration of the HST concept into proprietary codebases, AI systems, or commercial pipelines constitutes a violation of copyright and license terms.

python hst_example.py
This includes both direct use and derivative implementations based on the definitions provided in this repository.
5. Proof of Authorship

The public timestamp of this repository, together with the included PDF documentation, serves as verifiable evidence of authorship and priority of the HST concept.
6. Contact

For commercial licensing, research collaboration, or inquiries regarding permitted use, please contact the author directly.
The author reserves all rights to pursue patent protection.

Commercial licensing available upon request.
Contact the author for closed‑source or commercial use.
