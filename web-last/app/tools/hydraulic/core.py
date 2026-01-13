# =========================================
# Hydraulic Tool Core Calculations Module
# =========================================
# Pure mathematical functions for hydraulic system calculations.
# Contains all the physics and engineering formulas for hydraulic motors, pumps, and power transmission.
# No I/O operations, no formatting - just pure calculations.
#
# Purpose: Calculate hydraulic motor displacement, pump requirements, and achievable speeds
# Used by: hydraulic service and API endpoints
# Dependencies: constants.py (gravity constant)

import math  # Mathematical functions (pi, sin, cos, etc.)
from typing import Dict, Any, List  # Type hints for better code documentation
from .constants import GRAVITY  # Gravity constant (9.81 m/s²)

def calculate_displacement_mode(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate hydraulic motor displacement and pump requirements for a given vehicle speed.

    This function calculates the required hydraulic motor displacement and corresponding
    pump specifications to achieve a desired vehicle speed, considering all resistances
    (rolling, gradient, curvature, starting) and system efficiencies.

    Args:
        inputs (Dict[str, Any]): Input parameters including:
            - speed: Desired vehicle speed in km/h
            - weight: Locomotive weight in tonnes
            - axles: Number of axles
            - wheel_diameter: Wheel diameter in mm
            - slope_percent: Track gradient in percentage
            - curve_degree: Curve degree (1/R where R is radius in meters)
            - pressure: System pressure in bar
            - mech_eff_motor: Motor mechanical efficiency in percentage
            - axle_gear_box_ratio: Gear ratio between motor and axle
            - engine_gear_ratio_list: List of engine gear ratios
            - pto_gear_ratio: PTO (Power Take-Off) gear ratio
            - vol_eff_motor: Motor volumetric efficiency in percentage
            - vol_eff_pump: Pump volumetric efficiency in percentage
            - max_vehicle_rpm: Maximum vehicle engine RPM

    Returns:
        Dict[str, Any]: Comprehensive results including:
            - Motor displacement in cc/rev
            - Required flow rates in LPM
            - Pump specifications for each gear ratio
            - All intermediate calculations for verification

    Raises:
        ValueError: For invalid input parameters (zero divisions, etc.)
    """
    # Initialize result containers
    results = {}  # Main calculation results
    pump_results = []  # Pump specifications for different gear ratios
    warnings = []  # Warning messages for out-of-range conditions

    # Extract input parameters
    speed = inputs['speed']  # Desired speed in km/h
    locomotive_weight = inputs['weight']  # Weight in tonnes
    number_of_axles = inputs['axles']  # Number of axles
    wheel_diameter = inputs['wheel_diameter']  # Wheel diameter in mm
    slope_percent = inputs['slope_percent']  # Track gradient in %
    curve_degree = inputs['curve_degree']  # Curve degree (1/R)
    pressure_bar = inputs['pressure']  # System pressure in bar
    mechanical_efficiency = inputs['mech_eff_motor'] / 100.0  # Convert % to decimal
    gear_ratio = inputs.get('axle_gear_box_ratio', 1.0)  # Axle gearbox ratio
    engine_gear_list = inputs.get('engine_gear_ratio_list', [1.0])  # Engine gear ratios
    pto_gear_ratio = inputs['pto_gear_ratio']  # PTO gear ratio

    # ===== BASIC VEHICLE CALCULATIONS =====
    # Calculate wheel circumference and rotational speeds
    wheel_circumference = (wheel_diameter * math.pi) / 1000  # Circumference in meters
    if wheel_circumference == 0:
        raise ValueError("Wheel Diameter cannot be 0.")

    speed_mps = (speed * 1000) / 3600  # Convert km/h to m/s
    wheel_rpm = (speed_mps / wheel_circumference) * 60  # Wheel RPM
    gearbox_input_rpm = wheel_rpm * gear_ratio  # RPM at gearbox input (motor output)

    # Input validation
    if number_of_axles <= 0:
        raise ValueError("Number of axles must be greater than 0.")
    if locomotive_weight <= 0:
        raise ValueError("Weight must be greater than 0.")

    # ===== RESISTANCE CALCULATIONS =====
    # Calculate rolling resistance using empirical formula
    # Formula: R = (A + B*v + C*v²) * W * g
    # Where A, B, C are empirical coefficients
    A = 0.647 + (13.17 / (locomotive_weight / number_of_axles))  # Rolling coefficient A
    B = 0.00933  # Rolling coefficient B (speed dependent)
    C = 0.057 / locomotive_weight  # Rolling coefficient C (speed squared dependent)

    # Calculate each resistance component in kN
    rolling_resistance = (A + B * speed + C * speed**2) * locomotive_weight * GRAVITY / 1000
    gradient_resistance = locomotive_weight * 1000 * GRAVITY * slope_percent / 100000  # Gradient resistance
    curvature_resistance = 0.4 * locomotive_weight * curve_degree * GRAVITY / 1000  # Curve resistance
    starting_resistance = 6 * locomotive_weight * GRAVITY / 1000  # Starting resistance

    # Total resistance = sum of all resistance components
    total_resistance = rolling_resistance + gradient_resistance + curvature_resistance + starting_resistance

    # ===== TORQUE CALCULATIONS =====
    # Calculate required torque at wheels
    wheel_radius = wheel_diameter / 2000  # Wheel radius in meters
    required_total_torque = total_resistance * 1000 * wheel_radius  # Total torque in Nm

    number_of_wheels = number_of_axles * 2  # Total number of wheels
    per_wheel_torque = required_total_torque / number_of_wheels if number_of_wheels > 0 else 0.0
    per_axle_torque = required_total_torque / number_of_axles if number_of_axles > 0 else 0.0

    # Calculate torque at gearbox input (motor output)
    if gear_ratio == 0:
        raise ValueError("Axle Gearbox Ratio cannot be 0.")
    per_gearbox_input_torque = per_axle_torque / gear_ratio  # Torque in Nm

    # Convert to kg·cm for hydraulic calculations (common unit in hydraulics)
    per_gearbox_input_torque_kg_cm = per_gearbox_input_torque * 10.1972
    pressure_kg_cm2 = pressure_bar * 1.01972  # Convert bar to kg/cm²

    # ===== HYDRAULIC MOTOR CALCULATIONS =====
    # Validate inputs
    if pressure_kg_cm2 == 0 or mechanical_efficiency == 0:
        raise ValueError("Pressure or Mechanical Efficiency cannot be 0.")

    # Calculate motor displacement using hydraulic formula:
    # D = (T × 2π) / (P × η_mech)
    # Where: D = displacement, T = torque, P = pressure, η_mech = mechanical efficiency
    motor_displacement = (per_gearbox_input_torque_kg_cm * 2 * 3.1416) / (pressure_kg_cm2 * mechanical_efficiency)

    # Calculate required flow rate considering volumetric efficiency
    vol_eff_motor_frac = (inputs['vol_eff_motor'] / 100.0)
    if vol_eff_motor_frac == 0:
        raise ValueError("Motor Volumetric Efficiency cannot be 0.")

    # Flow rate = (Displacement × RPM) / Volumetric Efficiency
    hydraulic_motor_flow = ((motor_displacement * gearbox_input_rpm) / vol_eff_motor_frac ) / 1000

    # ===== STORE INTERMEDIATE RESULTS =====
    results['speed_mps'] = speed_mps
    results['wheel_circumference'] = wheel_circumference
    results['wheel_rpm'] = wheel_rpm
    results['gearbox_input_rpm'] = gearbox_input_rpm
    results['A'] = A  # Rolling resistance coefficient A
    results['B'] = B  # Rolling resistance coefficient B
    results['C'] = C  # Rolling resistance coefficient C
    results['rolling_resistance'] = rolling_resistance
    results['gradient_resistance'] = gradient_resistance
    results['curvature_resistance'] = curvature_resistance
    results['starting_resistance'] = starting_resistance
    results['total_resistance'] = total_resistance
    results['wheel_radius'] = wheel_radius
    results['required_total_torque'] = required_total_torque
    results['per_wheel_torque'] = per_wheel_torque
    results['per_axle_torque'] = per_axle_torque
    results['per_gearbox_input_torque'] = per_gearbox_input_torque
    results['per_gearbox_input_torque_kg_cm'] = per_gearbox_input_torque_kg_cm
    results['pressure_kg_cm2'] = pressure_kg_cm2
    results['motor_displacement_cc'] = motor_displacement
    results['per_motor_flow_rate_lpm'] = hydraulic_motor_flow

    # ===== PUMP CALCULATIONS =====
    # Calculate required pump specifications for each engine gear ratio
    prop_rpm_list = [inputs.get('max_vehicle_rpm', 0.0)]  # Engine RPM list
    vol_eff_pump_frac = inputs['vol_eff_pump'] / 100.0  # Pump volumetric efficiency

    if vol_eff_pump_frac == 0:
        raise ValueError("Pump Volumetric Efficiency cannot be 0.")

    # Calculate pump requirements for each gear combination
    for engine_gear in engine_gear_list:
        for max_vehicle_rpm_input in prop_rpm_list:
            # Validate gear ratios
            if engine_gear == 0 or gear_ratio == 0:
                raise ValueError("Engine or Axle Gear Ratio cannot be 0.")

            # Calculate pump RPM through gear train
            actual_prop_rpm = max_vehicle_rpm_input / engine_gear  # Engine RPM at this gear
            pump_rpm_from_prop = pto_gear_ratio * actual_prop_rpm  # Pump RPM

            if pump_rpm_from_prop <= 0:
                raise ValueError(f"Calculated pump RPM ({pump_rpm_from_prop:.2f}) is 0 or negative.")

            # Calculate required pump displacement
            # Flow = Displacement × RPM × Volumetric Efficiency
            # Therefore: Displacement = Flow / (RPM × Volumetric Efficiency)
            pump_denom = (pump_rpm_from_prop * vol_eff_pump_frac)
            if pump_denom == 0:
                raise ValueError("Calculated Pump RPM or Volumetric Efficiency is 0.")

            disp_L_rev = hydraulic_motor_flow / pump_denom  # Displacement in L/rev
            pump_disp = disp_L_rev * 1000.0  # Convert to cc/rev

            # Store pump results for this gear combination
            pump_results.append({
                'engine_gear_ratio': engine_gear,
                'max_vehicle_rpm_input': max_vehicle_rpm_input,
                'pump_rpm': pump_rpm_from_prop,
                'pump_disp_cc': pump_disp,
                'actual_prop_rpm': actual_prop_rpm
            })

    # ===== FINALIZE RESULTS =====
    results['pump_results'] = pump_results
    results['warnings'] = warnings
    return results

def calculate_speed_mode(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate achievable vehicle speed for given hydraulic motor and pump specifications.

    This function works backward from hydraulic specifications to determine what speed
    the vehicle can achieve, considering all gear ratios and system efficiencies.

    Args:
        inputs (Dict[str, Any]): Input parameters including:
            - axle_gear_box_ratio: Gear ratio between motor and axle
            - engine_gear_ratio_list: List of engine gear ratios
            - max_vehicle_rpm: Maximum vehicle engine RPM
            - vol_eff_pump: Pump volumetric efficiency in percentage
            - vol_eff_motor: Motor volumetric efficiency in percentage
            - pto_gear_ratio: PTO gear ratio
            - max_pump_rpm: Maximum allowable pump RPM
            - pump_disp_in: Pump displacement in cc/rev
            - motor_disp_in: Motor displacement in cc/rev
            - max_motor_rpm: Maximum allowable motor RPM
            - wheel_diameter: Wheel diameter in mm

    Returns:
        Dict[str, Any]: Results including:
            - Achievable speeds for each gear ratio
            - Flow rates and RPMs throughout the system
            - Warnings for components exceeding maximum RPMs

    Raises:
        ValueError: For invalid input parameters
    """
    # Initialize result containers
    results = {}
    warnings = []

    # Extract gear ratios with defaults
    axle_gear_box_ratio = inputs.get('axle_gear_box_ratio', 1.0)
    engine_gear_list = inputs.get('engine_gear_ratio_list', [1.0])

    # Input validation
    if axle_gear_box_ratio <= 0:
        raise ValueError("Axle Gearbox Ratio must be greater than 0.")

    # Engine RPM list (typically maximum RPM)
    prop_rpm_list = [inputs.get('max_vehicle_rpm', 0.0)]
    results_list = []  # Results for each gear combination

    # Convert efficiencies from percentage to decimal
    vol_eff_pump_frac = (inputs['vol_eff_pump'] / 100.0)
    vol_eff_motor_frac = (inputs['vol_eff_motor'] / 100.0)

    # Validate efficiencies
    if vol_eff_pump_frac == 0:
        raise ValueError("Pump Volumetric Efficiency cannot be 0.")
    if vol_eff_motor_frac == 0:
        raise ValueError("Motor Volumetric Efficiency cannot be 0.")

    # ===== CALCULATE SPEEDS FOR EACH GEAR COMBINATION =====
    for engine_gear in engine_gear_list:
        for max_vehicle_rpm_input in prop_rpm_list:
            # Validate gear ratios
            if engine_gear == 0 or axle_gear_box_ratio == 0:
                raise ValueError("Engine or Axle Gear Ratio cannot be 0.")

            # Calculate RPMs through the power train
            actual_prop_rpm = max_vehicle_rpm_input / engine_gear  # Engine RPM at this gear
            pump_rpm = actual_prop_rpm * inputs['pto_gear_ratio']  # Pump RPM

            # Check if pump RPM exceeds maximum
            if pump_rpm > inputs['max_pump_rpm']:
                warnings.append(f"Engine Gear {engine_gear}: Pump speed ({pump_rpm:.0f} RPM) exceeds max Pump RPM ({inputs['max_pump_rpm']:.0f} RPM).")

            # Calculate flow rates
            pump_flow_lpm = (inputs['pump_disp_in'] * pump_rpm * vol_eff_pump_frac) / 1000.0  # Pump flow in LPM
            motor_disp_lpm = inputs['motor_disp_in'] / 1000.0  # Motor displacement in LPM

            if motor_disp_lpm <= 0.0:
                raise ValueError("Motor displacement cannot be 0 for speed calculation.")

            # Calculate motor RPM from flow rate
            motor_speed_rpm = (pump_flow_lpm / motor_disp_lpm) * vol_eff_motor_frac

            # Check if motor RPM exceeds maximum
            if motor_speed_rpm > inputs['max_motor_rpm']:
                warnings.append(f"Engine Gear {engine_gear}: Motor speed ({motor_speed_rpm:.0f} RPM) exceeds max Motor RPM ({inputs['max_motor_rpm']:.0f} RPM).")

            # Calculate final drive RPMs and vehicle speed
            axle_shaft_rpm = motor_speed_rpm / axle_gear_box_ratio  # Axle shaft RPM
            wheel_circumference = (inputs['wheel_diameter'] * math.pi) / 1000.0  # Wheel circumference in meters

            if wheel_circumference <= 0:
                raise ValueError("Wheel Diameter must be greater than 0.")

            # Vehicle speed = (RPM × circumference) / 60 (convert RPM to RPS, then to m/s)
            speed_mps = (axle_shaft_rpm * wheel_circumference) / 60.0
            achievable_speed_kph = speed_mps * 3.6  # Convert m/s to km/h
            wheel_rpm = axle_shaft_rpm  # Wheel RPM = axle shaft RPM

            # Store results for this gear combination
            loop_res = {
                'engine_gear_ratio': engine_gear,
                'max_vehicle_rpm_input': max_vehicle_rpm_input,
                'actual_prop_rpm': actual_prop_rpm,
                'pump_rpm': pump_rpm,
                'pump_flow_lpm': pump_flow_lpm,
                'motor_disp_lpm': motor_disp_lpm,
                'motor_speed_rpm': motor_speed_rpm,
                'axle_shaft_rpm': axle_shaft_rpm,
                'wheel_circumference': wheel_circumference,
                'wheel_rpm': wheel_rpm,
                'achievable_speed_kph': achievable_speed_kph
            }
            results_list.append(loop_res)

    # ===== FINALIZE RESULTS =====
    results['speed_results_list'] = results_list  # All gear combinations
    results['warnings'] = warnings  # System warnings

    # Include the last result in top-level results for convenience
    if results_list:
        results.update(results_list[-1])

    return results