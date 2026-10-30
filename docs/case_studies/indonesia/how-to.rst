.. _OJPWalkthrough:

.. title:: Walkthrough | Ontong Java Plateau

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Ontong Java Plateau</span>
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

To begin the modelling, once Hades is open, the user must firstly pick an initial set-up. The user indicates in the 'Setup' section if the magmatic suite is subalkaline (default) or alkaline and if the former is stipulated the user must say if the subalkaline suite is tholeiitic (default) or calc-alkaline. For OJP, we retain the default settings of subalkaline tholeiitic.


For the Ontong Java Plateau (OJP) data, we set Hades to use a subalkaline tholeiitic data suite since the OJP magmas are anhydrous (0.1 - 0.2 wt.% H2O), and the lavas have tholeiitic compositions. The ``ontong_java_plateau.xlsx`` file contains samples from :cite:t:`hastie_composition_2016` and :cite:t:`sano_experimental_2004` and is loaded by clicking the 'Browse...' button and selecting the file. 

Clicking on the 'Set Samples' button, we assign samples '1187-12 Primary' and '1187-12' from :cite:t:`hastie_composition_2016` as the primary and primitive magma compositions respectively; '1187-12 Primary' has among the highest MgO and lowest SiO2 values available. For the basic sample, we choose Kwiambaita lava '807-12' because it has some of the highest SiO2 and lowest MgO values.

----

Mineralogy
----------

:cite:t:`sano_experimental_2004` present plagioclase and clinopyroxene K\ :sub:`D` values and so we set these to 0.95 and 0.25, respectively, by clicking 'Configure' and editing the table in the 'Geochemistry' tab. In line with experiments and petrological modelling (:cite:t:`sano_experimental_2004` and :cite:t:`herzberg_geodynamic_2004`), we configure Hades to consider only certain minerals. We do this by clicking on the 'Phase Compositions' tab in the configuration window.

In the primitive to basic stage we keep only olivine, spinel, plagioclase and clinopyroxene ticked; ilmenite would also have been considered for such tholeiitic subalkaline rocks by default but we do not consider it here and untick it. Furthermore, we use mineral compositions in the primitive to basic drop-down table from :cite:t:`sano_experimental_2004` for plagioclase and clinopyroxene, as shown in the table below in wt.%.

=====================  ======  ======  ======  ======  ======  ======  ======  ======
Mineral                SiO2    TiO2    Al2O3   FeO     MnO     MgO     CaO     Na2O
=====================  ======  ======  ======  ======  ======  ======  ======  ======
Plagioclase            49.54   0.00    31.12   0.82    0.34    15.82   2.35    0.03
Clinopyroxene          52.53   0.29    3.14    7.95    18.4    17.63   0.15    0.00
=====================  ======  ======  ======  ======  ======  ======  ======  ======

Click 'Apply' to save these changes and return to the main window.

----

Running the Model
-----------------

Clicking the 'Run' button for the primary and then primitive stages in the 'Mineral Modal Abundances' section will find the optimal bulk mineral assemblage and amount of fractional crystallisation for both stages.

Hades predicts a solution with 28% fractional crystallisation of 100 wt.% olivine and 0 wt.% spinel required to reproduce Kroenke primitive lava '1187-12' which is very similar to modelling results from :cite:t:`hastie_composition_2016`. It models the OJP liquid line of descent after the olivine control line with 27% crystallisation of 18.6 wt.% olivine, 5.4 wt.% spinel, 24.2 wt.% clinopyroxene and 51.8 wt.% plagioclase. 

These values will vary, since Hades is not guaranteed to find the global minimum solution, but the modelled trends are very similar to those from :cite:t:`hastie_composition_2016` and :cite:t:`sano_experimental_2004`.

.. rubric:: References

.. bibliography::
   :filter: docname in docnames