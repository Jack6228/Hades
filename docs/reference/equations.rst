.. _TheoryEquations:

.. title:: Petrology & Equations

.. raw:: html

   <section class="hero-section">
      <div class="hero-container">
         <h1 class="hero-title">
            <span class="text-gradient">Petrology & Equations</span>
         </h1>
      <div class="hero-badge">
         <span class="badge-dot"></span>
         <span>Theory</span>
      </div>
      </div>
   </section>

.. rst-class:: hero-title-hidden

Petrology & Equations
=====================

This page provides a detailed overview of the mathematical framework and theoretical principles underlying Hades. It mimics part of the appendices of Hades' correponding publication, but is provided here for convenience. Click on the sections below to expand each topic.

.. dropdown:: Notation and Conventions
   :animate: fade-in
   :icon: info

   This section outlines the mathematical framework for computing the olivine control line in Hades. We adopt standard linear algebra notation, denoting scalars as light-faced italic types :math:`\left(F \in \mathbb{R}\right)`, row vectors as boldface lowercase letters :math:`\left(\mathbf{w} \in \mathbb{R}^{1 \times N}\right)`, and matrices as boldface uppercase letters :math:`\left(\mathbf{C} \in \mathbb{R}^{N \times M}\right)`. Specific rows of a matrix are indexed via a single subscript, such that :math:`\mathbf{C}_i \in \mathbb{R}^{1 \times M}` denotes the :math:`i`-th row vector of :math:`\mathbf{C}`, while individual elements are indexed as :math:`C_{i,j}`.

   To illustrate our convention, the transformation of a vector, :math:`\mathbf{w}`, through a scaling factor, :math:`F`, and a matrix, :math:`\mathbf{C}`, is evaluated via the linear combination :math:`\mathbf{y} = F\mathbf{w}\mathbf{C}`, mapped explicitly as: 
   
   .. math::
      
      \mathbf{y} = F \cdot  \begin{bmatrix}  w_1 & w_2 & \cdots & w_{N}  \end{bmatrix} \begin{bmatrix}  C_{1,1} & C_{1,2} & \cdots & C_{1,M} \\  C_{2,1} & C_{2,2} & \cdots & C_{2,M} \\  \vdots & \vdots & \ddots & \vdots \\  C_{N,1} & C_{N,2} & \cdots & C_{N,M}  \end{bmatrix} = \begin{bmatrix}  y_1 & y_2 & \cdots & y_M  \end{bmatrix}
      
   where the resulting row vector satisfies :math:`\mathbf{y} \in \mathbb{R}^{1 \times M}`.

----

Olivine Control Line Computation
--------------------------------

