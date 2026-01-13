# =========================================
# Load Distribution Tool Service Layer
# =========================================
# Orchestrates load distribution calculations and formats results for presentation.
# Acts as the bridge between pure mathematical functions (core.py) and API endpoints.
#
# Purpose: Coordinate calculations, format step-by-step explanations, and prepare
#          data for reports and user interfaces.
# Used by: load_distribution API endpoints and report generation
# Dependencies: core.py (pure calculation functions)

from typing import Dict, Any, Tuple  # Type hints for better code documentation
from .core import perform_load_distribution_calculation  # Import main calculation function

def perform_load_distro_calculation(config_type: str, total_load: float, front_percent: float,
                                  q1_percent: float, q3_percent: float) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.

    This function maintains compatibility with older code that uses the
    "distro" spelling. It simply calls the new core calculation function.

    Args:
        config_type (str): Vehicle configuration ("bogie" or "truck")
        total_load (float): Total vehicle load in tonnes
        front_percent (float): Percentage of load on front axle (0-100)
        q1_percent (float): Percentage of front axle load on Q1 wheel (0-100)
        q3_percent (float): Percentage of rear axle load on Q3 wheel (0-100)

    Returns:
        Dict[str, Any]: Complete calculation results (same as core function)

    Note:
        This is a wrapper function - consider using perform_load_distribution_calculation directly
    """
    return perform_load_distribution_calculation(config_type, total_load, front_percent, q1_percent, q3_percent)

def perform_load_distro_calc(config_type: str, total_load: float, front_percent: float,
                           q1_percent: float, q3_percent: float) -> Dict[str, Any]:
    """
    Main orchestration function for load distribution calculations.

    This is the primary service function that coordinates the load distribution
    analysis. It calls the core calculation function and returns the results
    for further processing by API endpoints or report generation.

    Args:
        config_type (str): Vehicle configuration type ("bogie" or "truck")
        total_load (float): Total vehicle load in appropriate units
        front_percent (float): Percentage of total load carried by front axle
        q1_percent (float): Percentage of front axle load on left wheel (Q1)
        q3_percent (float): Percentage of rear axle load on left wheel (Q3)

    Returns:
        Dict[str, Any]: Complete analysis results including:
            - Individual wheel loads (Q1, Q2, Q3, Q4)
            - Axle loads and distribution
            - Safety metrics and pass/fail status
            - Min/max wheel load analysis

    Note:
        This function delegates all calculations to the core module for consistency
        and testability. The service layer focuses on orchestration and data flow.
    """
    return perform_load_distribution_calculation(config_type, total_load, front_percent, q1_percent, q3_percent)

def format_load_distro_steps(inputs: Dict[str, Any], results: Dict[str, Any]) -> str:
    """
    Format load distribution calculation steps into a human-readable explanation.

    This function creates a detailed step-by-step breakdown of the load distribution
    calculations, showing the mathematical formulas and intermediate results.
    Used for educational purposes and detailed reports.

    Args:
        inputs (Dict[str, Any]): Original input parameters from the user/API
        results (Dict[str, Any]): Calculation results from core functions

    Returns:
        str: Formatted step-by-step explanation with formulas and values

    Format Structure:
        1. Front/Rear Load Calculations - Basic load distribution
        2. Individual Wheel Loads - Q value calculations
        3. Safety Metrics - Q, ΔQ, ΔQ/Q calculations
        4. Final Check - Pass/fail determination

    Example Output:
        "1. Calculate Front and Rear Loads:
           Front = Total Load × (Front % / 100)
           Front = 100.00 × (60.00 / 100) = 60.00 Ton"
    """
    return (
        f"1. Calculate Front and Rear Loads:\n"
        f"   Front = Total Load × (Front % / 100)\n"
        f"   Front = {inputs['total_load']:.2f} × ({inputs['front_percent']:.2f} / 100) = {results['front_load']:.2f} Ton\n\n"
        f"   Rear = Total Load - Front Load\n"
        f"   Rear = {inputs['total_load']:.2f} - {results['front_load']:.2f} = {results['rear_load']:.2f} Ton\n\n"

        f"2. Calculate Individual Wheel Loads (Q Values):\n"
        f"   Q1 = Front Load × (Q1 % / 100)\n"
        f"   Q1 = {results['front_load']:.2f} × ({inputs['q1_percent']:.2f} / 100) = {results['q_values']['Q1']:.2f} Ton\n\n"
        f"   Q2 = Front Load - Q1\n"
        f"   Q2 = {results['front_load']:.2f} - {results['q_values']['Q1']:.2f} = {results['q_values']['Q2']:.2f} Ton\n\n"
        f"   Q3 = Rear Load × (Q3 % / 100)\n"
        f"   Q3 = {results['rear_load']:.2f} × ({inputs['q3_percent']:.2f} / 100) = {results['q_values']['Q3']:.2f} Ton\n\n"
        f"   Q4 = Rear Load - Q3\n"
        f"   Q4 = {results['rear_load']:.2f} - {results['q_values']['Q3']:.2f} = {results['q_values']['Q4']:.2f} Ton\n\n"

        f"3. Calculate Q, ΔQ, and ΔQ/Q:\n"
        f"   Q (Average on heavier axle) = {results['q_value']:.2f} Ton\n"
        f"   QL (Lowest wheel load) = {results['ql_value']:.2f} Ton ({results['ql_name']})\n"
        f"   ΔQ = Q - QL = {results['q_value']:.2f} - {results['ql_value']:.2f} = {results['delta_q']:.2f} Ton\n\n"
        f"   ΔQ/Q = ΔQ / Q = {results['delta_q']:.2f} / {results['q_value']:.2f} = {results['delta_q_by_q']:.4f}\n\n"

        f"4. Final Check:\n"
        f"   Is {results['delta_q_by_q']:.2%} ≤ {results['limit']:.0%}? {'Yes' if results['status']=='success' else 'No'}.\n"
        f"   Result: {results['status'].upper()}"
    )