.. IrelandWalkthrough:

.. title:: Walkthrough | Carlingford, Ireland

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Carlingford Igneous Centre</span>
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

In this example, we demonstrate construction of the major element AFC trends from the Carlingford mafic rocks toward sthe intermediate rocks in its cone sheet complex :cite:t:`meade_bimodal_2014`. Hades is also able to replicate the liquid line of descent for the non-AFC major element fractional crystallisation trend from :cite:t:`furman_petrogenesis_1992` which explains the formation of rhyolitic cone sheet magmas from basaltic rocks in the same cone sheet. This non-AFC trend is covered in the Hades publication and not covered here, though the results and plots for that trend are available in the GitHub repository.

Data Suite
------------

Keeping Hades in its default subalkaline tholeiitic mode, we load the ``carlingford.xlsx`` data suite file. This contains the Carlingford mafic and intermediate rock compositions from :cite:t:`meade_bimodal_2014`. The 'Set Samples' button is used to assign samples 'GM1', 'CB3', and 'C-CS-CR' to the basic, intermediate, and evolved endmembers, with all others set to 'None'. 

----

Mineralogy
----------

We allow Hades to use its default K\ :sub:`D` values. For the basic and intermediate stages, :cite:t:`furman_petrogenesis_1992` shows they can be modelled with an olivine, plagioclase, clinopyroxene, magnetite and ilmenite mineral assemblage (olivine exchanged for orthopyroxene in the intermediate stage) and so we ensure only these minerals are ticked in the 'Phase Compositions' tab of the configuration window (press 'Configure'). For the evolved stage, we only allow plagioclase, K-feldspar, clinopyroxene, ilmenite and magnetite. 

No custom mineral compositions are used in this example, so we keep the default mineral compositions for each stage.

.. rubric:: Assimilant 

In the 'Assimilant Input' section, we can enter the major oxide components of an assimilant, or can use the 'Load Assimilant' button to load a composition from file - with the option of including trace elements. For this example, we load the ``carlingford_assimilant.xlsx`` file which contains the average major element composition of metasiltstones as a possible assimilant :cite:t:`meade_bimodal_2014`.

On the right side of the 'Assimilant Input' section, we enter 50 for the amount of assimilant to be added in the basic and intermediate stages, meaning that over the course of the AFC process in each stage - however much Hades calculates to be the amount of fractional crystallisation - 50% of that amount will be assimilant and 50% will be the bulk mineral assemblage. The evolved stage is kept at 0% assimilant.

----

Running the Model
-----------------

Pressing the 'Run' button for each relevant stage in the 'Mineral Modal Abundances' section will find the optimal bulk mineral assemblage and amount of fractional crystallisation for each stage. Though the Na\ :sub:`2`\ O content is a little high, the modelled LLOD closely matches the expected trend for the introduction of a metasiltstone assimilant into the Carlingford mafic rocks.

.. rubric:: References

.. bibliography::
   :filter: docname in docnames