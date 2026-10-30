"""Numba-compiled versions of the phase functions for Hades.

When run, the produced .pyd file should be copied into the hades/ directory to be the preferred 'vectorised_phases' module used by Hades for optimised performance.
"""

from numba import jit, njit, prange
from numba.pycc import CC
import numpy as np
cc = CC('phases')

@jit(nopython=True, cache=True)
@cc.export('compute_cost', 'f8[:](f8[:,:], f8[:])')
def compute_cost(computed: np.ndarray, expected: np.ndarray) -> np.ndarray:
    """
    Finds sum of absolute differences between computed and expected compositions.

    Parameters
    ----------
    computed : np.ndarray
        Computed compositions, shape (N, 8)
    expected : np.ndarray
        Expected compositions, shape (8,)

    Returns
    -------
    np.ndarray
        Array of costs for each computed composition, shape (N,)
    """
    # Scale down the massive oxides so everyone plays on a level field, but keep the math purely linear for Differential Evolution.
    weights = 1.0 / np.sqrt(expected + 1e-5) 
    return np.sum(np.abs(computed - expected) * weights, axis=1)

@jit(nopython=True, cache=True)
@cc.export('lookup_mineral_bank_cotectic', 'f8[:](f8, f8[:,:])')
def lookup_mineral_bank_cotectic(WR_val: float, min_bank: np.ndarray) -> np.ndarray:
    """
    Performs a batch lookup for an WR value against a mineral bank, returning the corresponding cotectic compositions.

    Assumes that the last row of the mineral bank contains the WR values sorted in ascending order, and that the cotectic compositions are in the rows above. For each WR value, it finds the appropriate column in the mineral bank where that WR value would fit and retrieves the corresponding cotectic composition.

    Parameters
    ----------
    WR_val : float
        A WR value to look up in the mineral bank
    min_bank : np.ndarray
        Mineral bank array, shape (8, M) where the last row (index 7) contains sorted WR values and the rows above contain cotectic compositions.

    Returns
    -------
    out : np.ndarray
        Array of cotectic compositions retrieved from the mineral bank for each WR value, shape (N, 8)
    """
    # For each WR value, find the appropriate column in the mineral bank and retrieve the cotectic composition
    last_row = min_bank[-1]
    idx = np.searchsorted(last_row, WR_val, side='right')
    if idx >= last_row.size:
        idx = last_row.size - 1
    # Extract the major oxides (not the WR in the last row)
    out = min_bank[:8, idx]
    return out

@njit(cache=True, fastmath=True)
@cc.export('mass_balance_step', 'f8[:,:](f8[:,:], f8[:,:], f8[:], f8)')
def mass_balance_step(C_, Bt_all, A, Apct):
    """
    JIT-compiled sequential loop for maximum speed.

    Parameters
    ----------
    C_ : np.ndarray
        Pre-allocated array for compositions, shape (F+1, 8)
    Bt_all : np.ndarray
        Pre-computed bulk compositions for each step, shape (F, 8)
    A : np.ndarray
        Assimilant composition, shape (8,)
    Apct : float
        Percentage of assimilant to be added during the mass balance process

    Returns
    -------
    np.ndarray
        Updated compositions after mass balance, shape (F+1, 8)
    """
    
    ## Pre-calculate constants outside the loop to save operations
    # Convert Apct to a decimal
    Apct = Apct * 0.01
    # Divide Apct by C_.shape[0] - 1 (F) to get the per-step assimilation fraction, avoiding divide by zero
    denom = C_.shape[0] - 1
    if denom <= 0:
        denom = 1
    Apct = Apct / denom
    # Constants
    one_minus_apct = (100.0 - Apct)
    a_times_apct = A * Apct
    needs_assim = Apct > 0.0
    
    for i in range(1, C_.shape[0]):
        F_prev = (101 - i) / 100.0
        F_current = (100 - i) / 100.0
        
        # Core mass balance step
        C_[i] = (C_[i-1] * F_prev - Bt_all[i-1] * 0.01) / F_current

        # Add assimilant and renormalise (avoiding divide by 0)
        if needs_assim:
            C_[i] = (C_[i] * one_minus_apct) + a_times_apct
            C_sum = np.sum(C_[i])
            C_[i] = C_[i] * (100.0 / C_sum) if C_sum != 0.0 else C_[i]

    return C_

