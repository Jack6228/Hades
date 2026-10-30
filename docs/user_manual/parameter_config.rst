.. _ParameterConfiguration:

.. title:: Parameter Configuration | User Guide

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Parameter Configuration</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>User Guide</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Parameter Configuration
=======================

The various subalkaline and alkaline modes have preset values for a range of variables, which have been taken from literature and theory. However, all such values are able to be edited, to enable prior knowledge of a system to be applied, and to provide more capable modelling. Clicking on the 'Configure' button in the 'Magmatic Data' section provides a pop-up window which enables the configuration of:

- Fe\ :sup:`2+` to FeO ratio: control how Hades converts and interprets iron, and thus how mineral banks are selected from
- K\ :sub:`D` values for all minerals in each phase
- Mineral compositions and presence: the major oxide compositions in each phase, and which minerals are to be included - or not - in a the crystallising assemblage for each phase

The images below show the appearance of these windows, include the default values when launched in the subalkaline, tholeiitic mode. Values can be entered manually, or for the tabular inputs, can be copied and pasted from a spreadsheet or other source. The 'Apply' button must be clicked to save any changes made, and closing the window without applying will discard any changes.

Note that by default, all mineral compositions are empty, as they are automatically obtained from mineral banks - or for olivine, computed from first principles - unless a composition is manually provided.

The 'Load Config' button enables a ``.hades`` file to be loaded which will automatically load a data suite, initial magma composition and all customised values (K\ :sub:`D` values, compositions, etc.) from a previously saved session. See :doc:`/user_manual/config_files` for more information on saving and loading sessions.

.. figure:: /assets/ParamConfig_Geochemistry.png
   :alt: Geochemistry configuration window
   :align: center
   :width: 50%

.. raw:: html

   <br>
   <br>

.. figure:: /assets/ParamConfig_PhaseCompositions.png
   :alt: Mineralogy configuration window
   :align: center
   :width: 50%