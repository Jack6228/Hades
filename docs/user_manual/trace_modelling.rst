.. _TraceModelling:

.. title:: Trace Modelling | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Trace Modelling</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Trace Modelling
====================

Once the optimal parameters have been acquired (or manually provided) to produce a satisfactory LLOD, the 'Trace Elements' button can be clicked up bring up a window to include accessory minerals (Apatite, Zircon, Monazite, Allanite) in the fractionally crystallising system.

The trace element analysis function uses the mineral abundances and percentages of FC from the main window's 'Mineral Modal Abundances' table, as well as any other parameters set (K\ :sub:`D` values, mineral compositions, etc.). Furthermore, the K\ :sub:`D` Values' tab in this trace element window enables you to customise the K\ :sub:`D` values for the trace elements of each mineral, though default values from literature are provided, where available. 

To run the trace element analysis, you can input a wt.% of each accessory mineral for the first phase of interest and click 'View'. This will rebalance the mineral abundances with your selection of accessory minerals and run a FC model under the same conditions as specified in the main window.

Trace modelling can be run for each phase sequentially, though note that subsequent phases continue from the LLOD produced by the previous phase. This means that the optimal solution found in the main window may not remain the optimal solution following the addition of accessory minerals, however, we believe that this trace element analysis function provides an easy way to understand the extent to which these accessory minerals contribute to fractional crystallisation of your data suite, and under which conditions. 

The drop-down cell below the instructions enables you to select the y-axis variable of the final Harker SiO2 diagrams, with the first seven reserved for those traces which may be structural components of the melt.

Clicking the 'Save & Close' button will save the trace element modelling results separately and close the pop-up window. Exporting the data from the main window using the 'Export Data' or 'Export PDF' buttons (see :doc:`/user_manual/exporting`) after this will ensure that these results are exported. If the program is reset or a new round of modelling in the main Hades window is started, the trace element results are wiped from memory.

.. figure:: /assets/TraceModelling.png
   :alt: Trace modelling window
   :align: center
   :width: 70%