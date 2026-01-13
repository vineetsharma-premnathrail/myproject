# =========================================
# Tractive Effort Tool Service Layer
# =========================================
# Orchestrates tractive effort calculations and formats results for presentation.
# Acts as the bridge between pure mathematical functions (core.py) and API endpoints.
#
# Purpose: Coordinate calculations, format detailed reports, and prepare
#          data for user interfaces and PDF generation.
# Used by: tractive_effort API endpoints and report generation
# Dependencies: core.py (pure calculation functions)

from typing import Dict, Any, Tuple, Optional  # Type hints for better code documentation
from .core import perform_tractive_effort_calculation  # Import main calculation function

def perform_te_calculation(inputs: Dict[str, Any], inputs_raw: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
    """
    Main orchestration function for tractive effort calculations.

    This function coordinates the complete tractive effort analysis and returns
    both the raw calculation results and a formatted report for presentation.

    Args:
        inputs (Dict[str, Any]): Processed input parameters for calculations
        inputs_raw (Dict[str, Any], optional): Original raw input values for display
            If not provided, falls back to processed inputs

    Returns:
        Tuple[Dict[str, Any], str]:
            - results: Raw calculation results from core functions
            - formatted_report: Human-readable report string

    Process Flow:
        1. Call core calculation function
        2. Format results into detailed report
        3. Return both raw data and formatted report

    Note:
        The function returns a tuple to support both programmatic access
        to raw data and human-readable report generation.
    """
    # Perform the core calculations
    results = perform_tractive_effort_calculation(inputs)

    # Format the results into a comprehensive report
    formatted_report = format_te_report(inputs, results, inputs_raw or {})

    return results, formatted_report

def format_te_report(inputs: Dict[str, Any], results: Dict[str, Any], inputs_raw: Dict[str, Any]) -> str:
    """
    Format tractive effort calculation results into a comprehensive report.

    This function creates a detailed, well-structured report showing all inputs,
    calculations, and results. Used for PDF generation, web display, and documentation.

    Args:
        inputs (Dict[str, Any]): Processed input parameters
        results (Dict[str, Any]): Calculation results from core functions
        inputs_raw (Dict[str, Any]): Original user input values (for display)

    Returns:
        str: Formatted report in Markdown-like format with sections:
            - Input parameters
            - Summary results (TE, Power, Current)
            - Detailed resistance components (T1, T2, T3, T4)

    Report Structure:
        1. Inputs Section: All user-provided parameters
        2. Calculation Results: Key outputs (tractive effort, power, current)
        3. Resistance Components: Detailed breakdown of each resistance type

    Units:
        - Load: tons
        - Tractive Effort: kg (also shown in tons)
        - Power: HP (horsepower)
        - Current: A (amperes)
        - Resistances: kg (force)

    Note:
        Uses raw inputs for display when available to preserve user formatting,
        falls back to processed inputs if raw values not provided.
    """
    return (
        f"# Tractive Effort Calculation Report\n\n"
        f"--- 1. Inputs ---\n"
        f"• Shunting Load: {inputs_raw.get('load', inputs.get('load'))} tons\n"
        f"• GBW of Vehicle: {inputs_raw.get('loco_weight', inputs.get('loco_weight'))} tons\n"
        f"• Gradient: {inputs_raw.get('gradient', inputs.get('gradient'))} ({inputs.get('grad_type')})\n"
        f"• Curvature: {inputs_raw.get('curvature', inputs.get('curvature'))} ({inputs.get('curvature_unit')})\n"
        f"• Speed: {inputs_raw.get('speed', inputs.get('speed'))} km/h\n"
        f"• Mode: {inputs.get('mode')}\n\n"

        f"--- 2. Calculation Results ---\n"
        f"Summary of Results:\n"
        f"  • Tractive Effort (TE): {results['te']:.2f} kg  ({results['te']/1000:.3f} tons)\n"
        f"  • Rail Horsepower: {results['power']:.2f} HP\n"
        f"  • OHE Current: {results['ohe_current']:.2f} A\n\n"
        f"Resistance Components:\n"
        f"  • T1 (Wagon Rolling Resistance): {results['T1']:.2f} kg\n"
        f"  • T2 (Loco Rolling Resistance): {results['T2']:.2f} kg\n"
        f"  • T3 (Gradient Resistance): {results['T3']:.2f} kg\n"
        f"  • T4 (Curvature Resistance): {results['T4']:.2f} kg\n"
    )