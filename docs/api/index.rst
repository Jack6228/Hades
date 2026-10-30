.. _PythonAPIReference:

.. title:: API Reference

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">API Reference</span>
         </h1>

      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>v0.9.0</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

API Reference
======================

Welcome to the API reference for the `hades-obol` package - the backend behind Hades. This section documents 
how the main functions which are used to model using the Python version of Hades are structured and how they can be used. 

We also provide API references for a range of visualisation functions available in the `hades-obol` package, which are used to generate plots and visualisations of the results of Hades models, e.g., TAS diagrams, bivariate plots, and Harker diagrams.

The API reference is intended for developers and advanced users who want to understand the inner workings of Hades or extend its functionality. For full documentation of all modules, classes, and functions, for both the Python package and the code behind the GUI application, please see the code [on GitHub](https://github.com/Jack6228/Hades).

.. grid:: 2
   :gutter: 4
   :class-container: sd-justify-content-center

   .. grid-item-card:: Obol
      :link: /api/modules/obol
      :link-type: doc
      :class-card: navigation-card blob-hover arrow-action

      All the functions you need to run Hades in Python

   .. grid-item-card:: Visualisations
      :link: /api/modules/visualisations
      :link-type: doc
      :class-card: navigation-card blob-hover arrow-action

      Full reference for all visualisation functions

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents:

   modules/obol
   modules/visualisations