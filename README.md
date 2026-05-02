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

- **harmonic-shape-transform-2026-koncept.pdf**

This document establishes the idea, definitions, and potential applications.

---

## 📚 Citation

If you are interested in collaboration or discussion, feel free to reach out.

GPL‑3.0

## License
This project is released under the GNU General Public License v3.0 (GPL‑3.0).  
Commercial use, proprietary redistribution, or closed-source modifications are not permitted.  
Any reuse or modification must remain open-source under GPL‑3.0 and must credit the original author.

Commercial licensing available upon request.
Contact the author for closed‑source or commercial use.
