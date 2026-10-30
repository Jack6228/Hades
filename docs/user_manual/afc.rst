.. _AFC:

.. title:: AFC Modelling | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Assimilation Fractional Crystallisation</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

AFC Modelling
====================

If we wish to model the inclusion of an assimilant in our system, this can be configured using the 'Assimilant Input' section. Here, we can provide the composition of an assimilant, in major oxides and optionally including trace elements by uploading a file, as well as how much of the melt the assimilant should make up in each phase. Assigning 10% assimilant in the basic to intermediate phase, for example, will ensure that 10% of the melt is replaced with the desired assimilant composition over the course of however much percent of fractional crystallisation is to be performed. 

The 'Load File' button can be used to open an ``.xlsx``, ``.csv`` or ``.txt`` file as with the data suite, however Hades will here load only a single sample for the assimilant, or will select the first sample if more than one is provided in the input file. Upon loading a file, the major oxide element table will be populated, and any trace elements used in the file will be marked in bold. The major oxide elements can be adjusted manually, and are forced to be normalised to 100 wt.% when any model operations are run. 

See the :doc:`Carlingford Igneous Centre case study </case_studies/ireland/index>` for an example of the AFC modelling function in Hades.