@njit(cache=True, fastmath=True)
@cc.export('calculate_melt_evolution', 'f8[:,:](f8[:], f8[:,:], f8[:], f8[:], i4, f8[:], f8)')
def calculate_melt_evolution(C, M, Molv, W, F, A, Apct):
    """
    Optimized DRF variant that pre-computes the bulk composition for each step and uses a JIT-compiled inner loop for maximum speed.

    Parameters
    ----------  
    C : np.ndarray
        Initial composition of the melt, shape (8,)
    M : np.ndarray
        Cotectic compositions for each phase, shape (M, 8) where M is the number of minerals
    Molv : np.ndarray
        Olivine cotectic composition, shape (8,)
    W : np.ndarray
        Mineral weights for each phase, shape (M+1,) where the first element is the weight of olivine and the rest correspond to the other minerals
    F : int
        Number of steps to perform in the mass balance process
    A : np.ndarray
        Assimilant composition, shape (8,)
    Apct : float
        Percentage of assimilant to be added during the mass balance process

    Returns
    -------
    np.ndarray
        Updated compositions after mass balance, shape (F+1, 8)
    """
    # Pre-allocate array with initial composition
    C_ = np.zeros((F+1, C.shape[0]), dtype=np.float64)
    C_[0] = C

    # vectorised bulk composition setup
    Br = W[1:] @ M[1:]
    Bt_all = Br + (W[0] * Molv)  # Shape (99, 8) pre-calculated
    
    # Run the blazing fast compiled loop
    return mass_balance_step(C_, Bt_all, A, Apct)

