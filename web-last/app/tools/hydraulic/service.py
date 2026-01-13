"""
Hydraulic Tool Service Layer Module
==================================
Purpose:
    Orchestrates hydraulic calculations and prepares formatted reports.
    Acts as the business logic layer between API endpoints and core calculations.
Layer:
    Backend / Tools / Hydraulic / Service
Functions:
    - perform_hydraulic_calculation: Main orchestration function
    - format_displacement_report: Format displacement calculation results
    - format_speed_report: Format speed calculation results
Calculation Modes:
    - calc_cc: Displacement calculation mode
    - calc_speed: Speed calculation mode
Report Generation:
    - Text-based reports for web display
    - Structured data for DOCX report generation
    - Step-by-step calculation breakdowns
    - Professional engineering report formatting
Dependencies:
    - core.py: Pure mathematical calculations
    - API endpoints for data flow
    - DOCX builder for report generation
"""

from typing import Dict, Any, Tuple, Optional
from .core import calculate_displacement_mode, calculate_speed_mode

def perform_hydraulic_calculation(inputs: Dict[str, Any], inputs_raw: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
    """
    Main orchestration function for hydraulic calculations.

    Coordinates the complete hydraulic calculation workflow based on the selected mode.
    Routes to appropriate calculation functions and formats results for both web display
    and report generation.

    Args:
        inputs (Dict[str, Any]): Processed and validated input parameters
        inputs_raw (Dict[str, Any], optional): Original raw input data for report formatting

    Returns:
        Tuple[Dict[str, Any], str]:
            - results: Detailed calculation results dictionary
            - formatted_report: Human-readable text report

    Calculation Modes:
        - "calc_cc": Calculate motor displacement and pump requirements for target speed
        - "calc_speed": Calculate achievable speeds for given motor/pump specifications

    Results Structure:
        For calc_cc mode:
            - Motor displacement requirements
            - Pump specifications for each gear ratio
            - Flow rates and pressure requirements
            - Efficiency calculations

        For calc_speed mode:
            - Achievable speeds for each gear ratio
            - Power requirements
            - Efficiency analysis

    Report Format:
        - Markdown-style formatted text
        - Sectioned layout with headers
        - Step-by-step calculation breakdown
        - Input parameters summary
        - Results tables and analysis
    """
    if inputs['calc_mode'] == "calc_cc":
        # Calculate motor displacement and pump requirements
        results = calculate_displacement_mode(inputs)
        formatted_report = format_displacement_report(inputs, results, inputs_raw or {})
    else:
        # Calculate achievable speeds for given specifications
        results = calculate_speed_mode(inputs)
        formatted_report = format_speed_report(inputs, results, inputs_raw or {})

    return results, formatted_report

def format_displacement_report(inputs: Dict[str, Any], results: Dict[str, Any], inputs_raw: Dict[str, Any]) -> str:
    """
    Format displacement calculation results into a professional report.

    Creates a comprehensive text report for motor displacement calculations,
    including all input parameters, step-by-step calculations, and final
    motor/pump specifications.

    Args:
        inputs (Dict[str, Any]): Processed input parameters
        results (Dict[str, Any]): Calculation results from core functions
        inputs_raw (Dict[str, Any]): Original raw input data for display

    Returns:
        str: Formatted text report with sections:
            - Vehicle inputs summary
            - Hydraulic system inputs
            - Step-by-step calculations
            - Motor specifications
            - Pump requirements for each gear ratio
            - Efficiency analysis

    Report Sections:
        1. Vehicle Inputs: Weight, axles, speed, dimensions
        2. Hydraulic Inputs: Motor/pump counts, efficiencies, gear ratios
        3. Step-by-step Calculations: Physics and engineering formulas
        4. Results: Motor displacement, flow rates, power requirements
        5. Gear Analysis: Performance for each engine gear ratio
    """
    raw = inputs_raw
    output_lines = []
    output_lines.append("# Pump & Motor (cc) Calculation as per Vehicle")
    output_lines.append("\n--- VEHICLE INPUTS ---")
    output_lines.append(f"Vehicle Weight: {raw.get('weight')} t")
    output_lines.append(f"Number of axles: {raw.get('axles')}")
    output_lines.append(f"Target Speed: {raw.get('speed')} km/h")
    output_lines.append(f"Wheel Dia: {raw.get('wheel_diameter')} mm")
    """Format displacement calculation report"""
    raw = inputs_raw
    output_lines = []
    output_lines.append("# Pump & Motor (cc) Calculation as per Vehicle")
    output_lines.append("\n--- VEHICLE INPUTS ---")
    output_lines.append(f"Vehicle Weight: {raw.get('weight')} t")
    output_lines.append(f"Number of axles: {raw.get('axles')}")
    output_lines.append(f"Target Speed: {raw.get('speed')} km/h")
    output_lines.append(f"Wheel Dia: {raw.get('wheel_diameter')} mm")
    output_lines.append(f"Slope: {raw.get('slope_percent')} %")
    output_lines.append(f"Curve: {raw.get('curve_degree')} deg")
    output_lines.append(f"Axle Gear box Ratio: {raw.get('axle_gear_box_ratio')}")
    output_lines.append(f"max Vehicle RPM : {raw.get('max_vehicle_rpm')}")
    output_lines.append(f"PTO Gear Box Ratio: {raw.get('pto_gear_ratio')}")
    output_lines.append(f"Engine Gear Box Ratios: {raw.get('engine_gear_ratio')}")
    output_lines.append("\n--- HYDRAULIC MOTOR & PUMP INPUTS ---")
    output_lines.append(f"Total Hydraulic Motor: {raw.get('num_motors')}")
    output_lines.append(f"Hydraulic Motor / axle: {raw.get('per_axle_motor')}")
    output_lines.append(f"Pressure: {raw.get('pressure')} bar")
    output_lines.append(f"Motor Mechanical Efficiency: {raw.get('mech_eff_motor')} %")
    output_lines.append(f"Motor Volumetric Efficiency: {raw.get('vol_eff_motor')} %")
    output_lines.append(f"Pump Volumetric Efficiency: {raw.get('vol_eff_pump')} %")
    output_lines.append("\n--- RESULTS: STEP-BY-STEP CALCULATION (COMMON) ---")
    output_lines.append("\nStep 1: Vehicle Speed & Wheel RPM")
    output_lines.append(f"  Speed (m/s) = {results.get('speed_mps'):.2f} m/s")
    output_lines.append(f"  Wheel Circumference (m) = {results.get('wheel_circumference'):.3f} m")
    output_lines.append(f"  Wheel RPM = {results.get('wheel_rpm'):.2f} RPM")
    output_lines.append("\nStep 2: Resistance Forces (kN)")
    output_lines.append(f"  Rolling Resistance (kN) = {results.get('rolling_resistance'):.2f} kN")
    output_lines.append(f"  Gradient Resistance (kN) = {results.get('gradient_resistance'):.2f} kN")
    output_lines.append(f"  Curvature Resistance (kN) = {results.get('curvature_resistance'):.2f} kN")
    output_lines.append(f"  Starting Resistance (kN) = {results.get('starting_resistance'):.2f} kN")
    output_lines.append("  ---")
    output_lines.append(f"  Total Resistance (kN): {results.get('total_resistance'):.2f} kN")
    output_lines.append("  ---")
    output_lines.append("\nStep 3: Torque Requirements")
    output_lines.append(f"  Wheel Radius (m) = {results.get('wheel_radius'):.3f} m")
    output_lines.append(f"  Required Total Torque (Nm) = {results.get('required_total_torque'):.2f} Nm")
    output_lines.append(f"  Required Torque per Wheel (Nm) = {results.get('per_wheel_torque'):.2f} Nm/wheel")
    output_lines.append(f"  Required Torque per Axle (Nm) = {results.get('per_axle_torque'):.2f} Nm/axle")
    output_lines.append(f"  Required Motor Torque (Nm) = {results.get('per_gearbox_input_torque'):.2f} Nm")
    output_lines.append("\nStep 4: Motor Speed")
    output_lines.append("  Motor Speed (RPM) (gearbox input RPM):")
    output_lines.append(f"    = {results.get('wheel_rpm'):.2f} * {inputs.get('axle_gear_box_ratio')} = {results.get('gearbox_input_rpm'):.2f} RPM")
    output_lines.append("\nStep 5: Motor Displacement (New Formula)")
    output_lines.append(f"  Motor Torque (kg-cm) = {results.get('per_gearbox_input_torque_kg_cm'):.2f} kg-cm")
    output_lines.append(f"  Pressure (kg/cm2) = {results.get('pressure_kg_cm2'):.2f} kg/cm2")
    output_lines.append(f"  Motor Displacement (cc/rev) = {results.get('motor_displacement_cc'):.2f} cc/rev")
    output_lines.append("\nStep 6: Motor Flow Rate (New Formula)")
    output_lines.append(f"  Per Motor Flow Rate (LPM) = {results.get('per_motor_flow_rate_lpm'):.2f} LPM")
    output_lines.append("\n--- RESULTS: STEP-BY-STEP CALCULATION (PER GEAR) ---")
    output_lines.append("\nStep 7: Required Pump Displacement")
    pump_results_list = results.get('pump_results', [])
    if not pump_results_list:
        output_lines.append("    (No pump results were calculated)")
    for res in pump_results_list:
        max_vehicle_rpm_input = res.get('max_vehicle_rpm_input', 0)
        actual_prop_rpm = res.get('actual_prop_rpm', 0)
        calc_pump_rpm = res.get('pump_rpm', 0)
        final_disp_cc = res.get('pump_disp_cc', 0)
        engine_gear = res.get('engine_gear_ratio', 1.0)
        output_lines.append(f"\n  --- For Engine Gear {engine_gear:.2f} @ {max_vehicle_rpm_input:.0f} RPM ---")
        output_lines.append(f"    Actual Prop RPM = {actual_prop_rpm:.2f} RPM")
        output_lines.append(f"    Calculate Pump RPM = {calc_pump_rpm:.2f} RPM")
        output_lines.append(f"    Required Pump Displacement (cc/rev) = {final_disp_cc:.2f} cc/rev")
    return '\n'.join(output_lines)

def format_speed_report(inputs: Dict[str, Any], results: Dict[str, Any], inputs_raw: Dict[str, Any]) -> str:
    """Format speed calculation report"""
    raw = inputs_raw
    output_lines = []
    output_lines.append("# MODE 2 REPORT: SPEED CALCULATION")
    output_lines.append("\n--- VEHICLE INPUTS ---")
    output_lines.append(f"Wheel Dia: {raw.get('wheel_diameter')} mm")
    output_lines.append(f"Axle Gear box Ratio: {raw.get('axle_gear_box_ratio')}")
    output_lines.append(f"max Vehicle RPM: {raw.get('max_vehicle_rpm')}")
    output_lines.append(f"PTO Gear Box Ratio: {raw.get('pto_gear_ratio')}")
    output_lines.append(f"Engine Gear Box Ratios: {raw.get('engine_gear_ratio')}")
    output_lines.append("\n--- HYDRAULIC MOTOR & PUMP INPUTS ---")
    output_lines.append(f"Total Hydraulic Motor: {raw.get('num_motors')}")
    output_lines.append(f"Hydraulic Motor / axle: {raw.get('per_axle_motor')}")
    output_lines.append(f"Motor Volumetric Efficiency: {raw.get('vol_eff_motor')} %")
    output_lines.append(f"max Motor RPM: {raw.get('max_motor_rpm')} RPM")
    output_lines.append(f"Motor Displacement: {raw.get('motor_disp_in')} cc")
    output_lines.append(f"Pump Volumetric Efficiency: {raw.get('vol_eff_pump')} %")
    output_lines.append(f"max Limit of Pump RPM: {raw.get('max_pump_rpm')} RPM")
    output_lines.append(f"Pump Displacement: {raw.get('pump_disp_in')} cc")
    output_lines.append("\n--- CALCULATION RESULTS (PER ENGINE GEAR) ---")
    speed_results_list = results.get('speed_results_list', [])
    if not speed_results_list:
        output_lines.append("    (No speed results were calculated)")
    for res in speed_results_list:
        max_vehicle_rpm_input = res.get('max_vehicle_rpm_input', 0)
        actual_prop_rpm = res.get('actual_prop_rpm', 0)
        pump_rpm = res.get('pump_rpm', 0)
        pump_flow_lpm = res.get('pump_flow_lpm', 0)
        motor_speed_rpm = res.get('motor_speed_rpm', 0)
        axle_shaft_rpm = res.get('axle_shaft_rpm', 0)
        achievable_speed_kph = res.get('achievable_speed_kph', 0)
        engine_gear = res.get('engine_gear_ratio', 1.0)
        output_lines.append(f"\n  --- For Engine Gear {engine_gear:.2f} @ {max_vehicle_rpm_input:.0f} RPM ---")
        output_lines.append(f"  Actual Prop RPM = {actual_prop_rpm:.2f} RPM")
        output_lines.append(f"  Calculate Pump RPM = {pump_rpm:.2f} RPM")
        output_lines.append(f"  Calculate Pump Flow (LPM) = {pump_flow_lpm:.2f} LPM")
        output_lines.append(f"  Calculate Motor Speed (RPM) = {motor_speed_rpm:.2f} RPM")
        output_lines.append(f"  Calculate Axle/Wheel Speed (RPM) = {axle_shaft_rpm:.2f} RPM")
        output_lines.append(f"  ** Achievable Speed: {achievable_speed_kph:.2f} km/h **")
    if results.get('warnings'):
        output_lines.append("\n--- ⚠️ WARNINGS ---")
        for warning in results['warnings']:
            output_lines.append(f"- {warning}")
    return '\n'.join(output_lines)