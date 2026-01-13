# =========================================
# Qmax Tool Service Layer Module
# =========================================
# Orchestration layer for Qmax calculations and report formatting.
#
# Purpose: Coordinate the complete Qmax calculation workflow from input processing
# through mathematical calculations to formatted report generation. Acts as the
# business logic layer between API endpoints and core calculation functions.
#
# Engineering Context:
# - Combines validated inputs with engineering formulas
# - Generates detailed calculation reports for documentation
# - Ensures consistent formatting across different output formats
# - Provides clear step-by-step engineering methodology
#
# Used by: api.py (endpoint orchestration)
# Dependencies: core.py (calculate_qmax), constants.py (CONSTANT_C)

from typing import Dict, Any, Tuple, Optional
from .core import calculate_qmax
from .constants import CONSTANT_C

def perform_qmax_calculation(inputs: Dict[str, Any], inputs_raw: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
    """
    Main orchestration function for Qmax (Maximum Axle Load) calculations.

    Coordinates the complete calculation workflow: performs the mathematical
    calculation using validated inputs and generates a formatted engineering
    report showing all steps and results.

    Process Flow:
    1. Execute core calculation with validated numeric inputs
    2. Generate detailed step-by-step report for documentation
    3. Return both raw results and formatted report

    Args:
        inputs (Dict[str, Any]): Validated numeric inputs from validation layer
                                - d: Wheel diameter in mm (float)
                                - sigma_b: Rail bending stress in N/mm² (float)
                                - v_head: Safety factor (float)

        inputs_raw (Dict[str, Any], optional): Original raw inputs for report formatting
                                             - Preserves user context in reports
                                             - Defaults to empty dict if not provided

    Returns:
        Tuple[Dict[str, Any], str]: A tuple containing:
            - results: Complete calculation results from core.py
            - formatted_report: Human-readable calculation report string

    Results Dictionary Contains:
        - d: Wheel diameter (input, mm)
        - sigma_b: Rail bending stress (input, N/mm²)
        - v_head: Safety factor (input)
        - qmax_kn: Maximum axle load in kiloNewtons
        - qmax_tonnes: Maximum axle load in metric tonnes

    Report Format:
        - Input parameters section
        - Engineering formula reference
        - Step-by-step calculation with intermediate values
        - Final results in both kN and tonnes

    Example:
        >>> inputs = {'d': 750.0, 'sigma_b': 880.0, 'v_head': 1.2}
        >>> results, report = perform_qmax_calculation(inputs)
        >>> print(f"Qmax = {results['qmax_kn']:.2f} kN")
        Qmax = 123.45 kN

    Note:
        This function serves as the main entry point for all Qmax calculations,
        ensuring consistent processing and reporting across different interfaces.
    """
    # Execute the core engineering calculation
    results = calculate_qmax(inputs['d'], inputs['sigma_b'], inputs['v_head'])

    # Generate detailed engineering report
    formatted_report = format_qmax_detailed_steps(results, inputs_raw or {})

    return results, formatted_report

def format_qmax_detailed_steps(results: Dict[str, Any], inputs_raw: Dict[str, Any]) -> str:
    """
    Format Qmax calculation results into a detailed engineering report.

    Creates a comprehensive, human-readable report showing the complete
    calculation methodology, input parameters, intermediate steps, and final
    results. Designed for engineering documentation and regulatory compliance.

    Report Structure:
    1. Input Parameters: Original user inputs with units
    2. Engineering Formula: Mathematical relationship with constants
    3. Step-by-Step Calculation: Intermediate values and substitutions
    4. Final Results: Qmax in both kN and tonnes

    Args:
        results (Dict[str, Any]): Calculation results from core.py containing
                                 all input parameters and computed Qmax values

        inputs_raw (Dict[str, Any]): Original raw inputs for display purposes
                                    - Preserves user-entered values in reports
                                    - Includes selection labels and custom values

    Returns:
        str: Formatted multi-line report string suitable for:
             - API responses (plain text)
             - Console output (readable format)
             - Report embedding (structured text)

    Report Sections:

    INPUT PARAMETERS:
    - Wheel diameter limit with units
    - Material strength selection and actual value used
    - Safety factor for dynamic loading

    STEP-BY-STEP CALCULATION:
    - Engineering formula with empirical constant
    - Parameter substitution with units
    - Intermediate calculations (stress ratios, diameter factors)
    - Final Qmax computation with proper significant figures

    FINAL RESULT:
    - Qmax in kiloNewtons (engineering standard)
    - Qmax in metric tonnes (practical reference)

    Mathematical Details:
    - Formula: Qmax = C × (d/2) × (σB/v_head)²
    - C: Empirical constant accounting for contact mechanics
    - d/2: Effective contact radius
    - (σB/v_head)²: Stress ratio with safety margin

    Example Output:
        # Qmax Calculation Report

        --- INPUT PARAMETERS ---
        Worn rail diameter limit (d): 750 mm
        Material Strength (σB): 880 N/mm²
          (Value Used: 880 N/mm²)
        Safety Factor (v_head): 1.2

        --- STEP-BY-STEP CALCULATION ---
        1. Formula:
           Qmax = C × (d / 2) × (σB / v_head)²
           Where C = 8.257e-7

        2. Substitute Values:
           d = 750 mm
           σB = 880 N/mm²
           v_head = 1.2

        3. Step-by-Step Calculation:
           a) (σB / v_head)² = (880 / 1.2)² = 538.666
           b) Qmax = 8.257e-7 × (750 / 2) × 538.666
           c) Qmax = 8.257e-7 × 375 × 538.666

        --- FINAL RESULT ---
        Qmax = 123.4567 kN
        Qmax = 12.589 tonnes

    Note:
        Report format is designed to be both human-readable and machine-parseable,
        supporting both direct display and inclusion in larger documents.
    """

    # Calculate intermediate values for detailed reporting
    sigma_v_head_squared = (results['sigma_b'] / results['v_head']) ** 2
    d_half = results['d'] / 2

    # Build comprehensive engineering report
    report_lines = [
        "# Qmax Calculation Report",
        "\n--- INPUT PARAMETERS ---",
        f"Worn rail diameter limit (d): {inputs_raw.get('d', 'N/A')} mm",
        f"Material Strength (σB): {inputs_raw.get('sigma_b_selection', 'N/A')}",
        f"  (Value Used: {results['sigma_b']} N/mm²)",
        f"Safety Factor (v_head): {inputs_raw.get('v_head', 'N/A')}",

        "\n--- STEP-BY-STEP CALCULATION ---",
        "1. Formula:",
        "   Qmax = C × (d / 2) × (σB / v_head)²",
        f"   Where C = {CONSTANT_C}",

        "\n2. Substitute Values:",
        f"   d = {results['d']} mm",
        f"   σB = {results['sigma_b']} N/mm²",
        f"   v_head = {results['v_head']}",

        "\n3. Step-by-Step Calculation:",
        f"   a) (σB / v_head)² = ({results['sigma_b']} / {results['v_head']})² = {sigma_v_head_squared:.3f}",
        f"   b) Qmax = {CONSTANT_C} × ({results['d']} / 2) × {sigma_v_head_squared:.3f}",
        f"   c) Qmax = {CONSTANT_C} × {d_half:.1f} × {sigma_v_head_squared:.3f}",

        "\n--- FINAL RESULT ---",
        f"Qmax = {results['qmax_kn']:.4f} kN",
        f"Qmax = {results['qmax_tonnes']:.4f} tonnes"
    ]

    return "\n".join(report_lines)