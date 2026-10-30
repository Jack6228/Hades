.. _MadeiraWalkthrough:

.. title:: Walkthrough | Madeira Archipelago

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Madeira and Porto Santo</span>
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

A transitional to alkaline rock suite, we first select the alkaline mode in the 'Setup' section of the :abbr:`GUI (Graphical User Interface)` and then load the ``madeira_porto_santo.xlsx`` data suite file. Using the 'Set Samples' button, we assign samples '4', '37', and '222' to the primary, primitive and end-point compositions, respectively, with all other samples kept at their automatically computed compositions. Click 'Apply' to save these changes and return to the main window.

----

Mineralogy
----------

Clicking the 'Configure' button, we allow Hades to use its default K\ :sub:`D` values. In the 'Phase Compositions' tab, we ensure the following minerals are ticked or unticked for each stage. The Madeira and Porto Santo rocks are not known to contain nepheline, leucite or nosean-haüyne and so these are deselected for all examples. For the primitive-basic stage we allow the mineral bank to be used and we assign olivine, spinel, plagioclase, titanaugite, alkali-amphibole, magnetite and ilmenite as phases to be used. For the basic and intermediate stages, we include olivine, plagioclase, titanaugite, alkali-amphibole, magnetite and ilmenite, but we use the compositions shown in the table below. In the intermediate stage we further allow K-feldspar and biotite to be considered. For the final evolved stage, only olivine, plagioclase, K-feldspar, biotite, ilmenite and magnetite are considered and relevant mineral compositions are taken from the table below.

=====================  ======  ======  ======  ======  ======  ======  ======  ======
Mineral                SiO2    TiO2    Al2O3   FeO     MnO     MgO     CaO     Na2O
=====================  ======  ======  ======  ======  ======  ======  ======  ======
**Clinopyroxene**      48.21   1.702   4.965   9.88    12.64   21.98   0.62    0
**Plagioclase**        
    Basic              51.96   0       30.66   0       0       13.47   3.67    0.242
    Intermediate       54.82   0       28.74   0       0       10.93   5.18    0.337
    Evolved            61.48   0       23.97   0       0       5.504   7.45    1.597
**Magnetite**          0       19.64   3.101   73.57   3.496   0.193   0       0
**Ilmenite**           0       51.14   0.458   43.03   5.249   0.124   0       0

=====================  ======  ======  ======  ======  ======  ======  ======  ======

Click 'Apply' to save these changes and return to the main window.

----

Running the Model
-----------------

Clicking through the 'Run' button for each relevant stage in the 'Mineral Modal Abundances' section will find the optimal bulk mineral assemblage and amount of fractional crystallisation for each stage, displaying the results in the table and plots. 

Results can be further viewed through the 'TAS Diagram' and 'View Mineralogy' buttons, or cna be exported to a PDF or Excel file using the 'export' buttons.