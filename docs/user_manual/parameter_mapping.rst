.. _ParameterMapping:

.. title:: Parameter Mapping | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Parameter Landscape Mapping</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Parameter Mapping
======================

.. warning::
   This page is a work in progress and will be updated soon!

Hades' differential evolution approach means that while the program tries to find the lowest cost solution in the full parameter space, it will likely find slightly different solutions close to this global cost minimum each time it is run. 

In the Python version of Hades, we provide a script which performs low-cost parameter landscape mapping. That is, we run many independent Hades optimisations for each case study and extract an entire candidate pool at the last generation of differential evolution in each case. This provides a sample of many thousands of low-cost solutions which when visualised can illustrate the interplay between the cost, amount of fractional crystallisation, and mineral abundances.

As an example, the figure below shows a corner plot of the 5 variables (FC% and four mineral weights) optimised and the cost in the primitive to basic stage optimisation of the :doc:`/case_studies/sao_tome/index` case study. The scatter points represent each of the 12,550 candidates in the final-generation pool across 50 independent Hades optimisations. The bottom row shows each parameter plotted against cost and reveals both how strongly that parameter influences the fit to the São Tomé suite and how well-constrained the optimum is. 

.. figure:: /assets/ParameterMaps/indonesia/2_Primitive-Basic_CornerPlot.png
   :alt: Ontong Java Plateau Primitive to Basic Corner Plot
   :name: corner-plot-indonesia
   :align: center
   :figwidth: 70%
   :width: 90%

   Corner plot of the optimised variables and cost of final-generation candidates across 50 independent differential evolution optimisations of the primitive to basic stage of the São Tomé case study. Scatter points show individual candidates with density contours overlain. The blue cross and dashed lines mark the single best solution across all runs; its values are labelled on the diagonal histograms. Diagonal plots show the marginal distributions for each variable. Off-diagonal panels show pairwise relationships; background shading denotes the correlation coefficient between pairs of variables, as labelled, indicating trade-offs or compensatory behaviour between parameters.

Distinct V-shaped trends indicate a well-defined optimum: cost rises systematically as the parameter moves away from its best value. The steepness of the V reflects the sensitivity of the solution; a steep V as seen for plagioclase and FC% means even small deviations from the optimal value rapidly degrade the fit, showing that the parameter exerts tight control. In contrast, flat or poorly defined (non-V) relationships indicate that a wide range of values produce similarly good solutions, meaning the parameter is weakly constrained and the optimisation landscape is relatively flat in that direction.

Figures like this one are available for each case study on the :doc:`/case_studies/index` page, and the script to generate them is available on GitHub.

.. TODO Add GitHub link once the script is uploaded and documented