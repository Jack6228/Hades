.. _IcelandUsage:

.. title:: Walkthrough | Þingmúli, Iceland

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Þingmúli and Hekla, Iceland</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>Walkthrough</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Walkthrough
===================

..

----

Data Suite
------------


Start by loading the ``thingmuli_hekla.xlsx`` data suite by using the 'Browse...' button. Hades will automatically compute the initial compositions for the model, but we will press the 'Set Samples' button to edit this default selection. In the subsequent pop-up window, select the following samples for the initial compositions:

* set the primary sample to ``None``
* sample ``T3-01`` for the primitive composition,
* sample ``T7-03`` for basic,
* leave the automatic selection for the intermediate and evolved phases,
* sample ``T3-12`` for the 'end' composition.

.. rubric::  Mineralogy

We slightly adjust the default mineralogy settings using the 'Configure' button. We use K\ :sub:`D` values of 0.95 and 0.25 for plagioclase and clinopyroxene, respectively, by editing the values in the 'Geochemistry' tab.

In the 'Phase Compositions' tab, we further adjust the default mineral usage for each phase, removing spinel from all stages, as well as orthopyroxene apart from in the intermediate stage and quartz apart from the evolved stage. We use clinopyroxene, plagioclase, magnetite, and ilmenite for all phases, leaving all others as default.

Custom mineral compositions are used for plagioclase and clinopyroxene, as shown in the table below in wt.%:

=====================  ======  ======  ======  ======  ======  ======  ======  ======
Mineral                SiO2    TiO2    Al2O3   FeO     MnO     MgO     CaO     Na2O
=====================  ======  ======  ======  ======  ======  ======  ======  ======
Basic plag.            51.10   0.07    30.07   0.78    0.17    14.39   3.33    0.08
Intermediate plag.     57.83   0.04    26.13   0.51    0.03    9.06    6.08    0.31
Evolved plag.          59.90   0.02    24.85   0.38    0.01    7.15    7.14    0.54
Basic cpx              50.78   1.08    1.97    12.28   14.07   19.51   0.31    0.00
Intermediate cpx       48.86   0.76    1.65    22.42   9.21    16.86   0.24    0.00
Evolved cpx            47.21   0.44    0.95    29.34   3.11    18.70   0.25    0.00
=====================  ======  ======  ======  ======  ======  ======  ======  ======

One should be able to copy and paste values from each row into the table in Hades directly. Press 'Apply' to save these changes and return to the main window.

----

Running the model
-----------------

To find the optimal bulk mineral crystallising assemblage, press the 'Run' buttons for the primitive through evolved  sequentially. Each button only becomes active after the previous phase has been run, ensuring that the model is run in order. This should display a good fit of the modelled compositions (solid red line) to the initial composition (grey dashed lines) in the bivariate plots.

The boxes of the 'Mineral Modal Abundances' section will automatically populate with the optimised values for the mineral weights (0-1) for each mineral, and the amount of fractional crystallisation (0-1) for each phase. The 'View' buttons can be used to run the model with these optimised values (or whatever values have been inputted to the boxes) and display the results in the visualisation panel.

We can also view these results in more detail by clicking on the 'View Mineralogy' buttons which displays the optimised values and the mineralogy on a bivariate plot in a new window.

.. rubric:: Trace Element Modelling

To assess the impact of adding accessory minerals to the melt evolution, having modelled the liquid line of descent for the major elements, we can click on the 'Trace Elements' button to open the trace element panel. Here, we can add wt.% values of four key accessory minerals, between 0-100.

This will add the desired amount of the accessory mineral to the melt evolution, and reduce the amount of the other (non-accessory) minerals accordingly. Pressing 'View' wil re-run the model and display the updated trend line in the Harker diagrams below. Adjusting the amounts of accessory minerals will change the modelled trace element trends, and can be used to assess the impact of accessory mineral crystallisation on the melt evolution.

Once an optimal accessory mineral assemblage has been identified, closing the trace element panel will return to the main window, and the optimised accessory mineral values will be saved for future use.

For Þingmúli and Hekla, inflections in the P- and Zr-SiO2 Harker plots can be modelled if 0.75 wt.% apatite is added to the basic-intermediate stage, 2 wt.% apatite and 0.1 wt.% zircon are added to the intermediate-evolved stage, and 0.75 wt.% apatite and 0.5 wt.% zircon are added to the evolved stage. 

.. note::
    The trace element results are saved only until the main model is reset or re-run, at which point the optimised accessory mineral values will be cleared. You may wish to export the results as a PDF or Excel file after closing the trace analysis window to save the model outputs.

.. rubric:: References

.. bibliography::
   :filter: docname in docnames