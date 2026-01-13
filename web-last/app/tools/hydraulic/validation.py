"""
Hydraulic Tool Validation Module
===============================
Purpose:
    Input validation and processing for hydraulic calculations.
    Ensures data integrity and provides user-friendly error messages.
Layer:
    Backend / Tools / Hydraulic / Validation
Validation Rules:
    - Weight and dimensions must be positive
    - Gear ratios must be valid numbers
    - Efficiencies must be between 0 and 100%
    - RPM values must be positive
    - Engine gear ratios parsed from comma-separated strings
Processing:
    - Converts string inputs to appropriate numeric types
    - Applies default values for optional parameters
    - Parses complex inputs (gear ratio lists)
    - Prepares data for calculation functions
Mode-Specific Validation:
    - calc_cc: Requires speed, pressure, mechanical efficiency
    - calc_speed: Requires motor and pump displacements
Error Handling:
    - Raises ValueError for invalid inputs
    - Provides specific error messages for debugging
    - Prevents invalid data from reaching calculations
"""

from typing import Dict, Any, Tuple, List
from .schemas import HydraulicInput

def validate_hydraulic_inputs(raw: HydraulicInput) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate and process hydraulic calculation inputs.

    Takes validated Pydantic input model and converts it to internal format
    used by calculation functions. Performs additional business logic validation
    beyond Pydantic's automatic validation.

    Args:
        raw (HydraulicInput): Validated input data from API endpoint

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]:
            - inputs: Processed input dictionary for calculations
            - inputs_raw: Original raw input dictionary for reference

    Raises:
        ValueError: For business logic validation failures:
            - Invalid calculation mode
            - Negative or zero values for physical parameters
            - Invalid efficiency percentages
            - Malformed gear ratio strings

    Processing Steps:
        1. Extract calculation mode and basic validation
        2. Convert string inputs to numeric types
        3. Parse engine gear ratios from comma-separated string
        4. Apply mode-specific validation rules
        5. Set default values for optional parameters

    Example:
        >>> input_data = HydraulicInput(calc_mode="calc_cc", weight="100", ...)
        >>> inputs, raw = validate_hydraulic_inputs(input_data)
        >>> # inputs now contains processed, validated data
    """
    # Convert Pydantic model to dictionary for processing
    inputs_raw = raw.dict()

    # Initialize processed inputs dictionary
    inputs = {}

    # Extract and validate calculation mode
    mode = raw.calc_mode
    if mode not in ["calc_cc", "calc_speed"]:
        raise ValueError("Invalid calculation mode. Must be 'calc_cc' or 'calc_speed'")
    inputs['calc_mode'] = mode

    # Validate common vehicle parameters
    try:
        inputs['weight'] = float(raw.weight)
        inputs['axles'] = int(raw.axles)
        inputs['wheel_diameter'] = float(raw.wheel_diameter)
        inputs['axle_gear_box_ratio'] = float(raw.axle_gear_box_ratio)
        inputs['max_vehicle_rpm'] = float(raw.max_vehicle_rpm)
        inputs['pto_gear_ratio'] = float(raw.pto_gear_ratio)
    except ValueError:
        raise ValueError("Invalid numeric input for vehicle parameters")

    # Validate ranges for common parameters
    if inputs['weight'] <= 0:
        raise ValueError("Vehicle weight must be greater than 0 tonnes")
    if inputs['axles'] <= 0:
        raise ValueError("Number of axles must be greater than 0")
    if inputs['wheel_diameter'] <= 0:
        raise ValueError("Wheel diameter must be greater than 0 mm")
    if inputs['max_vehicle_rpm'] <= 0:
        raise ValueError("Maximum vehicle RPM must be greater than 0")

    # Parse engine gear ratios from comma-separated string
    try:
        engine_gear_raw = raw.engine_gear_ratio.strip()
        if not engine_gear_raw:
            raise ValueError("Engine gear ratios cannot be empty")
        parts = [p.strip() for p in engine_gear_raw.split(',') if p.strip()]
        if not parts:
            raise ValueError("No valid gear ratios found")
        engine_gear_list = [float(p) for p in parts]
        inputs['engine_gear_ratio_list'] = engine_gear_list
        inputs['engine_gear_ratio'] = engine_gear_list[0] if engine_gear_list else 1.0
    except ValueError:
        raise ValueError("Invalid engine gear ratios. Must be comma-separated numbers")

    # Validate hydraulic system parameters
    try:
        inputs['num_motors'] = int(raw.num_motors)
        inputs['per_axle_motor'] = int(raw.per_axle_motor)
        inputs['vol_eff_motor'] = float(raw.vol_eff_motor)
        inputs['vol_eff_pump'] = float(raw.vol_eff_pump)
        inputs['max_motor_rpm'] = float(raw.max_motor_rpm)
        inputs['max_pump_rpm'] = float(raw.max_pump_rpm)
    except ValueError:
        raise ValueError("Invalid numeric input for hydraulic parameters")

    # Validate ranges for hydraulic parameters
    if inputs['num_motors'] <= 0:
        raise ValueError("Number of motors must be greater than 0")
    if inputs['per_axle_motor'] <= 0:
        raise ValueError("Motors per axle must be greater than 0")
    if not (0 < inputs['vol_eff_motor'] <= 100):
        raise ValueError("Motor volumetric efficiency must be between 0 and 100%")
    if not (0 < inputs['vol_eff_pump'] <= 100):
        raise ValueError("Pump volumetric efficiency must be between 0 and 100%")
    if inputs['max_motor_rpm'] <= 0:
        raise ValueError("Maximum motor RPM must be greater than 0")
    if inputs['max_pump_rpm'] <= 0:
        raise ValueError("Maximum pump RPM must be greater than 0")

    # Mode-specific validations and processing
    is_cc = (mode == 'calc_cc')

    if is_cc:
        # Displacement calculation mode - requires speed, pressure, mechanical efficiency
        try:
            inputs['speed'] = float(raw.speed)
            inputs['pressure'] = float(raw.pressure)
            inputs['mech_eff_motor'] = float(raw.mech_eff_motor)
        except ValueError:
            raise ValueError("Invalid numeric input for displacement calculation parameters")

        if inputs['speed'] <= 0:
            raise ValueError("Target speed must be greater than 0 km/h")
        if inputs['pressure'] <= 0:
            raise ValueError("System pressure must be greater than 0 bar")
        if not (0 < inputs['mech_eff_motor'] <= 100):
            raise ValueError("Motor mechanical efficiency must be between 0 and 100%")

        # Set speed mode parameters to defaults
        inputs['motor_disp_in'] = 0.0
        inputs['pump_disp_in'] = 0.0
    else:
        # Speed calculation mode - requires motor and pump displacements
        try:
            inputs['motor_disp_in'] = float(raw.motor_disp_in)
            inputs['pump_disp_in'] = float(raw.pump_disp_in)
        except ValueError:
            raise ValueError("Invalid numeric input for speed calculation parameters")

        if inputs['motor_disp_in'] <= 0:
            raise ValueError("Motor displacement must be greater than 0 cc/rev")
        if inputs['pump_disp_in'] <= 0:
            raise ValueError("Pump displacement must be greater than 0 cc/rev")

        # Set displacement mode parameters to defaults
        inputs['speed'] = 0.0
        inputs['pressure'] = 0.0
        inputs['mech_eff_motor'] = 0.0

    # Optional parameters with defaults
    try:
        inputs['slope_percent'] = float(raw.slope_percent or 0)
        inputs['curve_degree'] = float(raw.curve_degree or 0)
    except ValueError:
        raise ValueError("Invalid numeric input for optional parameters")

    # Return both processed inputs and original raw data
    return inputs, inputs_raw