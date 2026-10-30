.. title:: Home

.. raw:: html

   <section class="hero-section">
      <div class="hero-glow" aria-hidden="true">
         <div class="hero-glow-amber"></div>
      </div>

      <div class="hero-container">
         <h1 class="hero-title">
            Welcome to <span class="text-gradient-anim">Hades</span>
         </h1>

         <p class="hero-subtitle">
            <strong>Advanced petrological modelling, made easy and accessible</strong><br><br>
            Whether you prefer a simple point-and-click interface or automating in code, Hades models and solves complex fractional crystallisation and assimilation fractional crystallisation problems for subalkaline and alkaline igneous rocks
         </p>

         <div class="hero-features">
            <div class="feature-item">
               <span class="material-symbols-outlined feature-icon-hero">money_off</span>
               <span>100% Free</span>
            </div>

            <div class="feature-divider"></div>

            <div class="feature-item">
               <span class="material-symbols-outlined feature-icon-hero">lock_open_right</span>
               <span>Open Source</span>
            </div>

            <div class="feature-divider"></div>

            <div class="feature-item">
               <span class="material-symbols-outlined feature-icon-hero">target</span>
               <span>High-Precision Modelling</span>
            </div>
         </div>

      </div>

      <div style="display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 1rem; margin-bottom: 2rem;">
            <a href="https://github.com/Jack6228/Hades/releases" style="text-decoration: none; color: inherit;" target="_blank">
            <div class="hero-features-anim" style="margin-top: 2rem;">
               <div class="action-item">
                  <span class="material-symbols-outlined action-icon-hero" style="margin-top: 0.1rem;">download</span>
                  <span>Download for Windows</span>
               </div>
            </div>
            </a>
            <a href="https://pypi.org/project/hades-obol/" style="text-decoration: none; color: inherit;" target="_blank">
            <div class="hero-features-anim" style="margin-top: 2rem;">
               <div class="action-item">
                  <span class="material-symbols-outlined action-icon-hero" style="margin-top: 0.1rem;">terminal</span>
                  <span>pip install hades-obol</span>
               </div>
            </div>
            </a>
      </div>

   </section>


.. grid:: 1 1 3 3
   :gutter: 3
   :margin: 4 4 0 0

   .. grid-item-card:: Windows Software
      :link: user_manual/index
      :link-type: doc
      :class-card: navigation-card
      
      Use our standalone application - no coding required. Import your data, run mass balance models and export results.
      
      .. raw:: html
      
         <span class="link-button">Open the User Manual</span>

   .. grid-item-card:: Python Interface
      :link: api/python_installation
      :link-type: doc
      :class-card: navigation-card

      The computational engine. Automate your workflows, iterate over thousands of samples, and integrate seamlessly.

      .. raw:: html
      
         <span class="link-button">Use the API</span>

   .. grid-item-card:: Case Studies
      :link: case_studies/index
      :link-type: doc
      :class-card: navigation-card

      See it in action. Real-world workflows modelling fractional crystallisation using the software and the Python module.

      .. raw:: html
      
         <span class="link-button">View Case Studies</span>

----

=============================
How Hades Works
=============================

Hades uses your major and trace element data to model fractional crystallisation (with or without assimilation) of subalkaline and alkaline igneous rocks. Our software uses differential mass balance and optimisation algorithms to compute the composition of the crystallising mineral assemblage and the amount of crystallisation required to reach a daughter melt across a range of evolutionary stages, primary to evolved. 

Hades is vastly customisable, allowing you to define your own mineral assemblages, mineral compositions, and crystallisation paths. 

We offer a faster and more accurate alternative to traditional thermodynamic modelling, all packaged into a user-friendly interface for Windows. For those who prefer to work programmatically, we also provide a Python API for batch processing and automation, available on any platform.

----

=============================
Key Features
=============================