@njit(cache=True, fastmath=True)
@cc.export('compute_olivine_composition', 'f8[:,:](f8[:], f8[:], f8[:,:], i4, f8[:], f8, f8, f8, f8[:])')
def compute_olivine_composition(C, W, M, F, A, Apct, Fe2O3_FeO_Ratio, FeO_Fe2pO_Ratio, molecular_weights):
    """
    Computes the olivine composition evolution over F steps, taking into account assimilation and mass balance.

    Parameters  
    ----------
    C : np.ndarray
        Initial composition of the melt, shape (8,)
    W : np.ndarray
        Mineral weights for each phase, shape (M+1,) where the first element is the weight of olivine and the rest correspond to the other minerals
    M : np.ndarray
        Cotectic compositions for each phase, shape (M, 8) where M is the number of minerals
    F : int
        Number of steps to perform in the mass balance process
    A : np.ndarray
        Assimilant composition, shape (8,)
    Apct : float
        Percentage of assimilant to be added during the mass balance process
    Fe2O3_FeO_Ratio : float
        Conversion ratio from Fe2O3 to FeO
    FeO_Fe2pO_Ratio : float
        Conversion ratio from FeO to Fe2+
    molecular_weights : np.ndarray
        Molecular weights of the oxides, shape (8,)

    Returns
    -------
    np.ndarray
        Olivine composition evolution over F steps, shape (F, 8)
    """
    ncomp = 8
    nsteps = F

    ## Pre-calculate constants outside the loop to save operations
    # Convert Apct to a decimal
    Apct = Apct * 0.01
    # Divide Apct by F to get the per-step assimilation fraction
    Apct = Apct / (F)
    # Constants
    one_minus_apct = (100.0 - Apct)
    a_times_apct = A * Apct
    needs_assim = Apct > 0.0

    # Make local copies as float64
    C_FeO = np.empty(ncomp, dtype=np.float64)
    Wn = np.empty(W.shape[0], dtype=np.float64)
    Mn = np.empty_like(M, dtype=np.float64)
    mw = np.empty(ncomp, dtype=np.float64)

    for i in range(ncomp):
        C_FeO[i] = C[i]
        mw[i] = molecular_weights[i]

    # Normalise W
    wsum = 0.0
    for i in range(Wn.shape[0]):
        Wn[i] = W[i]
        wsum += W[i]
    inv_wsum = 1.0 / wsum
    for i in range(Wn.shape[0]):
        Wn[i] *= inv_wsum

    # C Fe2O3 -> FeO -> Fe2+
    C_FeO[3] = C_FeO[3] * Fe2O3_FeO_Ratio * FeO_Fe2pO_Ratio
    csum = 0.0
    for i in range(ncomp):
        csum += C_FeO[i]
    inv_csum = 100.0 / csum
    for i in range(ncomp):
        C_FeO[i] *= inv_csum

    # M -> FeO basis and row-normalise
    for i in range(Mn.shape[0]):
        for j in range(ncomp):
            Mn[i, j] = M[i, j]
        Mn[i, 3] = Mn[i, 3] * Fe2O3_FeO_Ratio

    for i in range(Mn.shape[0]):
        rs = 0.0
        for j in range(ncomp):
            rs += Mn[i, j]
        inv_rs = 100.0 / rs if rs != 0.0 else 0.0
        for j in range(ncomp):
            x = Mn[i, j] * inv_rs
            # manual nan_to_num
            if not np.isfinite(x):
                x = 0.0
            Mn[i, j] = x

    # Precompute Br_FeO
    Br_FeO = np.zeros(ncomp, dtype=np.float64)
    for j in range(1, Wn.shape[0]):
        wj = Wn[j]
        for i in range(ncomp):
            Br_FeO[i] += wj * Mn[j, i]

    # Buffers
    olvFeO = np.zeros((nsteps, ncomp), dtype=np.float64)
    bop = np.zeros(ncomp, dtype=np.float64)
    catD = np.zeros(ncomp, dtype=np.float64)
    catD[1] = 0.03
    catD[6] = 1e-4
    catD[7] = 1e-4

    cation_frac = np.zeros(ncomp, dtype=np.float64)
    cation_pct = np.zeros(ncomp, dtype=np.float64)
    olivine_comp = np.zeros(ncomp, dtype=np.float64)
    bop_mw = np.zeros(ncomp, dtype=np.float64)
    F1 = np.zeros(ncomp, dtype=np.float64)
    prevF1 = np.zeros(ncomp, dtype=np.float64)
    mw_inv = np.zeros(ncomp, dtype=np.float64)

    for i in range(ncomp):
        mw_inv[i] = 1.0 / mw[i]

    W0 = Wn[0] if Wn.shape[0] > 0 else 0.0
    step_done = 0

    for pct in range(1, nsteps + 1):
        # cation fractions
        s = 0.0
        for i in range(ncomp):
            cation_frac[i] = C_FeO[i] * mw_inv[i]
            s += cation_frac[i]
        inv_s = 1.0 / s if s != 0.0 else 0.0
        for i in range(ncomp):
            cation_pct[i] = cation_frac[i] * inv_s

        MgO_wt = C_FeO[4]
        if MgO_wt <= 0.0:
            break
        KD = 0.381 - (0.79 / MgO_wt) + (1.039 / (MgO_wt * MgO_wt))
        ratio_FeMg = cation_frac[3] / cation_frac[4] if cation_frac[4] != 0.0 else 1e300
        Fo = 1.0 / (KD * ratio_FeMg + 1.0)
        Mg_in_olivine = Fo * (2.0 / 3.0)
        DMg = Mg_in_olivine / cation_pct[4] if cation_pct[4] != 0.0 else 0.0

        catD[2] = ((-0.031) + 0.0035 * DMg + (0.093 / DMg)) if DMg != 0.0 else 0.0
        catD[3] = 0.263 * DMg + 0.196
        catD[4] = DMg
        catD[5] = ((-0.019) + 0.0071 * DMg + (0.063 / DMg)) if DMg != 0.0 else 0.0

        for i in range(ncomp):
            olivine_comp[i] = catD[i] * cation_pct[i]

        bop[0] = bop[1] = bop[2] = bop[3] = bop[4] = bop[5] = bop[6] = bop[7] = 0.0

        oct_part1 = 1.0 / (0.5 * (olivine_comp[2] - olivine_comp[6] - olivine_comp[7])
                           + olivine_comp[3] + olivine_comp[4] + olivine_comp[5]
                           + 2.0 * olivine_comp[6] + 2.0 * olivine_comp[7])
        t23 = 2.0 / 3.0
        bop[1] = olivine_comp[1] * t23 * oct_part1
        bop[2] = olivine_comp[2] * t23 * oct_part1
        bop[5] = olivine_comp[5] * t23 * oct_part1
        bop[6] = olivine_comp[6] * t23 * oct_part1
        bop[7] = olivine_comp[7] * t23 * oct_part1
        bop[0] = (1.0 / 3.0) - bop[1] - 0.5 * (bop[2] - bop[6] - bop[7])

        oct_part2 = 0.5 * (bop[2] - bop[6] - bop[7]) + bop[5] + 2.0 * bop[6] + 2.0 * bop[7]
        bop[3] = (1.0 - Fo) * (t23 - oct_part2)
        bop[4] = Fo * (t23 - oct_part2)

        s_bop = 0.0
        for i in range(ncomp):
            bop_mw[i] = bop[i] * mw[i]
            s_bop += bop_mw[i]
        inv_s_bop = 100.0 / s_bop if s_bop != 0.0 else 0.0
        for i in range(ncomp):
            F1[i] = bop_mw[i] * inv_s_bop

        # TODO [Future Option] Could add a similar mechanism for stopping olivine computation early if it diverges
        # Trial implementation had low values causing premature stopping, hence the very high 500 thresrhold
        # Only really affects computational time, not accuracy, so not a priority 
        # if pct > 1:
        #     diff = 0.0
        #     for i in range(ncomp):
        #         # d = F1[i] - prevF1[i]
        #         d = (abs(F1[i] - prevF1[i]) / prevF1[i]) * 100
        #         if d < 0: d = -d
        #         diff += d
        #     if diff > 50.0:
        #         break

        # Stop before recording this step if any component changes by more than 1 wt.% from the previous pct step. The first step has no comparison.
        if pct > 1:
            diverged = False
            for i in range(ncomp):
                if abs(F1[i] - prevF1[i]) > 1.0:
                    diverged = True
                    # print(f"Olivine composition diverged at step {pct} for component {i}: {F1[i]} vs {prevF1[i]}")
                    break
            if diverged:
                # Keep the last non-divergent composition for this and all
                # remaining requested steps rather than leaving them as zero.
                for r in range(pct - 1, nsteps):
                    for i in range(ncomp):
                        olvFeO[r, i] = prevF1[i]
                step_done = nsteps
                break  # Stop calculating once divergence is detected

        for i in range(ncomp):
            prevF1[i] = F1[i]

        # B = W0 * F1 + Br_FeO
        F_prv = 1.0 - (pct - 1) * 0.01
        F_crt = 1.0 - pct * 0.01
        for i in range(ncomp):
            C_FeO[i] = (C_FeO[i] * F_prv - (W0 * F1[i] + Br_FeO[i]) * 0.01) / F_crt
            if needs_assim:
                C_FeO[i] = (C_FeO[i] * one_minus_apct + a_times_apct[i])  # Assimilation step
                # Renormalise to 100%
                s_c = 0.0
                for j in range(ncomp):
                    s_c += C_FeO[j]
                inv_s_c = 100.0 / s_c if s_c != 0.0 else 0.0
                for j in range(ncomp):
                    C_FeO[j] *= inv_s_c

        for i in range(ncomp):
            olvFeO[pct - 1, i] = F1[i]
        step_done = pct

    # Convert to Fe2O3 basis
    for r in range(step_done):
        olvFeO[r, 3] /= Fe2O3_FeO_Ratio
        s = 0.0
        for j in range(ncomp):
            s += olvFeO[r, j]
        if s != 0.0:
            inv_s = 100.0 / s
            for j in range(ncomp):
                olvFeO[r, j] *= inv_s
        else:
            for j in range(ncomp):
                # sanitize (shouldn't happen)
                if not np.isfinite(olvFeO[r, j]):
                    olvFeO[r, j] = 0.0

    return olvFeO

