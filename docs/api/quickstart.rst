.. _PythonQuickstart:

.. title:: Python Quickstart

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Python Quickstart</span>
         </h1>

      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>pip install hades-obol</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Quickstart
======================

After installing ``hades-obol`` (see :doc:`/api/python_installation`), you can run a complete analysis in just a few lines of code.

Here, we present a minimal example that loads a dataset, configures a model, runs an analysis, and provides the numeric and visual results. To learn more about customising the analysis, see the :doc:`Case Studies </case_studies/index>`, or have a look at the :doc:`API Reference </api/index>`.

.. contents:: On this page
   :local:
   :depth: 1

----

Minimal Example
----------------

The following code runs a complete analysis using Hades' default settings. We use the data suite from the :doc:`Ontong Java Plateau </case_studies/indonesia/index>` case study as an example, which contains data from the primary through basic stages of magmatic evolution.

.. First, we load the :py:class:`~hades.model.Obol` class and create an instance of it with parameters appropriate for our dataset.

.. code-block:: python

   from hades_obol import Obol

   model = Obol.newModel()
   model.load_data_suite('./OJP.xlsx')    # load data

   model.run(1)      # primary -> primitive
   model.run(2)      # primitive -> basic

   model.summary()   # print a summary of the results










What Each Step Does
-------------------

.. raw:: html

   <div class="timeline-section-header">
      <span class="timeline-title-badge">Loading Data</span>
   </div>

.. code-block:: python

   from hades_obol import Obol

   model = Obol.newModel()
   model.load_data_suite('./OJP.xlsx')    # load data

``Obol.newModel()`` creates a new instance of the ``Model`` class, which is the main interface for running analyses in Hades. The ``load_data_suite()`` method loads a dataset from an Excel, ``.txt`` or ``.txt`` file and prepares it for analysis.

.. raw:: html

   <div class="timeline-section-header">
      <span class="timeline-title-badge">Running the Model</span>
   </div>

.. code-block:: python

   model.run(1)      # primary -> primitive
   model.run(2)      # primitive -> basic

The ``run()`` method executes the analysis for a given stage of magmatic evolution. In this example, we run two stages: primary to primitive, and primitive to basic.

.. raw:: html

   <div class="timeline-section-header">
      <span class="timeline-title-badge">Inspecting Results</span>
   </div>

.. code-block:: python

   model.summary()

To view a summary of the results, we call the ``summary()`` method on the model instance. This prints key output values to the console.

----

Extending the Example
---------------------

The above example uses default settings for a subalkaline, tholeiitic data suite. You can customise the analysis by adjusting model parameters and controlling geochemical processing options.

.. raw:: html

   <div class="timeline-section-header">
      <span class="timeline-title-badge">Model Configuration</span>
   </div>

.. code-block:: python

   model = Obol.newModel(
      mode = 'subalkaline',
      submode = 'calk-alkaline'
   )

This configures the model for a calc-alkaline data suite, which changes some default parameters in Hades, for example, which minerals are considered to contribute to the bulk crystallising mineral assemblage.

For the ``subalkaline`` mode, ``tholeitic`` and ``calc-alkaline`` are the two available submodes. For alkaline rocks, use ``mode='alkaline'``; there is n submode for alkaline rocks.

You can also configure the FeO/Fe2+ ratio, which is 0.9 by default. For example, to set it to 0.92 when running an alkaline model, use:

.. code-block:: python

   model = Obol.newModel(
      mode = 'alkaline',
      FeO_Fe2pO_Ratio = 0.92
   )

.. raw:: html

   <div class="timeline-section-header">
      <span class="timeline-title-badge">Visualising Results</span>
   </div>

Hades has a range of built-in visualisation functions to help you explore the results of your analysis. These are available in the ``hades.visuals`` module, all of which take a ``Model`` instance as their first argument, with some optional keyword arguments to customise the output.

.. code-block:: python

   from hades.visuals import bivar, tas, Harker, mineral_usage

.. tab-set::

   .. tab-item:: bivar

      This plots bivariate diagrams for a range of major oxide elements.
      
      .. code-block:: python

         bivar(
            model, 
            y_order=['TiO2', 'Fe2O3', 'Al2O3', 'CaO', 'Na2O', 'K2O'], 
            filename='bivariate_plots.png',
         )

      .. image:: /assets/ontong_java/bivariate_plots.png
         :alt: Bivariate plots example
         :align: center
         :width: 60%

   .. tab-item:: tas

      To plot a total alkali-silica (TAS) diagram, use the ``tas()`` function:

      .. code-block:: python

         tas(
            model, 
            filename='tas_diagram.png'
         )

      .. image:: /assets/ontong_java/tas_diagram.png
         :alt: TAS diagram example
         :align: center
         :width: 60%

   .. tab-item:: Harker

      Harker diagrams are a type of variation diagram which plots oxide and trace element concentrations against silica content. 

      .. code-block:: python

         Harker(model) # plots 'P', 'Zr', 'Ce' by default

         # To specify which oxides to plot, use the ``y_order`` keyword argument:
         Harker(model, y_order=['Zr', 'Nb', 'Y', 'Sr', 'Ba'])

      .. image:: /assets/ontong_java/Harker.png
         :alt: Bivariate plots example
         :align: center
         :width: 60%

   .. tab-item:: mineral_usage

      This handy function displays a binary representation of which minerals are contributing to the bulk crystallising mineral assemblage at each stage of magmatic evolution.

      .. code-block:: python

         mineral_usage(
            model,
            filename='mineral_usage.png',
         )

      .. image:: /assets/ontong_java/mineral_usage.png
         :alt: Mineral usage example
         :align: center
         :width: 60%

.. raw:: html

   <div class="timeline-section-header">
      <span class="timeline-title-badge">.hades Configuration Files</span>
   </div>

To save custom model configurations - which can be used both in the GUI and in Python - you can export a ``.hades`` configuration file. This will automatically save the data, model parameters, and any other settings you have changed from the defaults, so that you can easily reproduce your analysis later.

After setting your parameters, use the ``save_config()`` method to save a configuration file:

.. code-block:: python

   model.save_config('my_config.hades')

This can then be loaded into a new model instance using the ``load_config()`` method:

.. code-block:: python

   model = Obol.newModel()             # creates a new model
   model.load_config('my_config.hades')   # loads the saved configuration

----

Next Steps
----------

- :doc:`/api/modules/obol` — full parameter reference for ``hades-obol`` 
- :doc:`/api/modules/visualisations` — complete plotting options
- :doc:`/case_studies/index` — Find Jupyter Notebooks for each case study