# =========================================
# Tractive Effort Tool Core Calculations Module
# =========================================
# Pure mathematical functions for calculating train tractive effort requirements.
# Contains physics-based calculations for rolling resistance, gradient resistance,
# curvature resistance, and electrical power requirements.
#
# Purpose: Calculate the force required to move a train and the electrical power
#          needed from overhead electric (OHE) lines.
# Used by: tractive_effort service and API endpoints
# Dependencies: constants.py (resistance coefficients and electrical constants)

import math  # For trigonometric functions (gradient calculations)
from typing import Dict, Any, Optional  # Type hints for better code documentation
from .constants import (
    WAGON_ROLLING_RESISTANCE_START, LOCO_ROLLING_RESISTANCE_START,
    WAGON_ROLLING_RESISTANCE_RUNNING, LOCO_ROLLING_RESISTANCE_RUNNING,
    POWER_CONSTANT, OHE_VOLTAGE, OHE_EFFICIENCY, POWER_FACTOR, CURRENT_CONSTANT,
    GRADIENT_CONSTANT, CURVATURE_CONSTANT
)

def calculate_gradient_resistance(gradient: float, grad_type: str) -> float:
    """
    Calculate gradient (slope) resistance per tonne of train weight.

    Gradient resistance is the additional force required to move a train uphill.
    The calculation differs based on how the gradient is specified.

    Args:
        gradient (float): Gradient value
        grad_type (str): How gradient is specified ("Degree" or "1 in G")

    Returns:
        float: Gradient resistance in kg/tonne (force per tonne)

    Physics:
        - Degree: Uses tan(θ) where θ is the angle in degrees
        - 1 in G: Direct ratio (rise/run) - steeper when G is smaller
        - Formula: Resistance = sin(θ) × 1000 kg/tonne (approximated)

    Examples:
        - 1 degree: ~17.4 kg/tonne
        - 1 in 100: 10 kg/tonne
        - 1 in 50: 20 kg/tonne
    """
    if grad_type == "Degree":
        # Convert degrees to radians, then use tangent (approximation for small angles)
        return math.tan(math.radians(gradient)) * GRADIENT_CONSTANT if gradient != 0 else 0
    else:  # "1 in G" format
        # Direct ratio: 1/G gives the gradient ratio
        return GRADIENT_CONSTANT / gradient if gradient != 0 else 0

def calculate_curvature_resistance(curvature: float, curvature_unit: str) -> float:
    """
    Calculate curvature (curve) resistance per tonne of train weight.

    Curvature resistance is the additional force required to negotiate curves
    due to the longer path traveled by outer wheels and flange friction.

    Args:
        curvature (float): Curvature value
        curvature_unit (str): Unit of curvature ("Radius(m)" or "Degree")

    Returns:
        float: Curvature resistance in kg/tonne

    Physics:
        - Radius(m): Resistance ∝ 1/R (tighter curves = higher resistance)
        - Degree: Direct degree value (empirical relationship)
        - Typical values: 5-15 kg/tonne for normal railway curves

    Note:
        Curvature resistance increases as curve radius decreases (tighter curves)
    """
    if curvature_unit == "Radius(m)":
        # Resistance inversely proportional to radius
        return CURVATURE_CONSTANT / curvature if curvature != 0 else 0
    else:  # "Degree"
        # Direct degree value (empirical)
        return curvature

def get_rolling_resistances(mode: str) -> tuple[float, float, Optional[float]]:
    """
    Get rolling resistance coefficients for wagons and locomotives.

    Rolling resistance is the force required to overcome bearing friction,
    wheel deformation, and track irregularities when starting or running.

    Args:
        mode (str): Operating mode ("Start" or "Running")

    Returns:
        tuple[float, float, float]:
            - wagon_rr: Rolling resistance for wagons (kg/tonne)
            - loco_rr: Rolling resistance for locomotive (kg/tonne)
            - speed_for_power: Speed for power calculation (km/h), or None if to be provided separately

    Physics:
        - Starting resistance > Running resistance (static vs dynamic friction)
        - Locomotive resistance > Wagon resistance (different wheel designs)
        - Typical values: Start: 8-12 kg/tonne, Running: 2-5 kg/tonne
    """
    if mode == "Start":
        # Higher resistance when starting from rest
        return WAGON_ROLLING_RESISTANCE_START, LOCO_ROLLING_RESISTANCE_START, 1.0
    else:  # "Running"
        # Lower resistance when already moving
        return WAGON_ROLLING_RESISTANCE_RUNNING, LOCO_ROLLING_RESISTANCE_RUNNING, None  # speed will be passed separately

