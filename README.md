# Harmonic Shape Transform (HST)
### A New Concept for Shape Transformation Using Harmonic Notes

This repository contains the first public description of the **Harmonic Shape Transform (HST)** — a new mathematical concept for transforming shapes using the internal harmonic structure of a domain. The idea is based on the observation that every shape has its own *harmonic note*, defined as a normalized eigenfunction of the Laplace operator. This harmonic note can serve as a universal intermediate representation between shapes.

**Author:** Pavel Krahulik 
**Year:** 2026

---

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

Unauthorized integration of the HST concept into proprietary codebases, AI systems, or commercial pipelines constitutes a violation of copyright and license terms.¨

python hst_example.py
This includes both direct use and derivative implementations based on the definitions provided in this repository.
5. Proof of Authorship

The public timestamp of this repository, together with the included PDF documentation, serves as verifiable evidence of authorship and priority of the HST concept.
6. Contact

For commercial licensing, research collaboration, or inquiries regarding permitted use, please contact the author directly.

Commercial licensing available upon request.
Contact the author for closed‑source or commercial use.
