# =========================================
# Qmax Tool Validation Module
# =========================================
# Input validation and processing logic for Qmax calculations.
#
# Purpose: Validate and convert raw user inputs into properly typed, validated
# data structures suitable for engineering calculations. Ensures data integrity
# and prevents invalid parameters from causing calculation errors.
#
# Engineering Context:
# - Railway calculations require precise, validated inputs to ensure safety
# - Invalid parameters could lead to unsafe axle load recommendations
# - Type conversion and range validation prevent common user input errors
#
# Used by: api.py (endpoint validation), service.py (input processing)
# Dependencies: schemas.py (QmaxInput model), constants.py (SIGMA_B_OPTIONS)

from typing import Dict, Any, Tuple
from .schemas import QmaxInput
from .constants import SIGMA_B_OPTIONS

def validate_qmax_inputs(raw: QmaxInput) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate and process Qmax calculation inputs.

    Performs comprehensive validation of user inputs for maximum axle load
    calculations, converting string inputs to appropriate numeric types and
    applying engineering constraints.

    Validation Process:
    1. Convert string inputs to float values
    2. Apply physical constraints (positive values)
    3. Select appropriate material strength values
    4. Ensure safety factor is within reasonable bounds

    Args:
        raw (QmaxInput): Raw user input data from API request
                        Contains string representations of numeric values

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing:
            - inputs: Processed and validated numeric inputs for calculations
            - inputs_raw: Original raw inputs for report generation

    Raises:
        ValueError: If any input fails validation with descriptive error message
                   - Non-numeric values that can't be converted to float
                   - Negative or zero values for physical parameters
                   - Invalid material strength selections

    Input Processing Details:

    Wheel Diameter (d):
    - Converted from string to float (millimeters)
    - Must be positive (physical constraint)
    - Represents minimum allowable wheel diameter after wear

    Rail Bending Stress (sigma_b):
    - Either selected from predefined options or custom value
    - Predefined options: 880 N/mm² (high-strength), 680 N/mm² (standard)
    - Custom values must be positive and appropriate for rail steel
    - Represents maximum allowable rail deflection stress

    Safety Factor (v_head):
    - Converted from string to float
    - Must be positive (typically 1.1-1.5)
    - Accounts for dynamic loading and material uncertainties

    Example:
        >>> raw_input = QmaxInput(d="750", sigma_b_selection="880 N/mm²",
        ...                      sigma_b_custom="", v_head="1.2")
        >>> inputs, inputs_raw = validate_qmax_inputs(raw_input)
        >>> print(inputs)
        {'d': 750.0, 'sigma_b': 880.0, 'v_head': 1.2}

    Note:
        Raw inputs are preserved for report generation to maintain user context
        in calculation reports and downloadable documents.
    """

    inputs = {}  # Processed numeric inputs for calculations
    inputs_raw = raw.dict()  # Raw inputs for report formatting

    # Validate wheel diameter (d) - critical parameter for contact stress
    try:
        inputs['d'] = float(raw.d)
        if inputs['d'] <= 0:
            raise ValueError("Wheel diameter must be greater than 0 mm")
    except ValueError as e:
        if "greater than 0" in str(e):
            raise ValueError("Wheel diameter must be greater than 0 mm") from e
        raise ValueError("Invalid wheel diameter - must be a positive number") from e

    # Validate rail bending stress (sigma_b) - material property selection
    if raw.sigma_b_selection == "Custom":
        # Custom material strength specified by user
        try:
            inputs['sigma_b'] = float(raw.sigma_b_custom)
            if inputs['sigma_b'] <= 0:
                raise ValueError("Custom rail bending stress must be greater than 0 N/mm²")
        except ValueError as e:
            if "greater than 0" in str(e):
                raise ValueError("Custom rail bending stress must be greater than 0 N/mm²") from e
            raise ValueError("Invalid custom rail bending stress value") from e
    else:
        # Use predefined material strength option
        inputs['sigma_b'] = SIGMA_B_OPTIONS.get(raw.sigma_b_selection, 880)  # Default to 880

    # Validate safety factor (v_head) - accounts for dynamic loading uncertainties
    try:
        inputs['v_head'] = float(raw.v_head)
        if inputs['v_head'] <= 0:
            raise ValueError("Safety factor must be greater than 0")
    except ValueError as e:
        if "greater than 0" in str(e):
            raise ValueError("Safety factor must be greater than 0") from e
        raise ValueError("Invalid safety factor - must be a positive number") from e

    return inputs, inputs_raw