.. _Interface:

.. title:: Interface | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Interface</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Interface
====================

Hades is designed to be user friendly and easy-to-use, while also allowing for flexibility and customisation when modelling. The main interface is split into two sections: a control panel on the left where all inputs and options are selected, and a display area on the right where the results are plotted.

The control panel is used to load, manipulate, analyse, plot, and export data and updates the display area in real time, although additional plots can also be created in separate windows. 

.. figure:: /assets/HadesHomepage.png
   :alt: The main Hades GUI
   :align: center
   :width: 70%

.. raw:: html

   <br>
   <br>

At the bottom of the interface is a status bar which provides information about the current state of Hades. This includes messages about loading data, running models, and any errors. It is useful to monitor this area for any errors or important information during use. 

All buttons and functions in Hades are explained in the other sections of the user guide, however some of the simple buttons are outlined below:

 - The 'Reset Plot' button simply clears any computed magma trends from the bivariate plots in the main window, keeping all values and parameters as they are.
 - The 'Reset Defaults' button will reset all variables, plots and parameters to their defaults, as if loading Hades again.
 - 'Help' will launch your browser and take you to the documentation - either online here[link] or to a locally hosted version if you have no available internet connection.
 - 'Quit' will close Hades.

.. Hades is designed to be user friendly and easy-to-use, while also allowing for flexibility and customisation when modelling. The main interface is split into two sections: a control panel on the left where all inputs and options are selected, and a display area on the right where the results are plotted.

.. The control panel is used to load, manipulate, analyse, plot, and export data and updates the display area in real time, although additional plots can also be created in separate windows. The sections below outline what each section of the control panel does and how they should be used. An example workflow and video tutorial are then provided in the ... section.

.. .. figure:: /assets/HadesHomepage.png
..    :alt: Hades Interface
..    :align: center
..    :width: 60%

..    The Hades Interface

.. .. note::
..   By default, the development version of Hades automatically loads with the filepath for an example data suite (Krafla, Iceland) already filled in. This enables you to automatically use the application without having to find data. You can still load a different dataset at any time.

.. Status Bar
.. ------------

.. At the bottom of the interface is a status bar which provides information about the current state of Hades. This includes messages about loading data, running models, and any errors. It is useful to monitor this area for any errors or important information during use.

.. Setup & Config
.. --------------

.. This section allows for switching between using subalkaline (default) and alkaline rocks. When triggered, the window is reloaded to apply the changes. If subalkaline rocks are selected, there is a further option to select tholeiitic or calc-alkaline trends. If neither are selected, all subalkaline minerals are used, otherwise only minerals relevant to the selected trend are used in the model, see paper for full details.

.. The ``configure`` button opens a new window where the default parameters for Hades can be edited (see :doc:`Parameter Configuration <parameter_config>` for more information).

.. Data Suite & Magma
.. ------------------

.. Hades uses a provided suite of compositional data to model fractional crystallisation. This data can be loaded from a file (e.g. ``.csv``, ``.xlsx``, ``.txt``) by pressing the `Browse...` button, with files requiring an (8, N) shape, with an optional index column and/or header row, for example:

.. ...

.. Once loaded, the data suite is automatically plotted in the display area as a series of bivariate plots. An initial magma composition is also computed based on the SiO2 values in the data suite. A data file can be reloaded at any time by pressing the `Plot` button, which will refresh the data and display.

.. .. .. list-table:: Initial Magma Phases and SiO2 Ranges
.. ..     :header-rows: 1
.. ..     :widths: 15 15 15 15 20 15

.. ..     * - Phase
.. ..       - Primitive
.. ..       - Primary
.. ..       - Basic
.. ..       - Intermediate
.. ..       - Silicic
.. ..     * - SiO2 Range (wt%)
.. ..       - < 49
.. ..       - 49-55
.. ..       - 55-60
.. ..       - 60-70
.. ..       - > 70

.. The auto-computed initial composition can be manually adjusted, or a completely new composition can be loaded from a file. Like with the data suite, a file containing an initial magma composition can be loaded by pressing the `Browse...` button in the `Initial Magma` section. This file should be a (6, 8) table with no columns or index, such as:

.. .. list-table:: Example Initial Magma Format
..   :header-rows: 1
..   :widths: 15 15 15 15 15 15 15 15

.. where the index and header here are for clarity only and should not be included in the file. This will overwrite the automatically computed initial magma composition. Alternatively, the `Edit` button can be used to i) manually select samples from the data suite to use as initial magmas for each phase, or ii) select points on a plot of SiO2 v Fe2O3 to define the initial magma compositions. `Plot` will refresh the display area with the latest initial magma composition.

.. Mineral Compositions
.. --------------------

.. This section shows the weight percentages of each mineral in each phase as well as the percentage of fractional crystallisation (FC%). These values can be manually entered to run the model with custom parameters, or can be filled automatically by using the `Optimise` button (see below). Manually provided mineral proportional will be normalised to 100% prior to use in the model.

.. To the right, there are three buttons:

.. - **Run** will use the mineral weights and FC% to simulate the crystallisation of the initial magma specified above and plot this result on the bivariate plots in the display area.
.. - **Optimise** will find the best fitting mineral weights and FC% needed to reach the starting composition of the next phase. This may take a while depending on the complexity of the data and the number of iterations desired (see :ref:`Optimisation Parameters <optimisation-parameters>` below). 
.. - **Reset** clears previous phase's results from the plot and allows them to be re-run or re-optimised with different parameters. This is because Hades ensures that only consecutive phases can be modelled for continuity.

.. .. _optimisation-parameters:

.. Optimisation Parameters
.. -----------------------

.. Here you can adjust the maximum number of iterations for the optimisation, as well as the population size (i.e. how many different solutions are tested in each iteration). Increasing these values may improve the likelihood of finding a global solution which minimises the cost function, but will also increase the time taken to run the optimisation.

.. .. In the future we may add real time reflections of how well the algorithm is fitting so that these parameters can be adjusted accordingly. For now, the cost (how well the optimised parameters fit the data) can be viewed by through the 'Bulk Mineralogy' option (see below).

.. Additional Functions
.. --------------------

.. The buttons at the bottom of the control panel are for additional functions:

.. - **TAS Diagram** will open a new window with a Total Alkali Silica diagram and plot the data suite, initial magma, and optimised magma compositions on it.
.. - **Bulk Mineralogy** will open a new window with a the same bivariate plots as the main display area, but has an option where you can select which phase to plot the bulk mineralogy for. This also displays the compositions of each mineral used in the selected phase, optimised parameters, and results from the optimisation.
.. - **Export Results** will export the current results across all phases to a PDF containing all plots, tables, parameters, and information about the model.
.. - **Reset All** will completely reset Hades.
.. - **Reset Plots** will clear the bivariate plots in the display area.
.. - **Quit** will close the program.