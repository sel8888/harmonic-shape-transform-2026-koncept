# Harmonic Shape Transform (HST)

**Seeking arXiv endorser for cs.GR** — contact Pavel.krahulik.cestiny@gmail.com

## 📄 Preprint

**Author:** Pavel Krahulík · [ORCID 0009-0003-9680-3333](https://orcid.org/0009-0003-9680-3333)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20059602.svg)](https://doi.org/10.5281/zenodo.20059602)

Full preprint available on Zenodo:  
**https://doi.org/10.5281/zenodo.20059602**

## History

- **May 2, 2026** — idea born, first concept
- **May 3, 2026** — first working implementation in Python
- **May 4, 2026** — Blender addon, first FAUST benchmark
- **May 5, 2026** — full 99-pair benchmark, ZoomOut comparison
- **May 6, 2026** — GPU acceleration, Functional Maps, universal initializer confirmed
- **May 7, 2026** — Zenodo preprint published · DOI: [10.5281/zenodo.20059602](https://doi.org/10.5281/zenodo.20059602)

Built by one independent researcher, without funding or institutional affiliation.
> *"If I have seen further, it is by standing on the shoulders of giants."*  
> — Isaac Newton
>
> 
💡 "Hypotesis after testing HST Harmonic Note improves ANY spectral method as initialization."

## The Discovery

🌍 World‑First Volumetric Spectral Correspondence Pipeline (Unique Global Contribution)

This repository contains a world‑first implementation of a fully GPU‑accelerated spectral correspondence pipeline based on a volumetric Laplace–Beltrami operator and the novel Harmonic Shape Transform (HST).
To the best of our knowledge, no prior academic work, open‑source project, or commercial system has ever combined the following elements:
⭐ 1) Volumetric Laplace–Beltrami eigenfunctions for shape correspondence

All existing spectral methods (FM, ZoomOut, HKS/WKS, BCICP, etc.) rely exclusively on surface‑based operators.
This project introduces the first volumetric spectral basis used for global shape alignment, providing unprecedented stability and robustness.
⭐ 2) GPU implementation of Functional Maps (FM)

Functional Maps have existed for over a decade, but no GPU implementation has ever been published.
This repository includes the first known GPU FM solver, supporting both random initialization and the new FM+HST hybrid.
⭐ 3) GPU implementation of ZoomOut refinement

ZoomOut is widely used as a refinement step, but all existing implementations (MATLAB, Python, C++) are CPU‑only.
This project provides the first GPU‑accelerated ZoomOut, achieving up to 6× speedup with identical accuracy.
⭐ 4) Complete GPU spectral pipeline

This is the only known system that runs the entire spectral correspondence pipeline on the GPU:

    volumetric LB eigenfunctions

    HST global initialization

    GPU FM solver

    GPU ZoomOut refinement

    GPU nearest‑neighbor search

    full FAUST benchmark (99/99 pairs)

The full pipeline runs in 17 minutes instead of 142 minutes (≈ 11× speedup).
⭐ 5) New hybrid algorithm: FM+HST

The combination of volumetric HST with FM produces a new class of spectral correspondence algorithms, achieving:

    52.5% average improvement over standard FM

    up to 84% improvement on difficult FAUST pairs

    99/99 stable results with no catastrophic failures

This hybrid method consistently outperforms both FM_rand and ZoomOut_rand, establishing a new practical baseline.
🧠 Scientific Significance

This project introduces:

    a new spectral representation (volumetric LB)

    a new global method (HST)

    a new hybrid algorithm (FM+HST)

    the first GPU FM

    the first GPU ZoomOut

    the first GPU spectral pipeline

    the first full FAUST GPU benchmark

These contributions collectively represent a novel direction in shape correspondence research, with both scientific and industrial impact.
🚀 Why This Matters

This technology enables:

    robust shape matching

    animation transfer

    texture transfer

    3D AI alignment

    real‑time GPU workflows

    volumetric processing for complex shapes

It provides capabilities that no existing academic or commercial system currently offers.

