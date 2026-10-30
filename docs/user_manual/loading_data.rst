.. _LoadingData:

.. title:: Loading Data | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Loading Data</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Loading Data
====================

Upon loading Hades, the first step is to select whether you intend to analyse subalkaline or alkaline rocks, and if the former, whether these rocks follow a tholeiitic or calc-alkaline trend. The checkboxes in the 'Setup' box at the top of the Hades interface can be used to select which mode is to be used, which in turn informs various default parameters such as K\ :sub:`D` values, contributing minerals, and more; see :doc:`/user_manual/parameter_config`.

Loading Data
--------------------

Next, we import a data suite of geochemical data. Hades is able to read Excel spreadsheets (.xlsx), comma separates variable (.csv) or text (.txt) files and is flexible with regards to the orientation and structure of these files. A template spreadsheet is provided below; however, the program expects a table of labelled samples as columns with rows labelled for each major oxide or trace element. 

At a minimum, the eight major oxides must be provided, and if no labels are provided the order is interpreted as SiO2, TiO2, Al2O3, Fe2O3, MgO, CaO, Na2O, K2O. If supplying trace elements, these must be explicitly labelled to ensure correct parsing. Note that Hades currently only utilises geochemical data for the following trace elements, if they are provided in your input file, other traces will be ignored: P, Ba, Rb, Sr, Nb, Zr, Y, La, Ce, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, La, Hf, Ta, Th, U.

To use your file in Hades, click the 'Browse...' button in the 'Magmatic Data' section which will prompt you to find and select your desired file. Hades will automatically load and parse this file, displaying the name of the file which was loaded in the box on the left, and the number of samples loaded to the right of the 'Magmatic Data' box. Hades will also ensure your provided major oxides are normalised to 100 wt.% and also attempt to compute an initial magma composition at each stage of magma evolution, based on a range of SiO2 values for alkaline or subalkaline datasets.

The data suite and any computed initial composition are automatically displayed in the bivariate plots on the right-hand side of the window. The drop-down boxes below this plot can be used to adjust the major oxides which are displayed in the plot. 

Initial Magma Composition
---------------------------

We may wish to configure the initial magma composition computed by Hades, which can be done by clicking the 'Set Samples' button in the 'Magmatic Data' section. In the pop-up window, all of the data suite samples are displayed in a table, as well as an MgO-Al2O3 plot (again, with drop-down boxes to adjust the data shown) of the data and the current initial magma composition overlaid for each phase. To assign a different sample of the data suite to the initial composition of a particular phase, either i) click on a sample in the figure and select a phase to assign it to in the following pop-up, or ii) use the drop-down boxes in the 'Phase Assignment' section to assign samples by name. The figure will update in real-time to reflect your selection, and the 'Apply' button is used to confirm the selection and close the window, which will save the initial magma composition and update the bivariate plots in the main Hades window.
