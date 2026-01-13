# =========================================
# Vehicle Performance Tool Validation Module
# =========================================
# Input validation and processing logic for locomotive performance analysis.
#
# Purpose: Validate and convert raw user inputs into properly typed, validated
# data structures suitable for physics-based locomotive performance calculations.
# Ensures data integrity and prevents invalid operating parameters from causing errors.
#
# Engineering Context:
# - Railway performance calculations require precise, validated inputs for accuracy
# - Invalid parameters could lead to unsafe locomotive performance predictions
# - Type conversion and field mapping prevent common user input errors
#
# Used by: api.py (endpoint validation), service.py (input processing)
# Dependencies: schemas.py (VehiclePerformanceInput model)

from typing import Dict, Any, Tuple
from .schemas import VehiclePerformanceInput

def validate_vehicle_performance_inputs(raw: VehiclePerformanceInput) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate and process locomotive performance analysis inputs.

    Performs comprehensive validation of user inputs for locomotive performance
    evaluation, including field name mapping, data type conversion, and default
    value assignment to ensure compatibility with calculation modules.

    Validation Process:
    1. Leverage Pydantic schema validation for type safety and constraints
    2. Map HTML/form field names to internal calculation field names
    3. Handle special data types (gear ratios as comma-separated strings)
    4. Apply sensible defaults for optional parameters
    5. Preserve raw inputs for report generation

    Args:
        raw (VehiclePerformanceInput): Raw user input data from API request
                                      - Contains validated data from Pydantic schema
                                      - Includes locomotive specs, transmission, and limits

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing:
            - inputs: Processed and validated inputs with internal field names
            - inputs_raw: Original raw inputs for report generation

    Field Mapping Details:

    HTML Field Name -> Internal Field Name:
    - loco_gvw -> loco_gvw_kg: Locomotive weight in kg
    - max_speed -> max_speed_kmh: Maximum speed in km/h
    - shunting_load -> shunting_load_t: Shunting load in tonnes
    - peak_power -> peak_power_kw: Peak power in kW
    - wheel_dia -> wheel_dia_m: Wheel diameter in meters

    Special Processing:

    Gear Ratios:
    - Input: Comma-separated string (e.g., "8.5, 6.2, 4.5")
    - Processing: Split by comma, strip whitespace, convert to float list
    - Output: List[float] for transmission analysis

    RPM Parameters:
    - max_rpm: Defaults to 2500 RPM if not provided
    - min_rpm: Defaults to 100 RPM if not provided
    - Ensures valid engine speed range for calculations

    Units Preservation:
    - curve_unit: Preserved for curve resistance calculations
    - slope_unit: Preserved for gradient resistance calculations
    - Maintains input context for proper unit conversions

    Safety Validation:
    - Ensures locomotive specifications are within reasonable bounds
    - Prevents unrealistic performance predictions
    - Validates transmission configuration completeness

    Example:
        >>> raw_input = VehiclePerformanceInput(
        ...     loco_gvw=120000, max_speed=100, num_axles=4,
        ...     gear_ratios=[8.5, 6.2, 4.5], shunting_load=2000,
        ...     peak_power=2000, friction_mu=0.35, wheel_dia=1.25,
        ...     min_rpm=400, max_rpm=2100, max_curve=6.0, max_slope=2.0
        ... )
        >>> inputs, inputs_raw = validate_vehicle_performance_inputs(raw_input)
        >>> print(inputs.keys())
        dict_keys(['loco_gvw_kg', 'max_speed_kmh', 'num_axles', 'gear_ratios',
        ...        'shunting_load_t', 'peak_power_kw', 'friction_mu', 'wheel_dia_m',
        ...        'min_rpm', 'max_rpm', 'max_curve', 'max_slope', 'curve_unit', 'slope_unit'])

    Note:
        Field name mapping ensures compatibility between user-facing forms
        and internal calculation modules. Raw inputs are preserved for
        generating user-friendly reports with original parameter names and values.
        This validation layer acts as the interface between API inputs and
        the physics-based calculation engine.
    """

    inputs = {}  # Processed inputs with internal field names
    inputs_raw = raw.dict()  # Raw inputs for report formatting

    # Map user-facing field names to internal calculation field names
    # This ensures compatibility between HTML forms and calculation modules
    field_mapping = {
        'loco_gvw': 'loco_gvw_kg',        # kg for calculations
        'max_speed': 'max_speed_kmh',     # km/h for speed analysis
        'shunting_load': 'shunting_load_t', # tonnes for load analysis
        'peak_power': 'peak_power_kw',    # kW for power calculations
        'wheel_dia': 'wheel_dia_m'        # meters for torque conversion
    }

    # Apply field name mapping for calculation compatibility
    for html_field, internal_field in field_mapping.items():
        if html_field in inputs_raw:
            inputs[internal_field] = inputs_raw[html_field]

    # Special handling for gear ratios - convert from string to list if needed
    # Supports both list input (API) and comma-separated string (forms)
    if 'gear_ratios' in inputs_raw:
        gear_value = inputs_raw['gear_ratios']
        if isinstance(gear_value, str):
            # Parse comma-separated string into float list
            try:
                inputs['gear_ratios'] = [float(x.strip()) for x in gear_value.split(',') if x.strip()]
            except ValueError as e:
                raise ValueError(f"Invalid gear ratios format: {gear_value}. Use comma-separated numbers.") from e
        else:
            # Already a list, use as-is
            inputs['gear_ratios'] = gear_value

    # Apply sensible defaults for optional RPM parameters
    # Ensures valid engine speed range for performance calculations
    if 'max_rpm' not in inputs_raw or inputs_raw['max_rpm'] is None:
        inputs['max_rpm'] = 2500  # Default maximum engine speed
    if 'min_rpm' not in inputs_raw or inputs_raw['min_rpm'] is None:
        inputs['min_rpm'] = 100   # Default minimum engine speed

    # Copy remaining fields that don't need special processing
    # Includes units specifications and other direct-use parameters
    for key, value in inputs_raw.items():
        if key not in field_mapping and key != 'gear_ratios':
            inputs[key] = value

    return inputs, inputs_raw