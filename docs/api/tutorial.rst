.. _PythonWalkthrough:

.. title:: Python Walkthrough

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Python Tutorial</span>
         </h1>

      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>v0.9.1</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Tutorial
======================

The page steps through each of the main features of the Hades Python API, providing example code and explanations for each.

We use the :doc:`/case_studies/iceland/index` case study as an example: click on the link to find an interactive Jupyter Notebook, data and ``.hades`` config file.

----

Creating a Model
----------------

To create a model, import the :py:class:`~hades.model.Obol` class and create an instance of it with parameters appropriate for your dataset.

The default parameters are suitable for the Þingmúli dataset, but other options are shown in the code block below.

.. code-block:: python

   from hades_obol import Obol

   model = Obol.newModel(
       mode = 'subalkaline'      # subalkaline or alkaline
       submode = 'tholeiitic'    # tholeiitic or calcalkaline (only for subalkaline mode)
       # FeO = 0.9,              # FeO content of the primary melt (wt%), default is 0.9
   )

Loading a Dataset
-----------------

A `.csv`, `.xlsx`, or `.txt` file containing geochemical data for your samples can be loaded into the model using the :py:meth:`~hades.model.Obol.load_data_suite` method.

This will automatically validate your data and also select initial compositions for each stage of magmatic evolution. To select custom compositions, you can use the :py:meth:`~hades.model.Obol.set_initial_compositions` method and pass a list of sample names from the input file.

.. code-block:: python

   model.load_data_suite('./thingmuli_hekla.xlsx')
   model.set_initial_compositions([None, 'T3-01', 'T7-03', 'auto', 'auto', 'T3-12'])

Customising the Model
---------------------

While Hades employs a default set of K\ :sub:`D` values, mineral banks and other parameters from literature, you can also customise the model to suit your needs. 

.. tip::
    The three methods below all use an intuitive syntax to set parameters for the model. Simply provide as many arguments as you wish with parameter names as ``stage__mineral``. That is, the stage of magmatic evolution is specified first, followed by a double underscore, and then the mineral name. For example, to set the K\ :sub:`D` value for olivine in the primary stage, you would use ``primary__olivine``.

    To apply a setting to all stages or all minerals, you can use the wildcard ``all`` or simply omit the stage or mineral name. For example, to set the K\ :sub:`D` value for olivine in all stages, you could use ``all__olivine``, and to set the K\ :sub:`D` value for all minerals in the primary stage, you could use ``primary__``.

To specify which minerals should be considered in the bulk crystallising mineral assemblage at each stage of magmatic evolution, use the :py:meth:`~hades.model.Obol.set_mineral_usage` method. This allows you to include or exclude specific minerals from the analysis.

.. code-block:: python

   model.set_mineral_usage(
       primary__olivine=True,
       primary__clinopyroxene=True,
       primary__plagioclase=False,
       primitive__olivine=True,
       primitive__clinopyroxene=True,
       primitive__plagioclase=True,
       basic__olivine=False,
       basic__clinopyroxene=True,
       basic__plagioclase=True
   )

To set custom K\ :sub:`D` values for each mineral and stage, use the :py:meth:`~hades.model.Obol.set_Kd` method:

.. code-block:: python

   model.set_Kd(
       primary__olivine=0.3,
       primary__clinopyroxene=0.2,
       primitive__olivine=0.25,
       primitive__clinopyroxene=0.15,
       basic__clinopyroxene=0.1
   )

Finally, to provide custom mineralogies for minerals, use the :py:meth:`~hades.model.Obol.set_mineralogy` method. Each parameter should be a list or numpy array of eight major element oxides in the order: SiO2, TiO2, Al2O3, FeO, MnO, MgO, CaO, Na2O. Hades will automatically normalise the mineralogy to 100 wt% if it does not already sum to 100.

.. code-block:: python

   model.set_mineralogy(
       primary__olivine=[40.0, 0.0, 0.0, 8.0, 0.1, 50.0, 2.0, 0.0],
       primary__clinopyroxene=[50.0, 1.0, 5.0, 10.0, 0.2, 20.0, 10.0, 4.8],
       primitive__olivine=[38.0, 0.0, 0.0, 9.0, 0.1, 51.5, 1.4, 0.0],
       primitive__clinopyroxene=[48.5, 1.2, 6.5, 11.5, 0.3, 19.5, 9.5, 3.5],
       basic__clinopyroxene=[47.5, 1.5, 7.5, 12.5, 0.4, 18.5, 8.5, 3.1]
   )

Running the Model
-----------------

To find the optimal parameters needed to construct the liquid line of descent, we simply use the :py:meth:`~hades.model.Obol.run` method with the desired phase (primary = 1, primitive = 2, etc.) as the argument.

.. code-block:: python

   model.run(1)      # primary -> primitive
   model.run(2)      # primitive -> basic

If our initial input data included trace element concentrations, we can run the trace element modelling, provided the :py:meth:`~hades.model.Obol.run` method has already been called for the relevant stage of magmatic evolution. This is done using the :py:meth:`~hades.model.Obol.runTrace` method.

This method again takes the phase as the argument, as well as an optional argument to specify which accessory minerals should be included in the model. By default, all accessory minerals are included.

The second ``accessory_weights`` argument is a list or numpy array of four binary values, corresponding to apatite, zircon, titanite, and Fe-Ti oxides respectively. A value of 1 indicates that the mineral should be included in the model, while a value of 0 indicates that it should be excluded.

.. code-block:: python

   model.runTrace(1)      # primary -> primitive
   model.runTrace(2, [1, 1, 0, 0])      # primitive -> basic, only include apatite and zircon

Inspecting the Results
----------------------

The :py:meth:`~hades.model.Obol.summary` method prints a summary of the model results.

.. code-block:: python

   model.summary()

Visualising the Results
-----------------------

Instead, we can use functions from the :py:mod:`~hades.visuals` module to create plots of the results. Each function takes a :py:class:`~hades.model.Obol` instance as its first argument, with some optional keyword arguments to customise the output.

Since we have run trace element modelling, we can use the ``mode='traces'`` argument to overlay these results, otherwise the argument is omitted.

.. code-block:: python

   from hades.visuals import bivar

   bivar(
      model, 
      mode='traces',
      y_order=['TiO2', 'Fe2O3', 'Al2O3', 'CaO', 'Na2O', 'K2O'], 
      filename='bivariate_plots_trace_elements.png',
   )

Similarly, we can produce TAS and Harker diagrams using the :py:func:`~hades.visuals.tas` and :py:func:`~hades.visuals.harker` functions respectively.

.. code-block:: python

   from hades.visuals import tas, harker

   tas(
      model, 
      mode='traces',
      filename='tas_diagram_trace_elements.png',
   )

   harker(
      model, 
      mode='traces',
      filename='harker_diagram_trace_elements.png',
   )
 
Exporting the Results
-----------------------

To export the results of the model to an ``.xlsx`` or ``.pdf`` file, the following functions can be used:

.. code-block:: python

   model.export_results_xlsx('model_results.xlsx')
   model.export_results_pdf('model_results.pdf')

Configuration Files
-------------------

``.hades`` files can be saved to store the model configuration, including the dataset, initial compositions, mineral usage, K\ :sub:`D` values, and mineralogies. This allows you to easily reload the model with the same settings in the future, particularly useful for reproducibility and loading in the Windows application.

.. code-block:: python

   model.save_config('./thingmuli_hekla.hades')

Later on:

.. code-block:: python

   model = Obol.newModel()
   model.load_config('./thingmuli_hekla.hades')