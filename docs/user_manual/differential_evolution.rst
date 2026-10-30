.. _DiffEv:

.. title:: Differential Evolution | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Differential Evolution</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Differential Evolution
======================

.. warning::
   This page is a work in progress and will be updated soon!

Determining the percentage of fractional crystallisation and the mineral contributions of the bulk modal crystallising mineral assemblage required to generate a liquid line of descent to satisfactorily explain the evolution of a suite of data is an optimisation problem. Such optimisation problems iteratively adjust input parameters (e.g., various mineral proportions) to minimise a 'cost' function, which in our case is the difference between the modelled and expected melt compositions.

Differential evolution (DE) is a derivative-free, population-based global search method which uses arithmetic on a set of candidate solutions to iteratively improve them, 'evolving' towards an optimal solution. Because it is stochastic, DE can explore broad regions of parameter space and is less likely to get stuck (e.g., :cite:t:`storn_differential_1997`; :cite:t:`das_differential_2011`).

.. rubric:: References

.. bibliography::
   :filter: docname in docnames
   