# Note: It MUST accept the 2D array from SciPy and return a 1D array of scores.
@njit(parallel=False, cache=True, fastmath=True)
@cc.export('compute_phase_evolution_batch', 'Tuple((f8[:,:], f8[:,:], f8[:,:]))(f8[:,:], f8[:], f8[:,:], f8[:], f8, f8, f8, f8[:])')
def compute_phase_evolution_batch(params: np.ndarray, init_comp: np.ndarray, cotectics, assimilant, assimilant_pct, Fe2O3_FeO_Ratio, FeO_Fe2pO_Ratio, molecular_weights) -> tuple[np.ndarray, np.ndarray]:
    """
    A vectorised version of the big phase function that accepts a batch of candidate parameters and returns the computed compositions for each candidate.

    Parameters
    ----------
    params : np.ndarray
        Array of parameters for each candidate, shape (M+1, N) where N is the number of candidates and M is the number of mineral weights; + 1 (for F_mode).
    init_comp : np.ndarray
        Initial composition of the melt, shape (8,)
    cotectics : np.ndarray
        Cotectic compositions for each phase, shape (M, 8) where M is the number of minerals
    assimilant : np.ndarray
        Assimilant composition, shape (8,)  
    assimilant_pct : float
        Percentage of assimilant to be added during the mass balance process

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        A tuple containing:
        - Array of computed compositions for each candidate, shape (N, 8)
        - Array of final compositions after all steps for the last candidate, shape (F+1, 8)
    """
    params = np.atleast_2d(params)

    # Extract parameters and set up arrays
    N = params.shape[0]
    F_mode = params[:, 0]
    mineral_weights = params[:, 1:]
    # Normalise mineral_weights for each candidate, avoiding divide by zero
    row_sums = np.sum(mineral_weights, axis=1)
    for i in range(N):
        mineral_weights[i, :] /= row_sums[i] if row_sums[i] != 0 else 1.0

    C1 = init_comp.copy()
    W = mineral_weights.copy()
    F = mineral_weights[:, 0]
    M = cotectics.copy()
    F = (F_mode * 100).astype(np.int64)

    compute_olivine = True
    # If a custom composition is passed (i.e. the composition is not the default 0), we don't need to compute olivine and use this fixed composition
    if M[0].sum() != 0.:
        # print("Using custom olivine composition from cotectics.")
        compute_olivine = False

    # Pre-allocate the output array for SciPy (must be shape (S,))
    Noxides = C1.shape[0]
    C_arr = np.zeros((N, Noxides), dtype=np.float64)
    # Initialise C and Molv to avoid unbound local variable errors in the loop below
    C = None
    Molv = None

    for i in prange(N):

        # Extract mineral weights and FC% for this candidate
        W_, F_ = W[i], F[i]

        # If F_ is 0, skip and just return the initial composition
        if F_ == 0:
            C_arr[i] = C1[F_]
            continue

        # If we need to compute olivine, do so; otherwise, use the provided composition broadcast to a 2D array of shape (F_, 8)

        # If the olivine weight is 0, we don't need to compute olivine and can skip to the next candidate
        if W_[0] == 0.:
            # print(f"Candidate {i}: Olivine weight is 0, skipping olivine computation.")
            Molv = np.zeros((F_, Noxides), dtype=np.float64)
        elif compute_olivine:
            # print("Computing olivine")
            # Compute dynamic olivine composition for this candidate
            Molv = compute_olivine_composition(
                C1, W_, M, F_, assimilant, assimilant_pct,
                Fe2O3_FeO_Ratio, FeO_Fe2pO_Ratio, 
                molecular_weights
            )
            # Pad back to all geochemistry
            olv = np.zeros((F_, Noxides), dtype=np.float64)
            olv[:, :Molv.shape[1]] = Molv  # Copy the original array into the left section
            Molv = olv
        else:
            # Broadcast the provided olivine composition to a 2D array of shape (F_, 8)
            # print("Broadcasting provided olivine composition")
            Molv = np.zeros((F_, M[0].shape[0])) + M[0]
        # print(Molv.shape)
        
        C = calculate_melt_evolution(C1, M, Molv, W_, F_, assimilant, assimilant_pct)

        # Store the final composition after all steps
        C_arr[i] = C[F_]  
        
    # Return C_arr: the final composition for all candidates
    # Return C: the full composition evolution of the last candidate - this is only ever used when running a single candidate, not vectorisation, so only the last (only) is needed.
    # Return Molv: the olivine composition evolution of the last candidate - this is only ever used when running a single candidate, not vectorisation, so only the last (only) is needed.
    return C_arr, C, Molv