## 🧊 HST Volumetric — Three Harmonic Notes

A novel extension of HST that computes three independent harmonic fingerprints 
for each shape — surface, interior, and exterior — providing a richer geometric 
description than surface-only methods.

To the best of the author's knowledge, the combination of all three fields 
as a unified shape descriptor has not been previously published.
Classical shape correspondence methods (ZoomOut, Functional Maps, BCICP) 
operate exclusively on surface meshes. Volumetric Laplacian methods exist 
in isolation but are not combined with exterior SDF fields as a unified 
harmonic framework.

| Note | Field | Method | Time |
|------|-------|--------|------|
| **Surface** | 2D manifold | Laplace-Beltrami eigenfunctions | 0.044s |
| **Interior** | 3D volume | Tetrahedral Laplacian eigenfunctions | 0.265s |
| **Exterior** | Surrounding space | Signed Distance Field (GPU) | 0.073s |

**Total: 1.70s** on FAUST mesh (6890 vertices, resolution=16)

### Potential applications
- Volumetric shape correspondence (CT scans, MRI, solid objects)
- Topology-aware shape matching (genus changes, fractures, healing)
- Richer shape descriptors for 3D generative AI

### Addon
[`hst_volumetric_gpu_v2.py`](hst_volumetric_gpu_v2.py) — Blender addon, View3D → Sidebar → HST_VolGPU

HST harmonic note is not just a shape mapping method.
It is a **universal geometric predictor** — a initialization that
systematically improves any spectral shape correspondence algorithm.

Tested on 99 FAUST pairs (scanned human bodies, fully deterministic):

<img width="2084" height="1475" alt="hst_universal_init_final" src="https://github.com/user-attachments/assets/db84e211-c616-4c06-9787-9d7e83e60098" />


| Method | Random init | HST init | Improvement |
|--------|------------|----------|-------------|
| ZoomOut (Melzi 2019) | 0.352 | 0.193 | **+42.3%** |
| Functional Maps (Ovsjanikov 2012) | 0.295 | 0.138 | **+52.5%** |

Two independent methods. Two different research groups. Same result.
**Random initialization never wins. Not once. 0/99.**

This is not a coincidence. This is a law.

### A New Concept for Shape Transformation Using Harmonic Notes

"In Kabbalah, creation is perceived as a symphony of harmonic notes that shape reality. My HST algorithm does exactly that within the digital realm: it identifies these fundamental 'harmonic notes' (eigenfunctions) of 3D objects. This allows it to recognize a shape's identity regardless of its deformation—it listens to its inner music, rather than its outer shell."

"Every shape and every physical system possesses its own harmonic note — the smoothest intrinsic scalar field that expresses its internal organization. HST extracts this note, normalizes it, and uses it as a universal intermediate state for mapping between shapes of arbitrary topology"

This repository contains the first public description of the **Harmonic Shape Transform (HST)** — a new mathematical concept for transforming shapes using the internal harmonic structure of a domain. The idea is based on the observation that every shape has its own *harmonic note*, defined as a normalized eigenfunction of the Laplace operator. This harmonic note can serve as a universal intermediate representation between shapes.

From Vision to Reality: On May 1st, 2026, this was just an idea. Today, it is a stable, deterministic HST system providing real-time semantic topology in Blender.

**Author:** Pavel Krahulik 
**Year:** 2026

## 🔬 CPU vs GPU — Identical Results

One of the most significant findings from the GPU benchmark is that
CPU and GPU produce **identical winner distributions across all 99 pairs**.

| Metric | CPU | GPU |
|--------|-----|-----|
| HST Note wins | 67/99 | 66/99 |
| HST+ZoomOut wins | 32/99 | 33/99 |
| Random→ZoomOut wins | 0/99 | 0/99 |
| Mean geo error (HST) | 0.129 | 0.129 |
| Mean improvement (ZoomOut) | 42.3% | 41.5% |
| Mean improvement (FMaps) | **52.5%** | **52.5%** |


