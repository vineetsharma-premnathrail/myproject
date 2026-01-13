"""
Hydraulic Tool Schemas Module
============================
Purpose:
    Pydantic models for input validation and data structure definition.
    Defines the expected format for hydraulic calculation inputs from the frontend.
Layer:
    Backend / Tools / Hydraulic / Schemas
Validation:
    - Automatic type conversion and validation
    - Required vs optional field handling
    - Default values for optional parameters
    - Input sanitization and bounds checking
Calculation Modes:
    - calc_cc: Calculate motor displacement and pump requirements for target speed
    - calc_speed: Calculate achievable speeds for given motor/pump specifications
Fields:
    Vehicle Parameters:
        - weight: Locomotive weight in tonnes
        - axles: Number of axles
        - wheel_diameter: Wheel diameter in mm
        - speed: Target or actual speed in km/h
    System Configuration:
        - num_motors: Total number of hydraulic motors
        - per_axle_motor: Motors per axle
        - pressure: System pressure in bar
        - Various gear ratios (PTO, axle, engine)
    Efficiencies:
        - mech_eff_motor: Motor mechanical efficiency (%)
        - vol_eff_motor: Motor volumetric efficiency (%)
        - vol_eff_pump: Pump volumetric efficiency (%)
    Operating Conditions:
        - slope_percent: Track gradient (%)
        - curve_degree: Curve degree (1/R)
    Motor/Pump Specs:
        - motor_disp_in: Motor displacement (cc/rev)
        - pump_disp_in: Pump displacement (cc/rev)
        - max_motor_rpm, max_pump_rpm: Maximum RPM limits
"""

from pydantic import BaseModel
from typing import List, Optional

class HydraulicInput(BaseModel):
    """
    Input validation model for hydraulic calculations.

    Defines all possible input parameters for hydraulic motor/pump sizing calculations.
    Automatically validates data types, required fields, and provides defaults
    for optional parameters. Supports both calculation modes.

    Required Fields (All Modes):
        - calc_mode: Calculation mode ("calc_cc" or "calc_speed")
        - weight: Vehicle weight in tonnes
        - axles: Number of axles
        - wheel_diameter: Wheel diameter in mm
        - max_vehicle_rpm: Maximum engine RPM
        - pto_gear_ratio: PTO gear ratio
        - engine_gear_ratio: Engine gear ratios (comma-separated)
        - axle_gear_box_ratio: Axle gearbox ratio
        - num_motors: Total number of motors
        - per_axle_motor: Motors per axle
        - vol_eff_motor: Motor volumetric efficiency (%)
        - vol_eff_pump: Pump volumetric efficiency (%)
        - max_motor_rpm: Maximum motor RPM
        - max_pump_rpm: Maximum pump RPM

    Mode-Specific Required Fields:
        calc_cc mode:
            - speed: Target vehicle speed (km/h)
            - pressure: System pressure (bar)
            - mech_eff_motor: Motor mechanical efficiency (%)

        calc_speed mode:
            - motor_disp_in: Motor displacement (cc/rev)
            - pump_disp_in: Pump displacement (cc/rev)

    Optional Fields:
        - slope_percent: Track gradient percentage (default: 0)
        - curve_degree: Curve degree (default: 0)
    """

    # Calculation mode selection
    calc_mode: str  # "calc_cc" (calculate displacement) or "calc_speed" (calculate speed)

    # Vehicle parameters
    weight: str  # Locomotive weight in tonnes
    axles: str  # Number of axles
    speed: str  # Target speed (km/h) for calc_cc, or calculated speed for calc_speed
    max_vehicle_rpm: str  # Maximum vehicle engine RPM

    # Gear ratios
    pto_gear_ratio: str  # PTO (Power Take-Off) gear ratio
    engine_gear_ratio: str  # Engine gear ratios (comma-separated list)
    axle_gear_box_ratio: str  # Axle gearbox ratio

    # Track conditions
    slope_percent: str  # Track gradient in percentage
    curve_degree: str  # Curve degree (1/R where R is radius in meters)

    # Wheel specifications
    wheel_diameter: str  # Wheel diameter in mm

    # Hydraulic system configuration
    num_motors: str  # Total number of hydraulic motors
    per_axle_motor: str  # Number of motors per axle

    # System pressures and efficiencies
    pressure: str  # System pressure in bar (required for calc_cc)
    mech_eff_motor: str  # Motor mechanical efficiency in percentage (required for calc_cc)
    vol_eff_motor: str  # Motor volumetric efficiency in percentage
    motor_disp_in: str  # Motor displacement in cc/rev (required for calc_speed)
    max_motor_rpm: str  # Maximum motor RPM
    vol_eff_pump: str  # Pump volumetric efficiency in percentage
    pump_disp_in: str  # Pump displacement in cc/rev (required for calc_speed)
    max_pump_rpm: str  # Maximum pump RPM