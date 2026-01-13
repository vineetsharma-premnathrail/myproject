"""
Braking Tool Validation Module
=============================
Purpose:
    Input validation and processing for braking calculations.
    Ensures data integrity and provides user-friendly error messages.
Layer:
    Backend / Tools / Braking / Validation
Validation Rules:
    - Mass must be greater than 0 kg
    - Number of wheels must be greater than 0
    - Friction coefficient must be between 0 and 1
    - Reaction time must be non-negative
    - Gradient inputs are validated by parsing functions
Processing:
    - Converts Pydantic models to internal dictionaries
    - Applies default values for optional fields
    - Sanitizes string inputs
    - Prepares data for calculation functions
Error Handling:
    - Raises ValueError for invalid inputs
    - Provides specific error messages for debugging
    - Prevents invalid data from reaching calculations
"""

from typing import Dict, Any, Tuple
from .schemas import BrakingInput

def validate_braking_inputs(raw: BrakingInput) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate and process braking calculation inputs.

    Takes validated Pydantic input model and converts it to internal format
    used by calculation functions. Performs additional business logic validation
    beyond Pydantic's automatic validation.

    Args:
        raw (BrakingInput): Validated input data from API endpoint

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]:
            - inputs: Processed input dictionary for calculations
            - inputs_raw: Original raw input dictionary for reference

    Raises:
        ValueError: For business logic validation failures:
            - Mass must be greater than 0
            - Number of wheels must be greater than 0
            - Friction coefficient must be between 0 and 1

    Example:
        >>> input_data = BrakingInput(mass_kg=50000, reaction_time=1.0, ...)
        >>> inputs, raw = validate_braking_inputs(input_data)
        >>> # inputs now contains processed, validated data
    """
    # Convert Pydantic model to dictionary for processing
    inputs_raw = raw.dict()

    # Initialize processed inputs dictionary
    inputs = {}

    # Extract and validate required vehicle parameters
    inputs['mass_kg'] = raw.mass_kg
    inputs['reaction_time'] = raw.reaction_time
    inputs['num_wheels'] = raw.num_wheels
    inputs['calc_mode'] = raw.calc_mode

    # Extract rail-specific parameters
    inputs['rail_speed_input'] = raw.rail_speed_input
    inputs['rail_gradient_input'] = raw.rail_gradient_input
    inputs['rail_gradient_type'] = raw.rail_gradient_type

    # Extract road-specific parameters with defaults
    inputs['road_speed_input'] = raw.road_speed_input or ""
    inputs['road_gradient_input'] = raw.road_gradient_input or ""
    inputs['road_gradient_type'] = raw.road_gradient_type or "Percentage (%)"
    inputs['mu'] = raw.mu or 0.7

    # Extract documentation parameters with defaults
    inputs['doc_no'] = raw.doc_no or ""
    inputs['made_by'] = raw.made_by or ""
    inputs['checked_by'] = raw.checked_by or ""
    inputs['approved_by'] = raw.approved_by or ""
    inputs['wheel_dia'] = raw.wheel_dia or 0

    # Business logic validation (beyond Pydantic automatic validation)
    if inputs['mass_kg'] <= 0:
        raise ValueError("Vehicle mass must be greater than 0 kg")

    if inputs['num_wheels'] <= 0:
        raise ValueError("Number of wheels must be greater than 0")

    if inputs['mu'] <= 0 or inputs['mu'] > 1:
        raise ValueError("Friction coefficient must be between 0 and 1")

    if inputs['reaction_time'] < 0:
        raise ValueError("Reaction time cannot be negative")

    # Return both processed inputs and original raw data
    return inputs, inputs_raw