def calculate_resistance_components(inputs: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate all resistance components (T1, T2, T3, T4) for tractive effort.

    This function computes the four main resistance components that a locomotive
    must overcome to move a train:

    T1: Wagon rolling resistance
    T2: Locomotive rolling resistance
    T3: Gradient resistance
    T4: Curvature resistance

    Args:
        inputs (Dict[str, Any]): Input parameters including:
            - load: Wagon load in tonnes
            - loco_weight: Locomotive weight in tonnes
            - gradient, grad_type: Slope parameters
            - curvature, curvature_unit: Curve parameters
            - mode: "Start" or "Running"
            - speed: Train speed (for running mode)

    Returns:
        Dict[str, float]: Resistance components and speed for power calculation:
            - T1: Wagon rolling resistance (kg)
            - T2: Locomotive rolling resistance (kg)
            - T3: Gradient resistance (kg)
            - T4: Curvature resistance (kg)
            - speed_for_power: Speed in km/h for power calculations

    Physics:
        Total resistance = Σ(resistance_per_tonne × weight)
        All resistances are in kg (force units)
    """
    load = inputs['load']  # Wagon load in tonnes
    loco_weight = inputs['loco_weight']  # Locomotive weight in tonnes
    total_weight = load + loco_weight  # Total train weight

    # Calculate gradient and curvature resistances (per tonne)
    gradient_resistance_per_ton = calculate_gradient_resistance(inputs['gradient'], inputs['grad_type'])
    curvature_resistance_per_ton = calculate_curvature_resistance(inputs['curvature'], inputs['curvature_unit'])

    # Get rolling resistance coefficients
    wagon_rr, loco_rr, speed_for_power = get_rolling_resistances(inputs['mode'])
    if speed_for_power is None:  # Running mode - use provided speed
        speed_for_power = inputs['speed']

    # Calculate individual resistance components (in kg)
    T1 = load * wagon_rr  # Wagon rolling resistance
    T2 = loco_weight * loco_rr  # Locomotive rolling resistance
    T3 = total_weight * gradient_resistance_per_ton  # Gradient resistance
    T4 = total_weight * curvature_resistance_per_ton  # Curvature resistance

    return {
        'T1': T1,  # Wagon rolling resistance (kg)
        'T2': T2,  # Locomotive rolling resistance (kg)
        'T3': T3,  # Gradient resistance (kg)
        'T4': T4,  # Curvature resistance (kg)
        'speed_for_power': speed_for_power  # Speed for power calculation (km/h)
    }

def calculate_tractive_effort(components: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate final tractive effort, electrical power, and OHE current requirements.

    This function combines all resistance components and calculates the electrical
    power requirements for overhead electric (OHE) traction systems.

    Args:
        components (Dict[str, float]): Resistance components from calculate_resistance_components()

    Returns:
        Dict[str, float]: Final calculations:
            - te: Total tractive effort (kg)
            - power: Electrical power requirement (kW)
            - ohe_current: Overhead line current (A)

    Physics:
        - Tractive Effort (TE) = T1 + T2 + T3 + T4 (kg)
        - Power (P) = TE × Speed / Constant (kW)
        - Current (I) = P × Constant / (V × η × PF) (A)

    Electrical Engineering:
        - Accounts for OHE voltage, system efficiency, and power factor
        - Current calculation ensures electrical system capacity
    """
    # Total tractive effort is sum of all resistance components
    te = components['T1'] + components['T2'] + components['T3'] + components['T4']

    # Power = (Tractive Effort × Speed) / Power Constant
    power = (te * components['speed_for_power']) / POWER_CONSTANT

    # OHE Current = Power × Current Constant / (Voltage × Efficiency × Power Factor)
    ohe_current = (power * CURRENT_CONSTANT) / (OHE_VOLTAGE * OHE_EFFICIENCY * POWER_FACTOR)

    return {
        'te': te,           # Total tractive effort (kg)
        'power': power,     # Electrical power requirement (kW)
        'ohe_current': ohe_current  # OHE current requirement (A)
    }

def perform_tractive_effort_calculation(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main calculation function that orchestrates all tractive effort analysis.

    This function coordinates the complete tractive effort calculation by calling
    the individual calculation functions in the correct sequence.

    Args:
        inputs (Dict[str, Any]): Complete input parameters including:
            - load: Wagon load (tonnes)
            - loco_weight: Locomotive weight (tonnes)
            - gradient, grad_type: Slope parameters
            - curvature, curvature_unit: Curve parameters
            - mode: "Start" or "Running"
            - speed: Train speed (km/h, for running mode)

    Returns:
        Dict[str, Any]: Complete analysis results including:
            - All resistance components (T1, T2, T3, T4)
            - Speed for power calculation
            - Total tractive effort (te)
            - Electrical power requirement (power)
            - OHE current requirement (ohe_current)

    Process Flow:
        1. Calculate resistance components
        2. Calculate tractive effort and power requirements
        3. Combine all results for reporting
    """
    # Step 1: Calculate all resistance components
    components = calculate_resistance_components(inputs)

    # Step 2: Calculate final tractive effort and power requirements
    results = calculate_tractive_effort(components)

    # Step 3: Combine all results into comprehensive output
    final_results = {**components, **results}
    return final_results