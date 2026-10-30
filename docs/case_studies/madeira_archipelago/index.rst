.. _Madeira:

.. title:: Madeira Archipelago Case Study

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Madeira Archipelago</span>
         </h1>

      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>Transitional</span>
      <div class="feature-divider"></div>
         Primary &nbsp; ➜ &nbsp; Evolved
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Madeira Archipelago
===================

..
   
----

The islands of Madeira and Porto Santo are located in the Madeira Archipelago, northeast of the Atlantic Ocean. The islands are formed of transitional to alkaline rocks ranging from primary to evolved compositions, formed through fractional crystallisation. 

Instructions & Tutorials
------------------------

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: Software How-To
      :link: how-to
      :link-type: doc
      :class-card: navigation-card blob-hover arrow-action

      Step-by-step instructions for the Hades Windows Application and the resulting visualisations

   .. grid-item-card:: Python Tutorial
      :link: api-use
      :class-card: navigation-card blob-hover arrow-action

      Click here to launch the Jupyter Notebook tutorial in Google Colab and run in your browser. No installation required. Or, download the file below.

Data & Resources
----------------

All of the data, resources and outputs are available on GitHub, as linked below, but can be recreated using the Hades Windows Application or the Python API. The ``.hades`` configuration file can be uploaded directly into Hades to load the data and custom settings, or used in the Python API.
      
.. rubric:: Data & Code
   
.. grid:: 1 1 3 3
   :gutter: 3
   :margin: 4 4 0 0

   .. grid-item-card:: Data Suite
      :link: https://github.com/Jack6228/Hades/blob/main/examples/madeira_archipelago/madeira_porto_santo.xlsx
      :class-card: navigation-card arrow-action blob-hover
      
      Download the geochemical data suite for this case study
      
   .. grid-item-card:: Config File
      :link: https://github.com/Jack6228/Hades/blob/main/examples/madeira_archipelago/madeira_porto_santo.hades
      :class-card: navigation-card arrow-action blob-hover

      The ``.hades`` file can be uploaded directly into Hades to load the data and custom settings, or used in the Python API.

   .. grid-item-card:: Jupyter Notebook
      :link: https://github.com/Jack6228/Hades/blob/main/examples/madeira_archipelago/madeira_porto_santo.ipynb
      :class-card: navigation-card arrow-action blob-hover

      Replicate the analysis programmatically using the Python API. The notebook contains step-by-step instructions and code to reproduce the results.

.. rubric:: Outputs & Results

.. grid:: 1 1 3 3
   :gutter: 3
   :margin: 4 4 0 0

   .. grid-item-card:: PDF Summary
      :link: https://github.com/Jack6228/Hades/blob/main/examples/madeira_archipelago/outputs/results.pdf
      :class-card: navigation-card arrow-action blob-hover
      
      The auto-generated PDF summary of the results
      
   .. grid-item-card:: Data Spreadsheet
      :link: https://github.com/Jack6228/Hades/blob/main/examples/madeira_archipelago/outputs/data_output.xlsx
      :class-card: navigation-card arrow-action blob-hover

      All key results - mineral proportions, compositions, etc. - all in one spreadsheet

----

.. dropdown:: Parameter Landscape Maps
   :animate: fade-in
   :icon: info

   These figures visualise a large number of near-optimal candidate from the final generation population of many independent differential evolution runs. To learn more about what these figures represent, how to interpret them, and how to generate them, see the :doc:`Differential Evolution </user_manual/parameter_mapping>` section of the user manual.

   .. tab-set::

      .. tab-item:: Primary

         .. figure:: /assets/ParameterMaps/madeira_archipelago/1_Primary-Primitive_CornerPlot.png
            :alt: Primary parameter landscape map
            :name: fig-p1
            :align: center
            :figwidth: 70%
            :width: 90%
            
      .. tab-item:: Primitive
         
         .. figure:: /assets/ParameterMaps/madeira_archipelago/2_Primitive-Basic_CornerPlot.png
            :alt: Primitive parameter landscape map
            :name: fig-p2
            :align: center
            :figwidth: 70%
            :width: 90%

      .. tab-item:: Basic
         
         .. figure:: /assets/ParameterMaps/madeira_archipelago/3_Basic-Intermediate_CornerPlot.png
            :alt: Basic-Intermediate parameter landscape map
            :name: fig-p3
            :align: center
            :figwidth: 70%
            :width: 90%

      .. tab-item:: Intermediate
         
         .. figure:: /assets/ParameterMaps/madeira_archipelago/4_Intermediate-Evolved_CornerPlot.png
            :alt: Intermediate parameter landscape map
            :name: fig-p4
            :align: center
            :figwidth: 70%
            :width: 90%

      .. tab-item:: Evolved
         
         .. figure:: /assets/ParameterMaps/madeira_archipelago/5_Evolved-End_CornerPlot.png
            :alt: Evolved parameter landscape map
            :name: fig-p5
            :align: center
            :figwidth: 70%
            :width: 90%

.. rubric:: References

.. .. bibliography::
..    :filter: docname in docnames
   
.. toctree::
   :maxdepth: 1
   :hidden:

   how-to