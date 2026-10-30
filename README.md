<div align="center">
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Jack6228/Hades/main/docs/assets/HadesLogo_Dark_Text_Transparent.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Jack6228/Hades/main/docs/assets/HadesLogo_Light_Text_Transparent.png">
    <img alt="Hades Logo" src="https://raw.githubusercontent.com/Jack6228/Hades/main/docs/assets/HadesLogo_Light_Text_Transparent.png" width="300">
</picture>
<br>
  <sup style="font-family: monospace; font-weight: bold; letter-spacing: 2px; font-size: 24px;">[BETA]</sup>
<br>
<br>
<br>
</div>

<div align="center">

**Petrological Modelling for Fractional Crystallisation**

A Windows application and Python package for modelling and optimising (assimilation) fractional crystallisation of magmatic data suites, finding the optimal mineral assemblage and conditions to explain an observed liquid line of descent.

<!-- [![Paper](https://img.shields.io/badge/Paper-XXX-blue)]() -->
[![PyPI](https://img.shields.io/badge/PyPI-hades--obol-FCB001?logo=pypi)](https://pypi.org/project/hades-obol/)
[![Docs](https://img.shields.io/badge/ReadTheDocs-latest-00897B?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://img.shields.io/github/actions/workflow/status/Jack6228/Hades/ci.yml?branch=main)](https://github.com/Jack6228/Hades/actions/workflows/ci.yml?query=branch%3Amain)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](http://opensource.org/licenses/BSD-3-Clause)

</div>

# Hades

Hades is a piece of software which models the evolution of magmatic data suites under fractional crystallisation, finding the optimal mineral assemblage and conditions to explain an observed liquid line of descent.

The software is primarily available as a standalone Windows application, but also as a Python package for scripting and interactive use in Jupyter notebooks on any platform.

Hades is designed to be easy-to-use, with no prior programming knowledge, yet enables users to perform advanced modelling: customising a range of parameters (K<sub>D</sub> values, mineral compositions, etc.) as well as perform trace element modelling and visualisation of results.

<br>
<div align="center">
    <picture>
        <img src="https://raw.githubusercontent.com/Jack6228/Hades/main/docs/assets/HadesHomepage.png" alt="The Hades Interface" width="600" style="border-radius: 2px;">
    </picture>
</div>

## Key Features

- **Simple Input Format**: Use CSV, Excel or similar format files to structure your major element data and let Hades handle the rest. 

- **Customisable**: Tailor Hades based on what you already know. For example, add mineral data if you have analysed it and choose which minerals Hades should consider in the crystallising assemblages if you have the petrography. 

- **Visualisation**: Hades presents the uploaded data suite alongside the calculated liquid line of descent in a range of customisable bivariate plots for quick visualisation. The TAS diagram and bivariate plots showing the mineral data is also available. Hades combines the outputs into a downloadable pdf for future reference.  

- **Accessible for non-programmers**: Hades intuitive and simple interface is designed to be user-friendly and enable Geoscientists to model he evolution of magmatic systems. It is available as a standalone application or a Python module for complete automation and workflow integration. 

- **Range**: Hades can model fractional crystallisation and assimilation fractional crystallisation of subalkaline or alkaline data suites. It can model for hydrous phases and does not require thermodynamic, intrinsic (H<sub>2</sub>O) or extrinsic (P–T) conditions.  

## Installation

### Windows Application 

Download the latest installer from [Releases](https://github.com/Jack6228/Hades/releases), run the ``.exe`` file and follow the instructions.

Once installed, find a quickstart, how-to guides, and a user manual in the [documentation](https://hades-obol.readthedocs.io/en/latest/?badge=latest).

[![Docs](https://img.shields.io/badge/Docs-Windows_Installation-3776AB?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/overview/installation.html)
[![Release](https://img.shields.io/badge/Latest_Release-v0.9.1-00897B?logo=github)](https://github.com/Jack6228/Hades/releases/tag/v0.9.1)

### Python Package

```bash
pip install hades-obol
```

Find the Python quickstart, API and example usage in the [documentation](https://hades-obol.readthedocs.io/en/latest/?badge=latest) or download the example notebooks for [numerous case studies](https://hades-obol.readthedocs.io/en/latest/case_studies.html).

Alternatively, see Hades in action and run the Ontong Java Plateau case study in a [Google Colab Notebook](https://colab.research.google.com/github/Jack6228/hades/blob/main/examples/indonesia/ontong_java_plateau.ipynb), or access all other case studies below:

[![Colab](https://img.shields.io/badge/Colab-Notebooks-F9AB00?logo=googlecolab)](https://colab.research.google.com/github/Jack6228/hades/blob/main/examples/indonesia/ontong_java_plateau.ipynb)
[![Docs](https://img.shields.io/badge/Docs-Python_Installation-3776AB?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/api/python_installation.html)
[![Docs](https://img.shields.io/badge/Docs-Case_Studies-00897B?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies.html)

## Documentation

Full documentation is available on ReadTheDocs with installation instructions, quickstarts, case studies, a user guide for the software, and API reference for the Python package.

[![Docs](https://img.shields.io/badge/Docs-ReadTheDocs-00897B?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/?badge=latest)

## Examples

This repository contains example notebooks for numerous case studies, with input data suites, Python notebooks, ``.hades`` configuration files, and output plots and exported data. Each case study is also presented in the documentation with data and guides for use in both Python and the Windows application.

We provide a range of case studies to showcase the breadth of Hades' capabilities as well as a range of petrological scenarios:

<div align="center">

  [![Docs](https://img.shields.io/badge/-Synthetics-FFD54F?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/synthetics/index.html)
  [![Docs](https://img.shields.io/badge/-Ontong_Java_Plateau-FFB300?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/indonesia/index.html)
  [![Docs](https://img.shields.io/badge/-Þingmúli,_Iceland-F4511E?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/iceland/index.html)
  [![Docs](https://img.shields.io/badge/-Adamello_Batholith-C62828?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/italy/index.html)
  [![Docs](https://img.shields.io/badge/-Santa_María,_Guatemala-7F0000?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/guatemala/index.html)
  <br>
  [![Docs](https://img.shields.io/badge/-Carlingford,_Ireland-FF8F00?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/ireland/index.html)
  [![Docs](https://img.shields.io/badge/-Madeira_Archipelago-E53935?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/madeira_archipelago/index.html)
  [![Docs](https://img.shields.io/badge/-São_Tomé-B71C1C?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/sao_tome/index.html)
  [![Docs](https://img.shields.io/badge/-Jbel_Saghro,_Morocco-3D0000?logo=readthedocs)](https://hades-obol.readthedocs.io/en/latest/case_studies/morocco/index.html)

</div>

## Citing & License

If you use Hades in research, please use the following citation until a paper is published:

```
@software{hades,
  author       = {Smith, J. L. and Hastie, A. R. and 
                  Young, L. A. and Nash, I. J. and 
                  Law, S. and Fitton, J. G.},
  title        = {Hades: a new differential evolution 
                  mass balance program to model fractional 
                  crystallisation and assimilation in 
                  igneous rocks},
  month        = oct,
  year         = {2026},
  publisher    = {Zenodo},
  version      = {v0.9.1},
  doi          = {https://zenodo.org/record/23808870},
  url          = {https://doi.org/10.5281/zenodo.23808869},
}
```

Hades is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.