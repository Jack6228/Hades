.. _RunningModels:

.. title:: Running a Model | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Running a Model</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Running a Model
====================

Hades has a range of functions; primarily, it uses an optimisation algorithm to find the optimal bulk crystallising mineral assemblage to reconstruct a projected liquid line of descent (:abbr:`LLOD (liquid line of descent)`). However, it can also forward model a set of mineral modal abundances under a given percentage of fractional crystallisation and display the resulting liquid line of descent. Furthermore, an assimilant can be added throughout stages of fractional crystallisation (AFC) to model xyz, and trace element analyses (with and without AFC) can be performed to predict the amounts of accessory minerals required to reproduce the :abbr:`LLOD (liquid line of descent)`.

The following sections explain each of these functions in conjunction with how Hades works, though you may wish to skip to a particular section of interest.

Optimising a Solution
---------------------------

Once a data suite is loaded and any K\ :sub:`D` values, mineral compositions etc. are set using the 'Configure' button, to find an optimal bulk crystallising mineral assemblage, we use the 'Run' buttons. The 'Run' button can be initially clicked for any phase which has an associated initial magma composition, and thereafter clicked sequentially to re-run a given phase's optimisation, or to optimise the next phase.

Once the 'Run' button is clicked, Hades runs many models starting at your initial magma composition, modelling fractional crystallisation with a range of mineral modal abundances and percentages of :abbr:`FC (fractional crystallisation)`. Our differential evolution algorithm explores these solutions and converges on one which best fits your data and models the :abbr:`LLOD (liquid line of descent)` as best as possible. 

Differential evolution is an optimisation algorithm and so will produce slightly different solutions on each run. The variation in these solutions depend on the complexity of your problem (e.g. how many minerals contribute to the bulk assemblage). The 'Controls' section at the bottom of the Hades window has two numerical controls for the population size and number of iterations. These control how 'deeply' the differential evolution algorithm should search for the best solution. Increasing the number of iterations means that Hades will run more :abbr:`FC (fractional crystallisation)` models when finding an optimal solution, increasing the likelihood of finding an improvement. Increasing the population size means that models with a wider range of scenarios will be modelled. Increasing either value should provide a more stable solution, but at the expense of a longer computational time. To learn more about this optimisation process, and to see how the complexity of a problem affects the accuracy and stability of a solution Hades finds, see :doc:`/user_manual/differential_evolution`.

Once Hades finds an optimal solution, it will automatically plot this in each bivariate plot in red, for comparison to the initial magma (grey dashed line) which it has tried to reproduce. The 'cost' of the solution - that is, a measure of the difference between the expected, initial magma composition, and the newly found, optimised composition - is shown in the status bar at the bottom of the window (discussed more in the following paragraph). Hades also displays all of the mineral abundances and percentage of :abbr:`FC (fractional crystallisation)` which were found to result in this optimal solution, given your data and parameters selected.

We can re-click the 'Run' button to run the optimisation again, which might find a slightly different solution, updating the plot and table of values, respectively. If the graphical solutions vary dramatically between runs, or the cost value in the status bar is fluctuating, you may wish to increase the number of iterations or the population size until a more stable solution is obtained. If the cost value is similar between runs, Hades has likely found an optimal value. In extremely complex systems, Hades may not be able to find a consistent, stable solution, and user judgement should always be applied to determine the validity of a solution presented by Hades.

Having optimised one phase of evolution, we can use the 'Run' buttons in the following phases (where we have an initial magma composition and coverage by the data suite) to optimise these subsequent phases.

Modelling an LLOD 
--------------------

If Hades has found optimal solutions, rows in the table of mineral abundances and percentages of :abbr:`FC (fractional crystallisation)` at each phase will be filled in. Alternatively, values can be entered manually to model a single fractional crystallisation run with those values and visualise the results. Note that when manually adjusting mineral abundances, Hades will force normalisation to 100 wt.%. 