.. dropdown:: How the Olivine Control Line is Computed
   :animate: fade-in
   :icon: info

   We first denote the melt oxide composition as a function of fractional
   crystallisation as :math:`\mathbf{C} \in \mathbb{R}^{F \times 8}`, where
   :math:`F` is the integer percent of fractional crystallisation to be
   modelled. Our initial magma, :math:`\mathbf{C_0}`, is set following
   conversion from its :math:`\mathrm{Fe_2O_3}` species to
   :math:`\mathrm{Fe}^{3+}` using the Fe2O3-to-FeO and FeO-to-Fe3+ conversion
   equations, denoting

   To construct an olivine control line, we compute equilibrium olivine
   compositions and successively remove 1% increments to generate a liquid
   line of descent. The following steps are repeated for 1% increments,
   :math:`i`, from :math:`0` to :math:`F` %. First, we convert oxide weight
   percentages to normalised cation fractions:

   .. math::

      \mathbf{x} = \Sigma_{100}(\mathbf{C}_i \oslash \mathbf{m})

   where the Hadamard division operator, :math:`\oslash`, denotes
   element-wise division.

   We compute the partition coefficient for olivine,
   :math:`\mathbf{d} \in \mathbb{R}^{1 \times 8}`, by first determining the
   :math:`k_D{_{\mathrm{FeO}/\mathrm{MgO}}^{\text{ol/liq}}}` through the
   Fe-Mg exchange between olivine and the melt using the equations from
   :cite:t:`herzberg_phase_1998`:

   .. math::

      k_D{_{\mathrm{FeO}/\mathrm{MgO}}^{\text{ol/liq}}} = 0.381 -
      \left( \frac{0.79}{\mathbf{C}_{i, \text{MgO}}} \right) +
      \left( \frac{1.039}{\mathbf{C}_{i, \text{MgO}}^2} \right)

   which we define in shorthand as
   :math:`k_D^\prime = k_D{_{\mathrm{FeO}/\mathrm{MgO}}^{\text{ol/liq}}}`.
   This is followed by calculation of the forsterite content,
   :math:`F_\text{o}`, of olivine following
   :cite:t:`roeder_olivine-liquid_1970`:

   .. math::

      F_\text{o} = \frac{1}{\left( k_D^\prime /
      \frac{\mathbf{x}_{i, \text{FeO}}}{\mathbf{x}_{i, \text{MgO}}}
      \right) + 1}

   which is used to compute an updated value for the magnesium component
   of the partition coefficient, which becomes:

   .. math::

      k_D^\prime = \frac{2F_\text{o}}{3\mathbf{x}_{i, \text{MgO}}}

   We can then use empirical relationships from
   :cite:t:`herzberg_plume-associated_2002` to compute remaining components
   of the olivine bulk partition coefficient:

   .. math::

      \mathbf{d}^T =
         \begin{pmatrix}
               0 \\[0.5em]
               0.03 \\[0.5em]
               -0.031 + 0.0035\cdot k_D^\prime + \frac{0.093}{k_D^\prime} \\[0.5em]
               0.263 \cdot k_D^\prime + 0.196 \\[0.5em]
               k_D^\prime \\[0.5em]
               -0.019 + 0.007 \cdot k_D^\prime + \frac{0.063}{k_D^\prime} \\[0.5em]
               0.0001 \\[0.5em]
               0.0001
         \end{pmatrix}

   The olivine cation fraction is then derived by multiplying the cation
   partition coefficients and the melt cation fractions,
   :math:`\mathbf{\mathcal{O}} = \mathbf{d}\odot\mathbf{x}`. Stoichiometric
   balancing is applied to ensure charge balance, computing the
   stoichiometrically balanced olivine vector,
   :math:`\textbf{b} \in \mathbb{R}^{1 \times 8}`, through the two
   octahedral sites, :math:`P_1` and :math:`P_2`:

   .. math::

      P_1 = \frac{1}{2} \left( \mathbf{\mathcal{O}}_\text{Al2O3} -
      \mathbf{\mathcal{O}}_\text{Na2O} - \mathcal{O}_\text{K2O} \right) +
      \mathbf{\mathcal{O}}_\text{FeO} + \mathbf{\mathcal{O}}_\text{MgO} +
      \mathcal{O}_\text{CaO} + 2 \mathbf{\mathcal{O}}_\text{Na2O} +
      2 \mathbf{\mathcal{O}}_\text{K2O}

   .. math::

      \textbf{b}_\text{TiO2} = \frac{2}{3} \frac{\mathbf{\mathcal{O}}_\text{TiO2}}{P_1}
      \quad\quad\quad
      \textbf{b}_\text{Al2O3} = \frac{2}{3} \frac{\mathbf{\mathcal{O}}_\text{Al2O3}}{P_1}
      \quad\quad\quad
      \textbf{b}_\text{CaO} = \frac{2}{3} \frac{\mathbf{\mathcal{O}}_\text{CaO}}{P_1}

   .. math::

      \textbf{b}_\text{Na2O} = \frac{2}{3} \frac{\mathbf{\mathcal{O}}_\text{Na2O}}{P_1}
      \quad\quad\quad
      \textbf{b}_\text{K2O} = \frac{2}{3} \frac{\mathbf{\mathcal{O}}_\text{K2O}}{P_1}

   .. math::

      \textbf{b}_\text{SiO2} = \frac{1}{3} - \textbf{b}_\text{TiO2} -
      \frac{1}{2} \left( \textbf{b}_\text{Al2O3} - \textbf{b}_\text{Na2O} -
      \textbf{b}_\text{K2O} \right)

   .. math::

      P_2 &= \frac{1}{2} \left( \textbf{b}_\text{Al2O3} -
      \textbf{b}_\text{Na2O} - \textbf{b}_\text{K2O} \right) +
      \textbf{b}_\text{CaO} + 2 \textbf{b}_\text{Na2O} +
      2 \textbf{b}_\text{K2O} \\
      &= \frac{1}{2} \textbf{b}_\text{Al2O3} + \textbf{b}_\text{CaO} +
      1.5 \textbf{b}_\text{Na2O} + 1.5 \textbf{b}_\text{K2O}

   .. math::

      \textbf{b}_\text{Fe2O3} = (1 - F_\text{o}) \left( \frac{2}{3} - P_2 \right)

   .. math::

      \textbf{b}_\text{MgO} = F_\text{o} \left( \frac{2}{3} - P_2 \right)

   Having computed :math:`\textbf{b}`, we obtain the olivine composition in
   the FeO basis by multiplying by the oxide molecular compositions:

   .. math::

      \mathbf{\mathcal{O}} = \textbf{b}\odot\mathbf{m}

   To continue for the next percentage point, we update the melt
   composition using mass balance (see Appendix, melt modelling equations),
   which may include addition of an assimilant. The process described
   above is then repeated until the desired amount of fractional
   crystallisation is reached.

   Once the full olivine composition as a function of fractional
   crystallisation is computed, it can be converted from FeO to
   :math:`\mathrm{Fe_2O_3}`.

