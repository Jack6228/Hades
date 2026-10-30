.. _Theory:

.. title:: Hades User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            What is <span class="text-gradient-anim">Hades?</span>
         </h1>
      </div>
   </section>

.. rst-class:: hero-title-hidden

About Hades 
=========================

.. raw:: html

   <div style="text-align: center; font-weight: bold; width: 60%; margin: 0 auto 1rem; font-size: 1.1rem; margin-top: 1rem; margin-bottom: 2rem; line-height: 1.5rem;">
      Hades was developed to provide a user-friendly interface for petrological modelling, utilising advanced computational methods without users requiring extensive programming knowledge
   </div>

.. grid:: 1 1 3 3
   :gutter: 3
   :margin: 4 4 0 0

   .. grid-item-card:: Desktop Software
      :link: /user_manual/index
      :link-type: doc
      :class-card: navigation-card
      
      Use our standalone application - no coding required. Import your data, run mass balance models and export results.
      
      .. raw:: html
      
         <span class="link-button">Open the User Manual</span>

   .. grid-item-card:: Python Interface
      :link: /api/index
      :link-type: doc
      :class-card: navigation-card

      The core computational engine. Automate your workflows, iterate over thousands of samples, and integrate seamlessly.

      .. raw:: html
      
         <span class="link-button">Explore the API</span>

   .. grid-item-card:: Case Studies
      :link: /case_studies/index
      :link-type: doc
      :class-card: navigation-card

      See it in action. Real-world workflows modelling fractional crystallisation using both the software and the Python module.

      .. raw:: html
      
         <span class="link-button">View Case Studies</span>

Magmas, that eventually cool to form the wide variety of igneous rock types on the planet, are dominantly derived from the partial melting of peridotite rocks in the mantle and some are generated from the fusion of crustal sources (e.g., :cite:t:`mckenzie_partial_1991`; :cite:t:`nutman_3850_2007`). Although magma mixing, crustal contamination and assimilation are important factors that contribute to magmatic differentiation :cite:t:`depaolo_trace_1981`; :cite:t:`davidson_amphibole_2007`, the dominant process that drives magmatic evolution is fractional crystallisation :cite:t:`keskin_fc-modeler_2002`. 

Many computer programs have been designed to aid the igneous petrologist in modelling magma composition as it evolves, but here we present a simpler interactive petrological program called Hades that identifies the anhydrous and hydrous crystallising phases required during fractional crystallisation to model the magmatic evolution of a subalkaline or alkaline magmatic liquid line of descent, independent of pressure and temperature.

Hades primarily uses major elements to calculate an olivine control line from a primary magma composition and then uses provided mineral compositions or selects phase compositions from a simple internal mineral bank that are close to being in equilibrium with the melt that is being investigated to model a magmatic suite of rocks from primary to evolved compositions. Hades has the additional function of both modelling the effects of crustal assimilation on an ascending magma as it evolves down the liquid line of descent, as well as using the major element results to model the evolution of the trace elements during magmatic differentiation. Hades is built around a population-based global search method for calculating the modal abundance of appropriate phases required to explain a liquid line of descent in several bivariate diagrams. This is important as previous programs designed to use older least squares methods can no longer be used because they use older systems no longer supported. 

.. rubric:: References

.. bibliography::
   :filter: docname in docnames