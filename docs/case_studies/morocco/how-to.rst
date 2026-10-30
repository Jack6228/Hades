.. _Moroccoalkthrough:

.. title:: Walkthrough | Jbel Saghro, Morocco

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Jbel Saghro Volcanic Field, Morocco</span>
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

An alkaline rock suite, we select the alkaline mode in the 'Setup' section of Hades. The ``jbel_saghro.xlsx`` file is loaded by clicking the 'Browse...' button and selecting the file and we allow Hades to use its automatically computed samples for the initial magma compositions for a projected LLOD. 

----

Mineralogy
----------

Pressing the 'Configure' button, we allow Hades to use its default K\ :sub:`D` values but make changes to the mineralogy in the 'Phase Compositions' tab. For the primary to primitive stage, we ensure only olivine, spinel, titanaugite, ilmenite and nepheline are ticked as minerals to be used. For primitive to basic, the default mineralogy was kept alongside biotite and K-feldspar being ticked, as biotite and sanidine are found in some of these lavas. Leucite is deselected. Finally, in the basic to intermediate stage, the default mineralogy was kept but again k-feldspar is added and leucite deselected. 

For each stage, the average titanaugite composition of the olivine and pyroxene nephelinites (provided below) were entered into the mineral phase compositions accordingly. 

=====================  ======  ======  ======  ======  ======  ======  ======  ======
Mineral                SiO2    TiO2    Al2O3   FeO     MnO     MgO     CaO     Na2O
=====================  ======  ======  ======  ======  ======  ======  ======  ======
**Titanaugite**
Primary                46.93   2.303   6.838   7.506   12.59   23.18   0.66    0
Primitive              46.85   1.653   5.318   13.87   9.601   21.39   1.31    0
Basic                  50.84   1.59    2.33    21.05   4.95    12.91   6.33    0
=====================  ======  ======  ======  ======  ======  ======  ======  ======

Click 'Apply' to save these changes and return to the main window.

----

Running the Model
-----------------

Clicking through the 'Run' button for each relevant stage in the 'Mineral Modal Abundances' section will find the optimal bulk mineral assemblage and amount of fractional crystallisation for each stage, displaying the results in the table and plots. 

Results can be further viewed through the 'TAS Diagram' and 'View Mineralogy' buttons, or cna be exported to a PDF or Excel file using the 'export' buttons.