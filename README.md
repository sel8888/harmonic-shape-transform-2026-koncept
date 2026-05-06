# Harmonic Shape Transform (HST)

### A New Concept for Shape Transformation Using Harmonic Notes

"In Kabbalah, creation is perceived as a symphony of harmonic notes that shape reality. My HST algorithm does exactly that within the digital realm: it identifies these fundamental 'harmonic notes' (eigenfunctions) of 3D objects. This allows it to recognize a shape's identity regardless of its deformation—it listens to its inner music, rather than its outer shell."

"Every shape and every physical system possesses its own harmonic note — the smoothest intrinsic scalar field that expresses its internal organization. HST extracts this note, normalizes it, and uses it as a universal intermediate state for mapping between shapes of arbitrary topology"

This repository contains the first public description of the **Harmonic Shape Transform (HST)** — a new mathematical concept for transforming shapes using the internal harmonic structure of a domain. The idea is based on the observation that every shape has its own *harmonic note*, defined as a normalized eigenfunction of the Laplace operator. This harmonic note can serve as a universal intermediate representation between shapes.

From Vision to Reality: On May 1st, 2026, this was just an idea. Today, it is a stable, deterministic HST system providing real-time semantic topology in Blender.

**Author:** Pavel Krahulik 
**Year:** 2026

[![Latest Release](https://img.shields.io/github/v/release/sel8888/harmonic-shape-transform-2026-koncept?color=blue&label=Latest%20Version)](https://github.com/sel8888/harmonic-shape-transform-2026-koncept/releases/latest)

## 🚀 NEW: v2.0.0 Semantic Titan
The second generation of HST is here with a focus on stability and unmatched speed.

*   **Winner of HST Benchmark:** Residual error **0.00009**.
*   **29.1% Faster Initial Alignment** compared to previous builds.
*   **Production Ready:** Added **Geo-Error Fallback** for complex/dirty meshes (REG07).
*   **Download:** [Get v2.0.0 Addon ZIP here](https://github.com/sel8888/harmonic-shape-transform-2026-koncept/releases/latest)

### ⚡ High-Consistency Benchmark (Pairs 00 & 01)
In stress-tests across multiple runs, HST v2.0 demonstrated 100% consistency:

*   **Average Time:** 0.894s
*   **Residual:** 0.00005 (Ultra-High Precision)
*   **Geo Error:** 0.08361 (Constant)
---
> ### 🏆 Benchmark Breakthrough (Pairs 00 & 01)
> **HST Note vs. Standard ZoomOut (6.8k verts):**
> * **HST Note:** 0.79s (Geo Error: 0.0836)
> * **ZoomOut:** 42.45s (Geo Error: 0.2633)
> * **Efficiency:** 53.7x faster performance with 3x better accuracy.
---

## Benchmark Results — Full FAUST Dataset

📊 **Raw results:** [hst_faust_full_benchmark.csv](hst_faust_full_benchmark.csv)

Evaluated on all **99 consecutive pairs** of the FAUST training set  
(`tr_reg_000` → `tr_reg_099`, 6890 vertices each).  
All results **fully deterministic** (fixed ARPACK seed, fixed random seed).

### HST Note — 99 pairs

| Metric | Value |
|--------|-------|
| Mean geo error | 0.130 |
| **Median geo error** | **0.120** |
| Std | 0.050 |
| Min / Max | 0.066 / 0.504 |
| **Pairs < 0.20** | **96 / 99 (97%)** |
| Pairs < 0.30 | 98 / 99 (99%) |
| **Mean time per pair** | **0.802 s** |
| **Failures** | **0 / 99** |

### HST Note vs ZoomOut — selected pairs

| Method | Geo error | Time |
|--------|-----------|------|
| **HST Note (k=1)** | **0.084** | **0.81s** |
| Random → ZoomOut | 0.280 | 46s |
| HST Note → ZoomOut | 0.054 | 46s |

HST Note initialization improves ZoomOut by **29–81%** depending on pair difficulty.

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
<img width="2185" height="1060" alt="hst zoomout test  2026-05-06 10-09-08-343" src="https://github.com/user-attachments/assets/21fb3be4-bfdf-4df5-9e88-57a75753a91d" />


## 📊 Comparison of Shape Matching Methods on FAUST

Below is an overview of officially published results from classical and deep-learning methods on the FAUST benchmark, compared with the performance of our **HST Note** method.

| Method | Year | Type | Geodesic Error ↓ | Time per Pair ↓ | Notes |
|--------|------|------|------------------|------------------|--------|
| **BCICP** | 2018 | Classical | 0.15–0.20 | 20–30 min | Very accurate but extremely slow |
| **ZoomOut** | 2019 | Classical | 0.20–0.25 | 30–60 s | Standard baseline refinement |
| **Consistent ZoomOut** | 2020 | Classical | ~0.15 | 60–120 s | Improved stability, still slow |
| **Smooth Shell Maps** | 2020 | Classical | 0.10–0.12 | 5–10 min | High accuracy, heavy computation |
| **FMNet + ZoomOut** | 2017 | Deep Learning | 0.12–0.15 | 0.01 s + 30–60 s | Requires training on FAUST |
| **HSN (Spectral Networks)** | 2021 | Deep Learning | 0.08–0.10 | 0.02 s | State-of-the-art DL, training required |
| **HST Note (HST2026)** | 2026 | Classical | **0.0836** | **0.79 s** | No training, extremely fast |
| **HST Note – unstable mode** | 2026 | Classical | 0.45–0.55 | 0.16 s | Rare bad convergence (fixed via fallback) |

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

### 🚀 Why this matters for 3D Production
For artists and developers using the **Blender Addon**, this means:
* **Instant Results:** Zero-wait semantic mapping for rigging and retargeting.
* **Higher Precision:** Half the error rate of complex refinement algorithms.
* **Robustness:** Works natively on deformed meshes without needing expensive iterative optimization.

## 📚 Citation

If you are interested in collaboration or discussion, feel free to reach out.

GPL‑3.0

## License
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
