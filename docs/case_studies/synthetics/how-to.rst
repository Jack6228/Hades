.. _SyntheticWalkthrough:

.. title:: Walkthrough | Synthetic Validation

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Synthetic Validation</span>
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


To create synthetic data, we start with a known primary magma composition and compute by hand the resulting compositions after fractional crystallisation of a known mineral assemblage. 

For example, we evolve this primary magma with 100% of mineral 'A' through 15% fractional crystallisation to produce a new composition. We continue from this primitive composition with 25% crystallisation of 25% mineral 'A' and 75% mineral 'B'. We continue up to the evolved stage, which has four contributing minerals. See the drop-down below for full details.

The ``synthetics.csv`` file contains the compositions of these four stages which we use as the input for Hades to find the optimal bulk mineral assemblage and amount of fractional crystallisation which were used.

**Note:** We assign these arbitrary minerals to clinopyroxene, orthopyroxene, plagioclase, and amphibole in the Hades mineralogy settings, though they are not intended to represent these minerals in a petrological sense and are for illustrative purposes only.

.. dropdown:: Parameters for Synthetic Data Generation
   :animate: fade-in
   :icon: info

   The primitive through evolved compositions are computed with from an initial primary magma, and the following parameters:

   =====================  ======  ======  ======  ======  ====== 
   Phase                  FC%     A       B       C       D      
   =====================  ======  ======  ======  ======  ====== 
   Primary                15      100
   Primitive              20      25      75
   Basic                  25      10      45      45  
   Intermediate           30      2.5     40      40      17.5
   =====================  ======  ======  ======  ======  ======  

   where A = clinopyroxene, B = orthopyroxene, C = plagioclase, D = amphibole are in wt.%.

   This results in the following compositions, as computed by hand, which are used in the ``SyntheticDataSuite.csv`` file:

   =====================  ======  ======  ======  ======  ======  ======  ======  ======
   Sample Name            SiO2    TiO2    Al2O3   FeO     MnO     MgO     CaO     Na2O
   =====================  ======  ======  ======  ======  ======  ======  ======  ======
   Primary                51.10   0.07    30.07   0.78    0.17    14.39   3.33    0.08
   Primitive              57.83   0.04    26.13   0.51    0.03    9.06    6.08    0.31
   Basic                  59.90   0.02    24.85   0.38    0.01    7.15    7.14    0.54
   Intermediate           50.78   1.08    1.97    12.28   14.07   19.51   0.31    0.00
   Evolved                48.86   0.76    1.65    22.42   9.21    16.86   0.24    0.00
   =====================  ======  ======  ======  ======  ======  ======  ======  ======

We load the file using the 'Browse...' button and then select 'Set Samples' to assign the samples to the four phases of evolution - they are named accordingly.

----

Mineralogy
----------

The table below shows the mineral compositions used to generate the synthetic data, which we expect Hades to recover. Values in wt.%.

=====================  ===============  =====  =====  =====  =====  =====  =====  =====  =====
Mineral                Assigned to      SiO2   TiO2   Al2O3  FeO    MnO    MgO    CaO    Na2O
=====================  ===============  =====  =====  =====  =====  =====  =====  =====  =====
A                      orthopyroxene    48.00  1.00   6.00   10.00  14.00  19.50  1.00   0.50
B                      clinopyroxene    40.00  0.25   1.00   17.00  40.00  1.25   0.25   0.25
C                      plagioclase      50.00  0.00   31.00  0.00   0.00   16.00  2.50   0.50
D                      amphibole        0.00   5.00   0.00   95.00  0.00   0.00   0.00   0.00
=====================  ===============  =====  =====  =====  =====  =====  =====  =====  =====

By clicking on the 'Configure' button and then the 'Mineralogy' tab, we can copy and paste these values into the table in Hades for the relevant minerals and apply.

----

Running the Model
-----------------

Since this problem has only a few minerals, we increase the population size and maximum number of iterations to allow Hades to perform a more thorough search of the parameter space. We will reflect on the effect of these parameters in the results section below.

To find the optimal bulk mineral crystallising assemblage, press the 'Run' buttons for the primitive through evolved  sequentially. 

This should (if Hades finds the correct solution) display a perfect fit of the modelled compositions (solid red line) to the initial composition (grey dashed lines) in the bivariate plots.

The boxes of the 'Mineral Modal Abundances' section will automatically populate with the optimised values for the mineral weights (0-1) for each mineral, and the amount of fractional crystallisation (0-1) for each phase. These values should match those provided in the drop-down section above. 

The 'View' buttons can be used to run the model with these optimised values (or whatever values have been inputted to the boxes) and display the results in the visualisation panel. We can also view these results in more detail by clicking on the 'Mineralogy Info' buttons which displays the optimised values and the mineralogy on a bivariate plot in a new window.

----

Results
-------

We observe that Hades perfectly recovers the expected parameters in the first three cases, but is off by a few tenths of a percentage point in the 4-mineral case. This is because the search space is sufficiently complex that the optimisation algorithm has not fully converged to the global minimum. This reflects why Hades only provides a 'best-guess' solution, particularly in real-world problems where we have polymineralic assemblages and more complex geochemical evolution.

You can read more about differential evolution and the optimisation algorithm in the :doc:`Differential Evolution </user_manual/differential_evolution>` section of the user manual. To better understand the parameter space explored by Hades when trying to find a solution, see the :doc:`Parameter Mapping </user_manual/parameter_mapping>` section of the user manual. Parameter map visualisations for this problem are available at the bottom of the :doc:`previous page </case_studies/synthetics/index>`.