@jit(nopython=True, cache=True)
@cc.export('compute_phase_cost_batch', 'f8[:](f8[:,:], f8[:], f8[:], f8[:,:], f8[:], f8, f8, f8, f8[:])')
def compute_phase_cost_batch(params: np.ndarray, init_comp: np.ndarray, exp_comp: np.ndarray, cotectics, assimilant, assimilant_pct, Fe2O3_FeO_Ratio, FeO_Fe2pO_Ratio, molecular_weights) -> np.ndarray:
    """
    Wrapper which performs mass balance using the `compute_phase_evolution_batch` function and then computes the cost for each candidate against the expected composition. This function is used as the objective function for differential optimisation.

    Parameters
    ----------
    params : np.ndarray
        Array of parameters for each candidate, shape (M+1, N) where N is the number of candidates and M is the number of mineral weights; + 1 (for F_mode).
    init_comp : np.ndarray
        Initial composition of the melt, shape (8,)
    exp_comp : np.ndarray
        Expected composition to compare against, shape (8,)
    cotectics : np.ndarray
        Cotectic compositions for each phase, shape (M, 8) where M is the number of minerals
    assimilant : np.ndarray
        Assimilant composition, shape (8,)
    assimilant_pct : float
        Percentage of assimilant to be added during the mass balance process
    phase : int
        Phase number (1-5) indicating which phase calculation to perform

    Returns
    -------
    np.ndarray
        Array of costs for each candidate, shape (N,)
    """
    # Compute the phase evolution, discarding unused outputs and return the cost for all candidates
    result_p3, _, _ = compute_phase_evolution_batch(params.T, init_comp, cotectics, assimilant, assimilant_pct, Fe2O3_FeO_Ratio, FeO_Fe2pO_Ratio, molecular_weights)
    return compute_cost(result_p3, exp_comp)

if __name__ == "__main__":
    cc.compile()

# Usage:
# To compile this file into a .pyd file, run the following command in the terminal:
# python -m phases_precomp.py
# The generated .pyd file will take preference over the original .py file when imported, providing optimized performance.