.. raw:: html

   <!-- Include Google Material Icons CDN (Only needed once per site/page) -->
   <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />

      <div class="rst-timeline-container">
         <div class="feature-row">
            <div class="feature-col-icon">
                  <span class="material-symbols-outlined feature-icon">upload</span>
            </div>
            <div class="feature-col-title">
                  <span class="feature-inline-title-main">Simple Input Format</span>
            </div>
            <div class="feature-col-content">
                  Use CSV, Excel or similar format files to structure your major element data and let Hades handle the rest.
            </div>
         </div>

         <div class="feature-row">
            <div class="feature-col-icon">
                  <span class="material-symbols-outlined feature-icon">palette</span>
            </div>
            <div class="feature-col-title">
                  <span class="feature-inline-title-main">Customisable</span>
            </div>
            <div class="feature-col-content">
                  Tailor Hades based on what you already know. For example, add mineral data if you have analysed it and choose which minerals Hades should consider in the crystallising assemblages if you have the petrography.
            </div>
         </div>

         <div class="feature-row">
            <div class="feature-col-icon">
                  <span class="material-symbols-outlined feature-icon">image</span>
            </div>
            <div class="feature-col-title">
                  <span class="feature-inline-title-main">Visualisation</span>
            </div>
            <div class="feature-col-content">
                  Hades presents the uploaded data suite alongside the calculated liquid line of descent in a range of customisable bivariate plots for quick visualisation. The TAS diagram and bivariate plots showing the mineral data is also available. Hades combines the outputs into a downloadable pdf for future reference.  
            </div>
         </div>

         <div class="feature-row">
            <div class="feature-col-icon">
                  <span class="material-symbols-outlined feature-icon">left_click</span>
            </div>
            <div class="feature-col-title">
                  <span class="feature-inline-title-main">Accessible</span>
            </div>
            <div class="feature-col-content">
                  Hades intuitive and simple interface is designed to be user-friendly and enable Geoscientists to model he evolution of magmatic systems. It is available as a standalone application or a Python module for complete automation and workflow integration.
            </div>
         </div>

         <div class="feature-row">
            <div class="feature-col-icon">
                  <span class="material-symbols-outlined feature-icon">tune</span>
            </div>
            <div class="feature-col-title">
                  <span class="feature-inline-title-main">Range</span>
            </div>
            <div class="feature-col-content">
                  Hades can model fractional crystallisation and assimilation fractional crystallisation of subalkaline or alkaline data suites. It can model for hydrous phases and does not require thermodynamic, intrinsic (H<sub>2</sub>O) or extrinsic (P-T) conditions.  
            </div>
         </div>
      </div>

----

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: Citing & License
      :link: /reference/citation
      :link-type: doc
      :class-card: navigation-card blob-hover arrow-action

      Using Hades in your research? Click here to see how to reference Hades.

   .. grid-item-card:: GitHub Repo
      :link: https://github.com/Jack6228/Hades
      :link-type: url
      :class-card: navigation-card blob-hover arrow-action

      All of the code, data, and resources for Hades are open-source and available on GitHub.

   .. grid-item-card:: Read the Paper
      :class-card: navigation-card blob-hover arrow-action

      [In submission]

----

.. raw:: html

   <div class="hades-branding-card">
      <div class="branding-header">
         <h3>The Underworld Architecture</h3>
         <p>A guide to the mythology and naming conventions behind our project</p>
      </div>
      
      <div class="branding-grid">
         <!-- Hades Section -->
         <div class="branding-item">
            <svg class="branding-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
               <path d="M12 3L3 13L12 21L21 13L12 3Z"></path>
               <path d="M12 3L10 11L12 21"></path>
               <path d="M3 13L10 11L21 13"></path>
            </svg>

            <h4>Hades</h4>
            <p>In Greek mythology, the chthonic god Hades (ᾍδης) is the King of the underworld, brother of Zeus and Poseidon. Greeks often referred to Hades as Plouton (Πλούτων), the giver of wealth, as he presided over the fertile soil and mineral riches of the Earth. This latter name is also the etymological root of plutonism.</p>
         </div>

         <!-- Obol Section -->
         <div class="branding-item">
            <svg class="branding-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"> <path d="M22,12 L21,15.8 L19.1,19.1 L15.7,21.1 L12,22.2 L8.2,21 L4.9,19.1 L2.9,15.7 L2,12 L2.9,8.2 L4.8,4.9 L8.3,2.8 L12,2 L15.8,2.9 L19.1,4.9 L21.1,8.3 Z"/> <circle cx="12" cy="12" r="6.8"/> <path d="M10.5,8 L10,9.5 L10.5,11 L10,12 L10.5,13.5 L11.5,15.5 L12,16.5 L14,18 Q15,17.5 14.5,15 Q16,12 14.5,9.5 Q13,7 10.5,8 Z"/> </svg>
            <h4>hades-obol</h4>
            <p>An Obol was the silver coin placed in the mouth of the departed to pay Charon, the Ferryman, for passage over the river Acheron into the underworld. The Python engine behind Hades, obol, interfaces with the underworld to model the evolution of magmatic systems.</p> 
         </div>

      </div>
      </div>


.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Overview

   overview/about
   overview/installation
   overview/quickstart

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: User Manual

   user_manual/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :titlesonly:
   :caption: Case Studies

   case_studies/index
   
.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Python API
   :titlesonly: 

   api/python_installation
   api/quickstart
   api/tutorial
   api/index

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Reference

   reference/theory
   reference/citation
   reference/changelog

..
   .. toctree::
      :hidden:
      :maxdepth: 1
      :caption: TEMP

      template/index
..