# =========================================
# Qmax Tool Core Calculations Module
# =========================================
# Pure mathematical functions for Qmax (maximum axle load) calculations.
# Contains the engineering formula for calculating maximum permissible axle loads.
# No I/O operations, no formatting - just pure calculations.
#
# Purpose: Calculate maximum axle load capacity for rail vehicles
# Used by: qmax service and API endpoints
# Dependencies: constants.py (conversion factors and constants)

from .constants import CONSTANT_C, KN_TO_TONNES  # Qmax constant and unit conversion factor

def calculate_qmax(d: float, sigma_b: float, v_head: float) -> dict:
    """
    Calculate maximum axle load (Qmax) for rail vehicles.

    This function implements the standard engineering formula for calculating
    the maximum permissible axle load based on wheel diameter, rail bending
    stress, and vehicle speed.

    Engineering Formula:
    Qmax = C × (d/2) × (σB / v)²

    Where:
    - Qmax = Maximum axle load (in kN)
    - C = Empirical constant (depends on rail type and conditions)
    - d = Wheel diameter (in meters)
    - σB = Maximum allowable rail bending stress (in MPa)
    - v = Vehicle speed (in km/h)

    The formula ensures that rail bending stress under dynamic loading
    doesn't exceed the allowable limit, preventing rail damage.

    Args:
        d (float): Wheel diameter in meters
        sigma_b (float): Maximum allowable rail bending stress in MPa
        v_head (float): Vehicle speed in km/h

    Returns:
        dict: Calculation results containing:
            - d: Wheel diameter (input)
            - sigma_b: Rail bending stress (input)
            - v_head: Vehicle speed (input)
            - qmax_kn: Maximum axle load in kiloNewtons
            - qmax_tonnes: Maximum axle load in tonnes

    Note:
        The formula assumes standard rail conditions and may need adjustment
        for special rail types, track conditions, or loading scenarios.
    """
    # Calculate Qmax using the engineering formula
    # Qmax = C × (d/2) × (σB / v)²
    qmax_kn = CONSTANT_C * (d / 2) * (sigma_b / v_head) ** 2

    # Convert from kN to tonnes for user-friendly display
    qmax_tonnes = qmax_kn * KN_TO_TONNES

    # Return comprehensive results dictionary
    return {
        "d": d,                    # Wheel diameter (input echo)
        "sigma_b": sigma_b,        # Rail bending stress (input echo)
        "v_head": v_head,          # Vehicle speed (input echo)
        "qmax_kn": qmax_kn,        # Maximum axle load in kN
        "qmax_tonnes": qmax_tonnes # Maximum axle load in tonnes
    }