.. _ItalyWalkthrough:

.. title:: Walkthrough | Adamello

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Adamello Batholith</span>
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

We first select the calcalkaline option in the 'Setup' section of Hades before clicking the 'Browse...' button to load the ``adamello.xlsx`` file. Clicking on the 'Set Samples' button, we assign samples 'RN6V2', 'RN8', 'RN10', 'RN15V2' and 'RN17V2' for primitive, basic, intermediate, evolved, and end endmembers respectively.

----

Mineralogy
----------

:cite:t:`nandedkar2014evolution` also indicates what minerals crystallise at different stages and also gives electron microprobe analyses of most of these minerals. As such, in the primitive-basic stage we allow the crystallisation of olivine, clinopyroxene, spinel and plagioclase. Olivine and clinopyroxene compositions are taken from :cite:t:`nandedkar2014evolution`, but we allow Hades to use internal compositions for plagioclase and spinel. We also adjust the the plagioclase K\ :sub:`D` value from 1.2 to 3.2 because of the hydrous nature of the experimental chargers. 

For the basic-intermediate and intermediate-evolved stages we only allow the crystallisation of amphibole, plagioclase, orthopyroxene and magnetite. 

In the final evolved to end stage, Hades considers amphibole, plagioclase, magnetite, biotite and quartz. All mineral compositions are from Nandedkar et al. (2014) apart from amphibole that is taken from the internal mineral bank (Table 3). 

All mineral compositions in the table below except amphibole (taken from Hades' internal mineral banks) are from :cite:t:`nandedkar2014evolution` and are in equilibrium with sample RN10 (except for magnetite in the intermediate-evolved stage that is taken from RN15V2). 

Clicking the 'Configure' button enables us to first adjust the K\ :sub:`D` values, and then click on the 'Phase Compositions' tab to edit the mineral compositions for each stage. The table below shows the mineral compositions in wt.% oxides.

=====================  ======  ======  ======  ======  ======  ======  ======  ======
Mineral                SiO2    TiO2    Al2O3   FeO     MnO     MgO     CaO     Na2O
=====================  ======  ======  ======  ======  ======  ======  ======  ======
**Primitive**                                                
Olivine                38.67   0.02    0.03    17.48   43.5    0.27    0.01    0.01
Clinopyroxene          51.69   0.38    3.97    5.69    16.3    21.72   0.24    0.01
**Basic**                                                
Orthopyroxene          49.34   0.37    6.38    17.8    24.43   1.64    0.03    0.02
Amphibole              40.91   1.76    15.53   14.03   13.92   11.03   2.34    0.48
Plagioclase            46.68   0.02    33.35   0.74    0.06    17.37   1.71    0.06
Magnetite              0.07    4.72    13.92   76.87   4.23    0.15    0.03    0.02
**Intermediate**                                                
Amphibole              43.62   2.01    13.26   11.58   15.8    11.14   2.19    0.41
Plagioclase            47.78   0.06    32.59   1.06    0.33    16.18   1.88    0.12
Orthopyroxene          51.78   0.28    5.84    14.01   26.66   1.27    0.09    0.07
Magnetite              0.13    12.93   0.89    84.9    0.99    0.08    0.03    0.04
**Evolved**                                                
Plagioclase            59.3    0.02    28.04   0.38    0.15    4.67    6.97    0.48
Magnetite              0.31    5.4     0.42    93.35   0.4     0.01    0.03    0.07
Quartz                 99.82   0       0.08    0.04    0       0.03    0       0.02
Biotite                41.37   2.07    17.6    9.43    19.77   0.01    0.92    8.82
=====================  ======  ======  ======  ======  ======  ======  ======  ======

Click 'Apply' to save these changes and return to the main window.

----

Running the Model
-----------------

When we click the 'Run' button for each stage in the 'Mineral Modal Abundances' section, we find mineral proportional which are very close to those grown in the fractional crystallisation experiments.

We can model the phosphorous (P) content of the magmas by clicking the 'Trace Elements' button. Entering 0.1, 0.7 and 1 wt.% apatite in the basic, intermediate and evolved stages respectively, provided a good fit to the P liquid line of descent.

.. rubric:: References

.. bibliography::
   :filter: docname in docnames