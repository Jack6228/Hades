.. _GautemalaWalkthrough:

.. title:: Walkthrough | Santa María

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Santa María Volcano</span>
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

For this dataset, we select the calc-alkaline magmatic suite in the 'Setup' section of Hades. The ``santa_maria.xlsx`` file is loaded by clicking the 'Browse...' button and selecting the file.

We do not assign a sample (select 'None') for the primary, primitive and end stages, but assign samples 'SM104', S1120' and 'S1004' as the basic, intermediate and evolved stage endmembers, respectively.

----

Mineralogy
----------

In the 'Configure' button, we first adjust the K\ :sub:`D` value for plagioclase to 3.4 which is which is representative of an evolved hydrous melt with 4 wt.% H2O (evidenced by amphibole and biotite in the rocks; :cite:t:`sisson_experimental_1993`).

Then under the 'Phase Compositions' tab, we keep ticked olivine, clinopyroxene, orthopyroxene, plagioclase, magnetite and ilmenite in the basic-intermediate stage and clinopyroxene, orthopyroxene, plagioclase, amphibole, K-feldspar, biotite, quartz, magnetite and ilmenite for the intermediate-evolved stage. 

Mineral compositions are available for the 1922 dacitic dome suite (:cite:t:`rose_volcanic_1987` and :cite:t:`singer_tracking_2011`; see table below) and thus are included in the 'intermediate-evolved' mineral phase compositions instead of drawing compositions from the pre-determined mineral banks. The mineral banks are used for all other minerals. 

=====================  ======  ======  ======  ======  ======  ======  ======  ======
Mineral                SiO2    TiO2    Al2O3   FeO     MnO     MgO     CaO     Na2O
=====================  ======  ======  ======  ======  ======  ======  ======  ======
Clinopyroxene          51.93   0.2     1.63    10.43   15.4    19.79   0.61    0
Orthopyroxene          52.06   0.1     0.79    20.92   24.95   0.79    0.39    0
Plagioclase            56.26   0       27.83   0.33    0.1     9.75    5.53    0.2
Amphibole              42.78   2.34    11.79   14.34   15.04   10.77   2.54    0.41
Magnetite              0.67    7.42    2.7     87.18   1.74    0.19    0.1     0
=====================  ======  ======  ======  ======  ======  ======  ======  ======

----

Running the Model
-----------------

Iterating through the stages, we click the 'Run' button for each stage in the 'Mineral Modal Abundances' section to find the optimal bulk mineral assemblage and amount of fractional crystallisation for each stage.

The results are visible in the table to the left of the 'Run' buttons, or data can be viewed interactively via the 'View Mineralogy' button. The results can also be exported to an Excel file or PDF report by clicking either 'export' button.

.. rubric:: References

.. bibliography::
   :filter: docname in docnames