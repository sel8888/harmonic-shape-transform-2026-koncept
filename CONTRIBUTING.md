# Contributing to HST (Harmonic Shape Transform)

First off, thank you for considering contributing to HST! It's community members like you that make this tool better for everyone. Whether you are a developer, a technical artist, or a researcher, your input is highly valued.

## 🚀 How Can You Help?

### 1. Reporting Bugs
¨# Contributing to HST (Harmonic Shape Transform)

First off, thank you for considering contributing to HST! It's community members like you that make this tool better for everyone. By contributing to this project, you help us advance semantic geometry within the open-source ecosystem.

## 🚀 How Can You Help?

### 1. Reporting Bugs
If you find a bug, please open an **Issue**. To help us fix it faster, please include:
* Your Blender version.
* Your Operating System.
* A clear description of the steps to reproduce the error.
* (Optional) A screenshot of the System Console or a sample `.blend` file.

### 2. Feature Requests
Have an idea for a new feature? We’d love to hear it! Open an issue and label it as `enhancement`. We are particularly interested in:
* Denoising pipelines and AI-assisted rendering.
* Semantic rigging and skinning stability.
* Real-time mesh correspondence for VFX.

### 3. Code Contributions
We welcome Pull Requests for optimizations and new features.
* **Optimization:** Improvements to Laplacian computation or Eigen-decomposition (NumPy/SciPy).
* **Integration:** Enhanced bridges to Cycles, Eevee, or Geometry Nodes.

## 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sel8888/harmonic-shape-transform-2026-koncept.git](https://github.com/sel8888/harmonic-shape-transform-2026-koncept.git)
2  Dependencies: Ensure you have numpy and scipy installed within your Blender's Python environment.

3  Workflow: The main logic is contained within the HST_OT_Compute operator, while the UI is handled by HST_PT_Panel.

📮 Pull Request Guidelines

   1 Create a new branch for your feature: git checkout -b feature/cool-new-stuff.

   2 Keep your code clean and follow PEP8 standards where possible.

   3 Test your changes on basic meshes (Suzanne, Cube) as well as complex datasets (e.g., FAUST).

   4 Submit the PR with a clear description of what you’ve changed and why.

⚖️ License and Protections

By contributing to this repository, you agree to the following:

    License: Your contributions will be licensed under the GNU General Public License v3 (GPLv3). This ensures the project remains free and open-source forever.

    Originality: You certify that the code you submit is your original work or that you have the right to submit it under the GPLv3 license.

    Rights: All existing protections and trademarks associated with the HST Semantic Engine remain the property of the project maintainers.

Thank you for respecting the open-source spirit and helping HST grow!

Thank you for being part of the HST journey!