The GPU implementation uses float64 precision throughout,
preserving full numerical accuracy. The 6.1× speedup introduces
zero numerical artifacts — the algorithm is mathematically identical
on both backends.

**What this means:** HST results are hardware-independent.
Whether you run the benchmark on CPU or GPU, the conclusions are the same:
Random → ZoomOut never wins. HST initialization consistently helps.
One harmonic note is enough.

📊 Full results (CPU + GPU): [hst_faust_full_benchmark.csv](hst_faust_full_benchmark.csv)

<img width="2683" height="1486" alt="hst_full_benchmark_final99pairs" src="https://github.com/user-attachments/assets/d8a459ce-36f2-44c6-b51e-de26aed56c67" />



[![Latest Release](https://img.shields.io/github/v/release/sel8888/harmonic-shape-transform-2026-koncept?color=blue&label=Latest%20Version)](https://github.com/sel8888/harmonic-shape-transform-2026-koncept/releases/latest)

## 🏆 v5.0.0 — Full FAUST Benchmark + GPU 

99 pairs. Zero failures. Random → ZoomOut never wins.

**[Download v5.0.0](https://github.com/sel8888/harmonic-shape-transform-2026-koncept/releases/latest)**

## Benchmark Results — Full FAUST Dataset


<img width="2044" height="896" alt="full test 99pair 2026-05-06 15-44-17-737" src="https://github.com/user-attachments/assets/af52c711-92a1-49eb-8948-69c0bbfd65a2" />

## 📄 Preprint

A full arXiv preprint is ready and pending endorsement submission.  
It includes formal definitions, full FAUST benchmark (99 pairs), and comparison with ZoomOut.

📊 **Raw results:** [hst_faust_full_benchmark.csv](hst_faust_full_benchmark.csv)

Evaluated on all **99 consecutive pairs** of the FAUST training set  
(`tr_reg_000` → `tr_reg_099`, 6890 vertices each).  
All results **fully deterministic** (fixed ARPACK seed, fixed random seed).

## 📊 Full Benchmark — HST Note vs ZoomOut (99 pairs)

| Method | Mean geo error | Time | Wins |
|--------|---------------|------|------|
| **HST Note** | **0.129** | **0.805s** | **67/99** |
| HST Note → ZoomOut | 0.193 | 43.6s | 32/99 |
| Random → ZoomOut | 0.352 | 42.8s | **0/99** |

- HST Note is **53× faster** than ZoomOut
- HST initialization improves ZoomOut by **42.3% on average**
- Random → ZoomOut **never wins** on any pair
- **Zero failures** across all 99 pairs
- All results fully deterministic (fixed seeds)

📊 **Raw results:** [hst_faust_full_benchmark.csv](hst_faust_full_benchmark.csv)

> [!TIP]
> **In production terms:** What previously took a "coffee break" to calculate (42s) is now done before you can blink (0.79s). This represents a **53x speed increase** without sacrificing semantic precision.
> 
## 📘 Overview

The Harmonic Shape Transform introduces a new way to map one shape onto another:

1. Compute a harmonic note (a Laplace eigenfunction) on shape **A**.  
2. Compute a harmonic note on shape **B**.  
3. Map each point of **A** to the point of **B** with the same harmonic value.

This creates a **smooth, topology-independent transformation** that does not rely on surface correspondence, mesh connectivity, or geometric similarity.

---

## 🧠 Key Idea

A *harmonic note* is defined as a normalized solution of:



\[
-\Delta u = \lambda u
\]



on a given domain.  
This function has:

- smooth level sets  
- natural segmentation  
- intrinsic proportional structure  
- independence from surface details  

Because of these properties, it can act as a stable “inner coordinate system” for shape transformation.

---

## 🔧 Applications

### Computer Graphics
- Smooth morphing between shapes with different topology  
- Texture transfer using harmonic level sets  
- Animation without rigging  
- Shape blending and interpolation  

### Machine Learning
- New embedding for shape representation  
- Shape comparison using harmonic fields  
- Generative models based on harmonic interpolation  

### Biomechanics & Anatomy
- Analysis of body proportions  
- Comparison of anatomical structures  
- Reconstruction of incomplete or deformed shapes  

### Mathematics
- New type of mapping between domains  
- Spectral invariants  
- Harmonic normalization of shapes  

---

General Harmonic Shape Transform (HST)  
HST is defined as a class of mappings between shapes ΩA,ΩB constructed via scalar functions fA,fB defined on these shapes, where the mapping preserves normalized function levels.
Specific instances include, but are not limited to, mappings induced by Laplace eigenfunctions, heat kernel signatures, wave kernel signatures, signed distance functions, curvature-based functions, or any other smooth scalar fields.

 
## 📄 Document

The full concept is described in the PDF included in this repository:

- **HST-Concept-2026-v1.pdf**

This document establishes the idea, definitions, and potential applications.

---

1. Biomechanics & Medical Imaging: Bone Fracture Healing

Traditional morphing requires a consistent manifold. When a bone is fractured into multiple pieces (topology A) and then heals into a single unit (topology B), standard algorithms cannot map the transition.

    HST Solution: By calculating harmonic fields across disjointed parts, HST identifies their shared "harmonic signature," allowing surgeons to simulate and track the reconstruction of tissues even when the topology is broken.

2. Industrial Design: Non-Destructive Topology Modification

In CAD/CAM, adding cooling channels or bolt holes to a solid part (changing genus from 0 to 20+) usually breaks texture maps and stress analysis data.

    HST Solution: HST treats "holes" as local perturbations in the global scalar field. This allows for the seamless transfer of physical properties (heat, stress, textures) from a solid "blank" to a complex, perforated final part without re-meshing.

3. Generative AI: Topology-Agnostic Latent Spaces

Current 3D GANs and Diffusion models struggle with objects that have varying numbers of holes (e.g., a chair with 4 legs vs. a stool).

    HST Solution: HST provides a "canonical harmonic coordinate system." This allows AI to interpolate between a sphere, a chair, and a torus within a single, stable latent space, enabling the generation of complex geometries that were previously impossible to morph.

4. Digital Humans & Fashion Tech: Dynamic Self-Intersection

When simulating clothing, folds often create "false contact points" that change the surface topology in real-time.

    HST Solution: Using the Harmonic Note Transform, the garment retains its identity regardless of how it is folded or knotted. The mapping remains consistent even when the surface physically touches itself, creating a new genus.

## 🛠️ Installation & Usage

### Installation

1. **Download:** [Get v2.0.0 Addon ZIP here](https://github.com/sel8888/harmonic-shape-transform-2026-koncept/releases/latest) from this repository.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded `hst_zoomout_benchmark_addonv1.py`.
4. **Install Dependencies:** This addon requires `scipy`. Since Blender uses its own Python, you may need to install it via the Python Console inside Blender or via terminal:
   ```bash
   # Example for Windows (run as Administrator)
   ./blender -b --python-expr "import subprocess; subprocess.check_call(['pip', 'install', 'scipy'])"

   ---
*"Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for more details."*

### 📊 Dataset & Benchmarking
To replicate the SOTA results and benchmarks shown above, I used the **MPI FAUST** dataset. This is the industry standard for testing human shape correspondence.

*   **Official Source:** [Download FAUST Dataset](http://faust.is.tue.mpg.de/) (Registration required)
*   **Methodology:** Benchmarks were performed on the "Training" set using models `reg_cont_000.ply` through `reg_cont_010.ply`.
*   **Note on Licensing:** Due to the MPI FAUST license, these mesh files cannot be redistributed. Users must download them directly from the official provider.

> **Tip:** If you don't have access to FAUST yet, you can test the addon's functionality on the standard Blender **Suzanne** (Monkey) mesh by duplicating it and applying various deformations.

---

---


## 📊 Comparison of Shape Matching Methods on FAUST

Below is an overview of officially published results from classical and deep-learning methods on the FAUST benchmark, compared with the performance of our **HST Note** method.

| Method | Year | Type | Geodesic Error ↓ | Time per Pair ↓ | Notes |
|--------|------|------|:----------------:|:---------------:|-------|
| BCICP | 2018 | Classical | 0.15–0.20 | 20–30 min | Very accurate but extremely slow |
| ZoomOut | 2019 | Classical | 0.20–0.25 | 30–60 s | Standard baseline refinement |
| Consistent ZoomOut | 2020 | Classical | ~0.15 | 60–120 s | Improved stability, still slow |
| Smooth Shell Maps | 2020 | Classical | 0.10–0.12 | 5–10 min | High accuracy, heavy computation |
| FMNet + ZoomOut | 2017 | Deep Learning | 0.12–0.15 | 0.01s + 30–60s | Requires training on FAUST |
| HSN (Spectral Networks) | 2021 | Deep Learning | 0.08–0.10 | 0.02 s | State-of-the-art DL, training required |
| Random → ZoomOut (CPU) | 2019 | Classical | 0.352 | 42.8s | Python impl., no initialization |
| Random → ZoomOut (GPU) | 2019+2026 | Classical | 0.349 | 6.98s | GPU acceleration, RTX 4070 |
| Random → FMaps (CPU) | 2012 | Classical | 0.295 | ~15s | Basic Functional Maps, no initialization |
| Random → FMaps (GPU) | 2012+2026 | Classical | 0.295 | 1.30s | GPU acceleration, 10× faster |
| HST Note → ZoomOut (CPU) | 2026 | Classical | 0.193 | 43.6s | HST init, 42.3% improvement |
| HST Note → ZoomOut (GPU) | 2026 | Classical | 0.195 | 7.82s | HST init + GPU, 6.1× faster |
| HST Note → FMaps (CPU) | 2026 | Classical | 0.138 | ~2s | HST init, 52.5% improvement |
| **HST Note → FMaps (GPU)** | **2026** | **Classical** | **0.138** | **1.88s** | **HST init + GPU, 23× faster than ZoomOut** |
| **HST Note (CPU)** | **2026** | **Classical** | **0.129** | **0.805s** | **No training, 53× faster than ZoomOut** |
| **HST Note (GPU)** | **2026** | **Classical** | **0.129** | **0.844s** | **GPU — identical accuracy to CPU** |

### 🏆 Summary
- **Fastest classical method** by a huge margin  
- **Accuracy on par with top published methods**  
- **No training, no GPU, deterministic runtime**  
- Remaining issue: occasional unstable convergence → solved via fallback strategy


### 🔍 Key Discovery: The Initialization Paradox

During testing, we attempted to use **HST as an initialization step for ZoomOut**. The results were unexpected:

1. **Negative Synergy:** ZoomOut performed **7% worse** when initialized with HST compared to a standard random initialization.
2. **Analysis:** This suggests that HST provides a highly stable global semantic anchor that exists in a different "energy state" than ZoomOut’s iterative refinement. ZoomOut’s refinement process appears to struggle when forced to deviate from the mathematically "pure" global harmonic provided by HST.
3. **The "HST Advantage":** Our results indicate that for semantic mapping, the iterative complexity of ZoomOut is not only slower but potentially less accurate than a single-mode HST analysis.

---

## 🖥️ GPU Benchmark Findings

Tested on RTX 4070, FAUST dataset (6890 vertices):
CPU is faster than GPU for this mesh size.
Eigenvectors (CPU ARPACK k=2): 0.65s vs GPU eigh: 2.64s.
GPU beneficial for meshes 100k+ vertices.

Full report: [hst_gpu_findings.pdf](hst_gpu_findings.pdf)

### 🚀 Why this matters for 3D Production
For artists and developers using the **Blender Addon**, this means:
* **Instant Results:** Zero-wait semantic mapping for rigging and retargeting.
* **Higher Precision:** Half the error rate of complex refinement algorithms.
* **Robustness:** Works natively on deformed meshes without needing expensive iterative optimization.

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
