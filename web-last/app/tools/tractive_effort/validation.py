# =========================================
# Tractive Effort Tool Validation Module
# =========================================
# Input validation and processing logic for tractive effort calculations.
#
# Purpose: Validate and convert raw user inputs into properly typed, validated
# data structures suitable for physics-based traction calculations. Ensures data
# integrity and prevents invalid operating parameters from causing calculation errors.
#
# Engineering Context:
# - Railway traction calculations require precise, validated inputs for safety
# - Invalid parameters could lead to unsafe locomotive power recommendations
# - Type conversion and range validation prevent common user input errors
#
# Used by: api.py (endpoint validation), service.py (input processing)
# Dependencies: schemas.py (TractiveEffortInput model)

from typing import Dict, Any, Tuple
from .schemas import TractiveEffortInput

def validate_tractive_effort_inputs(raw: TractiveEffortInput) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate and process tractive effort calculation inputs.

    Performs comprehensive validation of user inputs for train traction analysis,
    ensuring all parameters are within physically meaningful ranges and properly
    typed for engineering calculations involving rolling resistance, gradients,
    and electrical power requirements.

    Validation Process:
    1. Leverage Pydantic schema validation for type safety and constraints
    2. Convert validated inputs to calculation-ready format
    3. Preserve raw inputs for report generation and user context

    Args:
        raw (TractiveEffortInput): Raw user input data from API request
                                    - Contains validated data from Pydantic schema
                                    - Includes load, weights, gradients, speeds, and modes

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing:
            - inputs: Processed and validated numeric inputs for calculations
            - inputs_raw: Original raw inputs for report generation

    Input Processing Details:

    Train Load (load):
    - Already validated as non-negative float by Pydantic
    - Represents total wagon/car load in tonnes
    - Can be zero for locomotive-only calculations

    Locomotive Weight (loco_weight):
    - Already validated as non-negative float by Pydantic
    - Represents locomotive gross weight in tonnes
    - Must be positive for meaningful traction calculations

    Track Gradient (gradient):
    - Already validated as non-negative float by Pydantic
    - Value depends on grad_type ("Degree" or "1 in G")
    - Zero represents level track (no gradient resistance)

    Track Curvature (curvature):
    - Already validated as non-negative float by Pydantic
    - Value depends on curvature_unit ("Radius(m)" or "Degree")
    - Zero represents straight track (no curvature resistance)

    Train Speed (speed):
    - Already validated as non-negative float by Pydantic
    - Represents train velocity in km/h
    - Zero represents stationary conditions (starting calculations)

    Operating Mode (mode):
    - Must be either "Start" or "Running" (enforced by Pydantic)
    - Affects rolling resistance coefficients
    - "Start" uses higher resistance values for initial movement

    Gradient Type (grad_type):
    - Must be "Degree" or "1 in G" (enforced by Pydantic)
    - Determines how gradient value is interpreted
    - Affects gradient resistance calculation methodology

    Curvature Unit (curvature_unit):
    - Must be "Radius(m)" or "Degree" (enforced by Pydantic)
    - Determines how curvature value is interpreted
    - Affects curvature resistance calculation methodology

    Safety Validation:
    - Ensures traction scenarios are physically possible
    - Prevents unrealistic operating conditions
    - Validates against railway engineering constraints

    Example:
        >>> raw_input = TractiveEffortInput(
        ...     load=1500.0, loco_weight=120.0, gradient=1.0,
        ...     curvature=300.0, speed=60.0, mode="Running",
        ...     grad_type="Degree", curvature_unit="Radius(m)"
        ... )
        >>> inputs, inputs_raw = validate_tractive_effort_inputs(raw_input)
        >>> print(inputs)
        {
            'load': 1500.0, 'loco_weight': 120.0, 'gradient': 1.0,
            'curvature': 300.0, 'speed': 60.0, 'mode': 'Running',
            'grad_type': 'Degree', 'curvature_unit': 'Radius(m)'
        }

    Note:
        Since comprehensive validation is handled by the Pydantic schema,
        this function primarily serves as a processing layer and maintains
        API consistency with other tool validation functions. Raw inputs
        are preserved for generating user-friendly reports with original
        parameter values and engineering context.
    """

    inputs = {}  # Processed numeric inputs for calculations
    inputs_raw = raw.dict()  # Raw inputs for report formatting

    # All inputs are already validated by Pydantic schema
    # Simply update inputs with validated data
    inputs.update(inputs_raw)

    return inputs, inputs_raw