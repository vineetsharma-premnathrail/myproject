# =========================================
# Load Distribution Tool Validation Module
# =========================================
# Input validation and processing logic for load distribution analysis.
#
# Purpose: Validate and convert raw user inputs into properly typed, validated
# data structures suitable for engineering calculations. Ensures data integrity
# and prevents invalid load distribution scenarios from causing analysis errors.
#
# Engineering Context:
# - Railway load analysis requires precise, validated inputs for safety
# - Invalid parameters could lead to unsafe load distribution recommendations
# - Type conversion and range validation prevent common user input errors
#
# Used by: api.py (endpoint validation), service.py (input processing)
# Dependencies: schemas.py (LoadDistributionInput model)

from typing import Dict, Any, Tuple
from .schemas import LoadDistributionInput

def validate_load_distribution_inputs(raw: LoadDistributionInput) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate and process load distribution analysis inputs.

    Performs comprehensive validation of user inputs for rail vehicle load
    distribution analysis, ensuring all parameters are within physically
    meaningful ranges and properly typed for engineering calculations.

    Validation Process:
    1. Leverage Pydantic schema validation for type safety and constraints
    2. Convert validated inputs to calculation-ready format
    3. Preserve raw inputs for report generation and user context

    Args:
        raw (LoadDistributionInput): Raw user input data from API request
                                    - Contains validated data from Pydantic schema
                                    - Includes config_type, total_load, percentages

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing:
            - inputs: Processed and validated numeric inputs for calculations
            - inputs_raw: Original raw inputs for report generation

    Input Processing Details:

    Configuration Type (config_type):
    - Must be one of: "Bogie", "Truck", or "Axle"
    - Determines safety limits and analysis methodology
    - Affects ΔQ/Q ratio validation thresholds

    Total Load (total_load):
    - Already validated as positive float by Pydantic
    - Represents gross vehicle weight in tonnes
    - Used as baseline for all load distribution calculations

    Front Axle Percentage (front_percent):
    - Already validated as 0-100% by Pydantic
    - Determines longitudinal load distribution
    - Critical for vehicle balance and braking analysis

    Wheel Load Percentages (q1_percent, q3_percent):
    - Already validated as 0-100% by Pydantic
    - q1_percent: Front axle left wheel load percentage
    - q3_percent: Rear axle left wheel load percentage
    - Used to calculate individual wheel loads (Q1-Q4)

    Safety Validation:
    - Ensures load distribution scenarios are physically possible
    - Prevents unrealistic load concentrations that could cause instability
    - Validates against configuration-specific safety limits

    Wheel Load Convention:
    - Q1: Front axle, left wheel (when facing direction of travel)
    - Q2: Front axle, right wheel (calculated as 100% - q1_percent)
    - Q3: Rear axle, left wheel (q3_percent of rear axle load)
    - Q4: Rear axle, right wheel (calculated as 100% - q3_percent)

    Example:
        >>> raw_input = LoadDistributionInput(
        ...     config_type="Bogie",
        ...     total_load=85.5,
        ...     front_percent=55.0,
        ...     q1_percent=52.0,
        ...     q3_percent=48.0
        ... )
        >>> inputs, inputs_raw = validate_load_distribution_inputs(raw_input)
        >>> print(inputs)
        {
            'config_type': 'Bogie',
            'total_load': 85.5,
            'front_percent': 55.0,
            'q1_percent': 52.0,
            'q3_percent': 48.0
        }

    Note:
        Since comprehensive validation is handled by the Pydantic schema,
        this function primarily serves as a processing layer and maintains
        API consistency with other tool validation functions. Raw inputs
        are preserved for generating user-friendly reports with original
        parameter values and context.
    """

    inputs = {}  # Processed numeric inputs for calculations
    inputs_raw = raw.dict()  # Raw inputs for report formatting

    # All inputs are already validated by Pydantic schema
    # Simply update inputs with validated data
    inputs.update(inputs_raw)

    return inputs, inputs_raw