----

Mineral Bank Selection from Whole-rock Ratios
---------------------------------------------

.. dropdown:: How samples are chosen from mineral banks based on whole-rock ratios
   :animate: fade-in
   :icon: info

   The polymineralic crystallisation computations in Hades are derived in
   this section, following the same notation introduced previously.

   Compositional ranges of potential crystallising minerals are obtained
   from Deer et al. (1992). This latter source is used as it is a common
   text found in any Earth Science department and research institute.
   Hades forms a polymineralic bulk composition to explain an evolving
   liquid line of descent. Silicate minerals have compositional solid
   solution ranges, thus Hades uses mineral :math:`K_\text{D}` values to
   estimate the most appropriate mineral for use in the modelling. For
   example, a basaltic magma crystallising olivine, clinopyroxene and
   plagioclase would not crystallise plagioclase with an albitic
   composition, but would crystallise a bytownite or labradorite. Hades
   therefore uses plagioclase :math:`K_\text{D}` values to attempt to use
   a more calcic plagioclase to model a crystallising basaltic magma.

   For a given initial melt composition, :math:`\mathbf{C}_0`, and
   :math:`K_\text{D}` values for each mineral,
   :math:`\mathbf{d} \in \mathbb{R}^{1 \times M}`, whole-rock partitioning
   ratios are computed for each mineral phase, :math:`M`. Though they can
   be configured within Hades, the default values for :math:`\mathbf{d}`
   at each stage are:

   .. list-table::
      :header-rows: 1

      * - plg
            - cpx
            - opx
            - amph
            - k-f
            - bio
            - tit
            - nep
            - leu
            - n/h
            - rie
      * - 1.2
            - 0.28
            - 0.29
            - 0.37
            - 1.3
            - 1.0
            - 1.0
            - 1.0
            - 1.0
            - 1.0
            - 1.0


   For plagioclase and nepheline, the :math:`\mathrm{Ca}/\mathrm{Na}`
   whole-rock partitioning ratio is computed as:

   .. math::

      \text{WR}_{\mathrm{Ca}/\mathrm{Na}} = \mathbf{d_M} \cdot
      \frac{\mathbf{C}_{0,\text{CaO}} / \mathbf{m}_{\mathrm{CaO}}}
      {\mathbf{C}_{0,\mathrm{Na2O}} / \mathbf{m}_{\mathrm{Na2O}}}

   For clinopyroxene, orthopyroxene, Ca-amphibole, biotite, titanaugite,
   and Na-amphibole:

   .. math::

      \text{WR}_{\mathrm{Fe}/\mathrm{Mg}} = \mathbf{d_M} \cdot
      \frac{\mathbf{C}_{0,\text{FeO}} / \mathbf{m}_{\mathrm{FeO}}}
      {\mathbf{C}_{0,\text{MgO}} / \mathbf{m}_{\mathrm{MgO}}}

   For leucite:

   .. math::

      \text{WR}_{\mathrm{K}/\mathrm{Na}} = \mathbf{d_M} \cdot
      \frac{\mathbf{C}_{0,\mathrm{K2O}} / \mathbf{m}_{\mathrm{K2O}}}
      {\mathbf{C}_{0,\mathrm{Na2O}} / \mathbf{m}_{\mathrm{Na2O}}}

   For nosean/hauyne:

   .. math::

      \text{WR}_\text{K+Ca/Na} = \mathbf{d_M} \cdot
      \frac{(\mathbf{C}_{0,\mathrm{K2O}} / \mathbf{m}_{\mathrm{K2O}}) +
      (\mathbf{C}_{0,\text{CaO}} / \mathbf{m}_{\mathrm{CaO}})}
      {\mathbf{C}_{0,\mathrm{Na2O}} / \mathbf{m}_{\mathrm{Na2O}}}

   These whole-rock ratios are used to find the closest matching mineral
   composition from the mineral banks to the provided :math:`\mathbf{d}`
   value, creating a matrix of mineral compositions,
   :math:`\mathbf{M} \in \mathbb{R}^{M \times 8}`. Fixed-composition
   minerals (e.g., spinel, quartz) are used directly, unless adjusted by
   the user. Olivine is computed uniquely as a function of fractional
   crystallisation as described in Appendix A, unless a custom, fixed
   composition is provided instead.

