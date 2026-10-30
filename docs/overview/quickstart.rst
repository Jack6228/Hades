.. _Quickstart:

.. title:: Hades Quickstart

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Hades Quickstart</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>Get started with Hades in under 5 minutes</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Quickstart
======================

This guide walks through the Hades GUI and its functionality. It assumes Hades is already installed — if not, see :doc:`installation` first.

By the end of this page you will have an understanding of the Hades interface and be ready to work through one of our case studies. Each step on this page is explained in more detail in the :doc:`User Manual </user_manual/index>`.

Launch Hades from the desktop shortcut or Start menu. The first time you run Hades, it may take a few additional moments to set up. You will see a splash screen while the application loads. The main window will look like this:

.. figure:: /assets/HadesHomepage.png
   :alt: The main Hades GUI
   :align: center
   :width: 70%

.. raw:: html

   <br>
   <br>

**The rest of this page guides you through these sections while using one of the case studies as the working example.**

----

Configuring the Model
---------------------

The 'Setup' tab enables you to select whether your data suite is alkaline or subalkaline, and if the latter, tholeiitic or calc-alkaline. This configures some of Hades' default parameters for the model.

In the 'Magmatic Data' tab, the 'Configure' button can be used to adjust the Fe to FeO ratio, select K\ :sub:`D` values for mineral phases, and specify custom mineral compositions and uptakes for mineral phases. All of these parameters assume default values depending on the selected model type, and can be left unchanged for most cases; mineral compositions are taken from built-in mineral banks (Deer ...) or computed from first principles for olivine.

The 'Load Config File' button can be used to load a previously saved ``.hades`` configuration file. Once a model is configured and run, you can save the configuration for future use - see :doc:`/user_manual/config_files` for more information.

Relevant user manual sections: :doc:`/user_manual/interface` and :doc:`/user_manual/parameter_config`.

----

Loading Data
------------

To load data, press the 'Browse...'' button of the 'Magmatic Data' section. This will enable you to select a ``.csv`` or ``.xlsx`` file and will subsequently load this data, validate it, and plot it in the visualisation panel. In this case, we load the dataset for Þingmúli, Iceland, which you can download from its case study page: :doc:`Þingmúli Case Study </case_studies/iceland/index>`.

Hades ensures that all samples in the data suite are valid (e.g. normalised to 100 wt.% and there are no missing values), major-element oxides are normalised to 100 wt.%, and computes an initial magma composition based on preset SiO2 ranges, where samples are available.

You may override these default magma allocations by pressing this 'Set Samples' button, which enables you to view the samples used in the reference liquid line of descent, or select new ones in a pop-up window. You can use the drop-down items in the 'Phase Assignment' tabs to assign samples by name to a particular phase of evolution, or click on scatter points in the plot to assign them to a phase. The axes on the graph can be changed using the two drop-down buttons at the bottom of the pop-up window.

.. hint:: 
   
   **Try it!** Download the Þingmúli dataset from its case study page, and load it into Hades. Hades will automatically compute a reference LLOD from the data.

Relevant user manual sections: :doc:`/user_manual/loading_data`.

----

Assimilant Input
-----------------

If you wish to include an assimilant in your modelling, Hades enables a composition of major oxides and trace elements to be added in a given amount at each phase. More information on how to use this feature is available in the :doc:`/user_manual/afc` section of the user manual.

----

Running a Model
--------------------

The 'Mineral Modal Abundances' tab initially shows boxes of 0's for all mineral wt.% values and the amount of fractional crystallisation. The 'View' buttons will use the values in these boxes to run the relevant phase of magmatic evolution and display the results in the visualisation panel. 

More usefully, the 'Run' button will apply differential evolution to find the optimal values of these parameters to minimise the misfit between the model and the data. The 'Run' button will display the optimised values in the boxes and overlay the modelled results on the data in the visualisation panel.

The 'Run' buttons have sequential functionality, ensuring the model is run in a stepwise manner, with the results of each phase being used as the starting point for the next. As such, if your initial data suite had no available samples for a particular phase, the 'Run' button is initially disabled. The 'Reset' button will clear a given phase and those following it from the plot. 

.. hint:: 
   
   **Try it!** Having loaded the Þingmúli dataset, press the 'Run' button to find the optimal solution for the fractional crystallisation problem. The modelled results will be overlaid on the data in the visualisation panel. 

   See the :doc:`Þingmúli Case Study </case_studies/iceland/index>` for a more detailed explanation of the results, as well as usage of parameter customisation to improve the model fit.

Relevant user manual sections: :doc:`/user_manual/running_models`.

----

Visualisation Panel
--------------------

The bivariate plots in the main window enable you to view any major oxide data from a 1 x 1 to a 6 x 2 grid of plots. The axes can be changed using the drop-down buttons at the bottom of the visualisation panel.

The data suite is automatically plotted in gold, the initial magma composition in the grey dashed line, and the modelled results in the solid red line. 

Figures in Hades, both in the main GUI, or in pop-up windows can be exported to publication-quality ``.png`` or ``.svg`` files using the save button at the bottom of each figure. The 'Export PDF' button in the 'Optimisation & Controls' tab will also save many of the figures to a single PDF file.

Relevant user manual sections: :doc:`/user_manual/visualisation`.

----

Parameters and Additional Functionality
---------------------------------------

The 'Optimisation & Controls' tab first enables you to adjust the number of iterations and population size for the differential evolution algorithm. The default values are selected to provide a good balance between speed and accuracy, but can be adjusted for more complex datasets. After each optimisation using the 'Run' button, the cost (offset between model and data) is displayed in the bottom status bar. You can monitor this value to determine if the optimisation is converging, and adjust the number of iterations or population size accordingly.

A range of other buttons are available in this tab:

- **TAS Diagram** — plots the data suite and model results on a Total Alkali-Silica diagram, with TAS fields and boundaries overlaid.
- **Mineralogy Info** — displays the mineral compositions and uptakes used in the model, their optimised modal abundances, as well as a single bivariate diagram of the data and mineral compositions at each phase of evolution.
- **Export PDF** — saves all of the inputs, parameters, and outputs to a handy PDF report for future reference (note that the first pop-up with some example options does nothing at the minute, just for testing, but the PDF should save afterwards).
- **Export Data** — saves the data suite and model results to an ``.xlsx`` file for further analysis in other software.
- **Reset All** — clears all inputs, parameters, and visualisations, returning the GUI to its initial state.
- **Reset Plot** — clears the visualisation panel, but retains all inputs and parameters.
- **Quit** — closes the Hades application.
- **Trace Elements** — opens the trace element panel which enables the addition of accessory minerals to an optimised model, and the visualisation of trace element data and model results. This is a more advanced feature, and is not covered in this quickstart guide.
- **Save Config** — saves the current model configuration to a ``.hades`` file for future use.

Relevant user manual sections: :doc:`/user_manual/visualisation`, :doc:`/user_manual/exporting`, and :doc:`/user_manual/trace_modelling`.

----

Now that you are familiar with the Hades workflow, you might want to try out the :doc:`Þingmúli Case Study </case_studies/iceland/index>`, otherwise, you can:

- :doc:`/user_manual/parameter_config` — learn about the parameters used in Hades and how to configure them for your own datasets.
- :doc:`/user_manual/running_models` — learn about the different ways to run models in Hades, and how to interpret the results.
- :doc:`/user_manual/trace_modelling` — learn about the trace element modelling capabilities of Hades, and how to use them to model accessory minerals.

If you use Python and want to run workflows programmatically, see the :doc:`Python Quickstart </api/quickstart>`.