----

Dynamic Polymineralic Rayleigh Fractional Crystallisation
------------------------------------------------------------

.. dropdown:: Modelling fractional crystallisation with a dynamic olivine composition and many minerals
   :animate: fade-in
   :icon: info

   Once the compositions of all minerals are known from Appendices A and
   B, we use an iterative approach to modelling the melt since the
   olivine composition varies as a function of melt, hence the 'dynamic'
   denotation.

   The bulk partition coefficient, :math:`\mathbf{B} \in \mathbb{R}^{1 \times 8}`,
   is computed as the matrix multiplication of the mineral weights and
   compositions:

   .. math::

      \text{B} = \text{w}\text{M}

   which is inherently normalised provided :math:`\mathbf{w}` and all
   mineral compositions in :math:`\mathbf{M}` are normalised. We use this
   to update the melt composition at each percentage point, :math:`i`, by
   subtracting the mass of crystallised minerals from the previous
   percentage point and correct for its removal using a mass balance
   factor:

   .. math::
      :label: eq-melt-modelling

      \mathbf{C_i} = \frac{F_p\mathbf{C}_{i-1} - \mathbf{B}_i}{F_c}

   where :math:`F_p` and :math:`F_c` represent the melt fraction before
   and after crystallisation at the current percentage point, :math:`i`,
   such that :math:`\Delta F = F_c - F_p = 0.01`:

   .. math::

      F_p = 1 - \frac{i-1}{100} \quad\quad\quad F_c = 1 - \frac{i}{100}

   If an assimilant of composition :math:`\mathbf{A} \in \mathbb{R}^{1 \times 8}`
   is added to the system, we instead use a modified version of
   :eq:`eq-melt-modelling` to account for addition of an assimilant. If
   :math:`a` % of this assimilant is to be added over the :math:`F` %
   fractional crystallisation, :eq:`eq-melt-modelling` is re-written as:

   .. math::
      :label: eq-melt-modelling-w-assimilant

      \mathbf{C}_i = \frac{F_p\mathbf{C}_{i-1} - \mathbf{B}_i}{F_c}
      \left(1 - a^\prime\right) + a^\prime\mathbf{A}

   where :math:`a^\prime = a/F` represents the amount of melt to be added
   at each step of fractional crystallisation.

----

Trace Element Modelling
--------------------------

.. dropdown:: Computing trace element abundances during fractional crystallisation
   :animate: fade-in
   :icon: info

   Hades considers only major oxide compositions to model mineral
   abundances during fractional crystallisation. To compute the same
   processes for trace elements, we do one of two processes depending on
   if trace elements are structural components of the melt. This is
   determined based on the user's selection of accessory mineral weights
   for apatite, zircon, monazite and allanite.

   For major oxides and 'structural trace elements', we re-model melt as
   shown in :eq:`eq-melt-modelling`-:eq:`eq-melt-modelling-w-assimilant`,
   now accounting for the addition of accessory minerals to the
   polymineralic bulk composition. However, this modelling is
   non-dynamic, that is, we use the olivine composition computed for the
   final stage of fractional crystallisation instead of varying it
   through time.

   For trace elements, denoted by :math:`T`, with no structural
   contributions, we use a databank of :math:`K_\text{D}` values,
   :math:`\mathbf{K} \in \mathbb{R}^{M \times T}` in addition to Hades'
   optimised solution to model melt. The bulk mineralogy is computed from
   the :math:`K_\text{D}` values as:

   .. math::

      \mathbf{B} = \mathbf{w}\mathbf{K}

   We then use De Paolo's melt equation, again under the assumption of
   non-dynamic olivine compositions:

   .. math::

      \mathbf{C} = \mathbf{C_0} \left[F^{-\mathbf{Z}} +
      \left(\frac{a}{a-1}\right)\cdot\frac{\mathbf{A}}{\mathbf{Z}\mathbf{C_0}}
      \cdot\left(1-F^{-\mathbf{Z}}\right)\right]

   .. math::

      \mathbf{C}_t = \mathbf{C}_0 \odot \left[ F^{-\mathbf{Z}} +
      \left(\frac{a}{a-1}\right) \odot \Big( \mathbf{A} \oslash
      (\mathbf{Z} \odot \mathbf{C}_0) \Big) \odot
      \left(1 - F^{-\mathbf{Z}}\right) \right]

   where

   .. math::

      \mathbf{Z} = \frac{a+(\mathbf{B}-1)}{a-1}

   and :math:`F^{-\mathbf{Z}}` denotes the element-wise exponentiation of
   the scalar :math:`F`.

----

.. rubric:: References

.. bibliography::
   :filter: docname in docnames