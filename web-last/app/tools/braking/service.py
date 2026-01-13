# =========================================
# Braking Tool Service Layer
# =========================================
# Orchestrates braking calculations and prepares data for reports and UI display.
# Acts as the business logic layer between API endpoints and core calculations.
#
# Purpose: Coordinate complex braking calculations for rail and road scenarios
# Used by: braking API endpoints and report generation
# Dependencies: core.py (calculations), constants.py (data), units.py (conversions)

import math  # Mathematical functions for calculations
from typing import Dict, Any, List, Tuple  # Type hints for function signatures
from .core import (  # Import core calculation functions
    calculate_max_rail_force,
    calculate_rail_scenario_forces,
    calculate_deceleration_and_distances,
    calculate_road_forces,
    calculate_gbr
)
from .constants import G, BRAKING_DATA  # Gravity constant and braking distance data
from .units import parse_list, calculate_angle, get_compliance, escape_latex  # Utility functions

def perform_braking_calculation(inputs: Dict[str, Any]) -> Tuple[List[Dict], Dict]:
    """
    Main orchestration function for braking calculations.

    This function coordinates all braking calculations for both rail and road modes,
    preparing data for both the results table display and PDF report generation.

    Args:
        inputs (Dict[str, Any]): User input parameters including:
            - mass_kg: Vehicle mass in kg
            - reaction_time: Driver reaction time in seconds
            - num_wheels: Number of wheels
            - rail_speed_input: Comma-separated rail speeds
            - rail_gradient_input: Comma-separated rail gradients
            - road_speed_input: Comma-separated road speeds (if Rail+Road mode)
            - road_gradient_input: Comma-separated road gradients
            - calc_mode: "Rail" or "Rail+Road"
            - Various other parameters for report generation

    Returns:
        Tuple[List[Dict], Dict]: (results_table_rows, context_for_reports)
            - results_table_rows: List of dictionaries for UI table display
            - context_for_reports: Dictionary with all data needed for PDF generation
    """
    # Initialize result containers
    results_table_rows = []  # Data for UI results table
    rail_detailed_calcs = []  # Detailed calculations for rail mode PDF
    road_detailed_calcs = []  # Detailed calculations for road mode PDF

    # Extract basic vehicle parameters
    mass_kg = inputs['mass_kg']  # Vehicle mass in kilograms
    weight_n = mass_kg * G  # Vehicle weight in Newtons (mass × gravity)
    reaction_time = inputs['reaction_time']  # Driver reaction time in seconds
    num_wheels = inputs['num_wheels']  # Number of wheels for force distribution

    # Calculate the maximum braking force required for rail mode
    # This is the worst-case scenario across all speeds in BRAKING_DATA
    max_rail_force = calculate_max_rail_force(mass_kg, reaction_time)

    # Prepare force capability table data (old_data_for_report)
    # This shows braking requirements for each speed in the standards
    old_data_for_report = {}
    for speed, dist in sorted(BRAKING_DATA.items()):
        v_ms = speed / 3.6  # Convert km/h to m/s for calculations
        # Required deceleration: v² = 2*a*distance => a = v²/(2*d)
        decel_required = (v_ms**2) / (2 * dist)
        # Required force: F = m*a
        force_required = mass_kg * decel_required

        # Store detailed data for each speed
        old_data_for_report[speed] = {
            'speed_ms': round(v_ms, 2),  # Speed in m/s
            'braking_distance': dist,  # Required braking distance in meters
            'deceleration': round(decel_required, 4),  # Required deceleration m/s²
            'reaction_distance': round(v_ms * reaction_time, 2),  # Distance during reaction time
            'total_stopping_distance': round((v_ms * reaction_time) + dist, 2),  # Total stopping distance
            'braking_force': round(force_required, 2)  # Required braking force in N
        }

    # ===== RAIL CALCULATIONS =====
    # Parse user input for rail speeds and gradients
    rail_speeds = parse_list(inputs['rail_speed_input'])  # List of speeds to calculate
    rail_gradients = parse_list(inputs['rail_gradient_input'])  # List of gradients to consider
    # Always include flat track (0% gradient) plus user-specified gradients
    rail_gradients_with_flat = sorted(list(set([0.0] + rail_gradients)))

    # Calculate braking performance for each gradient and scenario combination
    for grad_val in rail_gradients_with_flat:
        # Determine scenarios based on gradient
        scenarios = ["Straight Track"]  # Always include straight track
        if grad_val > 0:  # If there's a gradient, add uphill/downhill scenarios
            scenarios = ["Moving up", "Moving down"]

        # Calculate for each scenario and speed combination
        for scenario in scenarios:
            for speed in sorted(rail_speeds):
                v_ms = speed / 3.6  # Convert speed to m/s
                # Use gradient value (0 for straight track, actual value for uphill/downhill)
                current_grad = 0 if scenario == "Straight Track" else grad_val
                # Convert gradient to angle in degrees
                angle_deg = calculate_angle(current_grad, inputs['rail_gradient_type'])

                # Calculate forces for this rail scenario
                f_net, eff_grav = calculate_rail_scenario_forces(
                    max_rail_force, weight_n, angle_deg, scenario
                )

                # Calculate deceleration and stopping distances
                decel, braking_dist, reaction_dist, total_dist = calculate_deceleration_and_distances(
                    f_net, mass_kg, v_ms, reaction_time
                )

                # Check compliance with standards
                compliance = get_compliance(speed, total_dist)

                # Add row to results table for UI display
                results_table_rows.append({
                    "mode": "Rail",  # Mode identifier
                    "scenario": scenario,  # Track scenario
                    "speed": speed,  # Speed in km/h
                    "gradient": f"{current_grad} ({inputs['rail_gradient_type']})" if current_grad > 0 else "0",  # Gradient display
                    "gradient_value": current_grad,  # Numeric gradient value
                    "gravitational_force": round(weight_n * math.sin(math.radians(angle_deg)), 2),  # Gravity component
                    "applied_force": round(max_rail_force, 2),  # Maximum braking force
                    "net_force": round(f_net, 2),  # Net force available
                    "decel": round(decel, 2),  # Deceleration in m/s²
                    "dist": round(braking_dist, 2) if braking_dist < 99999 else "Inf",  # Braking distance
                    "total": round(total_dist, 2) if braking_dist < 99999 else "Inf",  # Total stopping distance
                    "status": compliance  # Compliance status
                })

                # Add detailed calculation data for PDF report generation
                rail_detailed_calcs.append({
                    'scenario': scenario,
                    'speed_kmh': speed,
                    'v_ms': round(v_ms, 2),
                    'v_ms_squared': round(v_ms**2, 2),
                    'gradient_value': current_grad,
                    'angle_deg': round(angle_deg, 2),
                    'mass_kg': mass_kg,
                    'weight_n': round(weight_n, 2),
                    'fmax': round(weight_n * math.sin(math.radians(angle_deg)), 2),
                    'f_g': round(eff_grav, 2),
                    'max_braking_force': round(max_rail_force, 2),
                    'f_net': round(f_net, 2),
                    'a_deceleration': round(decel, 2),
                    'a_deceleration_doubled': round(decel*2, 2),
                    'reaction_distance': round(reaction_dist, 2),
                    'braking_distance': round(braking_dist, 2),
                    'total_stopping_distance': round(total_dist, 2)
                })

    # ===== ROAD CALCULATIONS =====
    # Only perform road calculations if Rail+Road mode is selected
    if inputs['calc_mode'] == "Rail+Road":
        # Parse road-specific inputs
        road_speeds = parse_list(inputs['road_speed_input'])
        road_gradients = parse_list(inputs['road_gradient_input'])
        # Include flat road plus user gradients
        road_gradients = sorted(list(set([0.0] + road_gradients)))

        # Calculate road braking for each gradient and speed
        for grad_val in road_gradients:
            for speed in sorted(road_speeds):
                v_ms = speed / 3.6  # Convert to m/s
                # Convert gradient to angle
                angle_deg = calculate_angle(grad_val, inputs['road_gradient_type'])

                # Calculate road forces (friction-based braking)
                normal, grav, friction_f, net = calculate_road_forces(
                    weight_n, angle_deg, inputs['mu'], "Straight Track"
                )

                # Set up scenarios based on gradient
                if grad_val == 0:
                    scenarios = [{"name": "Straight Track", "grav_factor": 0}]
                else:
                    scenarios = [
                        {"name": "Moving up", "grav_factor": 1},    # Gravity increases load
                        {"name": "Moving down", "grav_factor": -1}  # Gravity reduces load
                    ]

                # Calculate for each scenario
                for scenario_dict in scenarios:
                    scenario = scenario_dict["name"]
                    # Adjust net force based on scenario
                    if scenario == "Moving up":
                        net = friction_f + grav  # Gravity increases braking requirement
                    elif scenario == "Moving down":
                        net = friction_f - grav  # Gravity reduces braking requirement

                    # Calculate distances for road mode
                    decel, braking_dist, reaction_dist, total_dist = calculate_deceleration_and_distances(
                        net, mass_kg, v_ms, reaction_time
                    )

                    # Format gradient display
                    gradient_display = f"{grad_val} ({inputs['road_gradient_type']})" if grad_val > 0 else "0"

                    # Add to results table
                    results_table_rows.append({
                        "mode": "Road",
                        "scenario": scenario,
                        "speed": speed,
                        "gradient": gradient_display,
                        "gradient_value": grad_val,
                        "gravitational_force": round(grav, 2),
                        "applied_force": round(friction_f, 2),
                        "net_force": round(net, 2),
                        "decel": round(decel, 2),
                        "dist": round(braking_dist, 2) if braking_dist < 99999 else "Inf",
                        "total": round(total_dist, 2) if total_dist < 99999 else "Inf",
                        "status": "N/A"  # Road mode doesn't have compliance standards
                    })

                    # Add to PDF context
                    road_detailed_calcs.append({
                        'scenario': scenario,
                        'gradient_value': grad_val,
                        'speed_kmh': speed,
                        'v_ms': round(v_ms, 2),
                        'v_ms_squared': round(v_ms**2, 2),
                        'mass_kg': mass_kg,
                        'weight_n': round(weight_n, 2),
                        'friction': inputs['mu'],
                        'angle_deg': round(angle_deg, 2),
                        'fmax': round(grav, 2),
                        'normal_force': round(normal, 2),
                        'fb_friction': round(friction_f, 2),
                        'f_g': round(grav, 2),
                        'f_net': round(net, 2),
                        'a_deceleration': round(decel, 2),
                        'a_deceleration_doubled': round(decel*2, 2),
                        'reaction_distance': round(reaction_dist, 2),
                        'braking_distance': round(braking_dist, 2),
                        'total_stopping_distance': round(total_dist, 2)
                    })

    # ===== BUILD CONTEXT FOR REPORTS =====
    # Prepare comprehensive context dictionary for PDF report generation

    # Get reference values for report (using maximum input speed)
    max_input_speed = max(rail_speeds) if rail_speeds else 0
    ref_v = max_input_speed / 3.6  # Reference speed in m/s

    # Find appropriate reference braking distance from standards
    ref_dist = 50  # Default fallback
    for s in sorted(BRAKING_DATA.keys(), reverse=True):
        if max_input_speed >= s:
            ref_dist = BRAKING_DATA[s]
            break

    # Calculate reference deceleration and force
    ref_decel = (ref_v**2) / (2 * ref_dist)
    ref_force = mass_kg * ref_decel
    gbr = calculate_gbr(max_rail_force, mass_kg)  # Gross Braking Ratio

    # Get downhill scenario data for report (most critical case)
    down_data = next((x for x in rail_detailed_calcs if x["scenario"] == "Moving down"), None)

    # Fallback calculation object if no downhill data
    calc_obj = down_data if down_data else {
        'mass_kg': mass_kg,
        'weight_n': round(weight_n, 2),
        'speed_kmh': max_input_speed,
        'v_ms': round(ref_v, 2),
        'max_braking_force': round(max_rail_force, 2),
        'angle_deg': 0,
        'fmax': 0,
        'f_g': 0,
        'f_net': round(max_rail_force, 2),
        'a_deceleration': round(ref_decel, 2),
        'gradient_value': 0
    }

    # Build comprehensive context dictionary for LaTeX template
    context = {
        # Document metadata
        'doc_no': escape_latex(inputs.get('doc_no', '')),
        'made_by': escape_latex(inputs.get('made_by', '')),
        'checked_by': escape_latex(inputs.get('checked_by', '')),
        'approved_by': escape_latex(inputs.get('approved_by', '')),

        # Basic vehicle parameters
        'mass_kg': mass_kg,
        'weight_n': round(weight_n, 2),
        'speed_kmh': max_input_speed,
        'v_ms': round(ref_v, 2),
        'reaction_time': reaction_time,
        'Reaction_distance': round(ref_v * reaction_time, 2),

        # Reference calculations
        'reference_speed_for_force': max_input_speed,
        'reference_braking_dist': ref_dist,
        'decel': round(ref_decel, 2),
        'totl_sto_distan': round((ref_v*reaction_time)+ref_dist, 2),
        'fb': round(ref_force, 2),
        'example_decel': round(ref_decel, 2),
        'example_fb': round(ref_force, 2),

        # Gradient information
        'gradient_input': max(rail_gradients) if rail_gradients else 0,
        'gradient_type': inputs.get('rail_gradient_type', ''),
        'road_gradient_input': max(parse_list(inputs.get('road_gradient_input', '0'))) if inputs.get('road_gradient_input') else 0,
        'road_gradient_type': inputs.get('road_gradient_type', ''),
        'road_angle_deg': round(calculate_angle(max(parse_list(inputs.get('road_gradient_input', '0'))) if inputs.get('road_gradient_input') else 0, inputs.get('road_gradient_type', 'Percentage (%)')), 2),

        # Wheel and friction parameters
        'number_of_wheels': num_wheels,
        'wheel_dia': inputs.get('wheel_dia', 0),
        'wheel_radius': inputs.get('wheel_dia', 0) / 2 if inputs.get('wheel_dia') else 0,
        'friction_coefficient': inputs.get('mu', 0.7),

        # Braking force calculations
        'max_braking_force': round(max_rail_force, 2),
        'min_braking_force': round(max_rail_force/num_wheels, 2) if num_wheels else 0,

        # Detailed calculation data for reports
        'old_data_for_report': old_data_for_report,
        'rail_detailed_calcs': rail_detailed_calcs,
        'road_detailed_calcs': road_detailed_calcs,

        # Specific values for downhill scenario
        'total_stopping_distance_ts_new__Moving_down': down_data['total_stopping_distance'] if down_data else 0,
        'fmax': down_data['fmax'] if down_data else 0,

        # Gross Braking Ratio
        'gbr': gbr,
        'gbr_value': gbr / 100,  # Decimal form
        'gbr_percentage': gbr,    # Percentage form

        # Additional data for templates
        'speed_list': rail_speeds,
        'standard_speed_inputs': old_data_for_report,
        'calc': calc_obj,

        # Display options
        'show_gbr': inputs.get('show_gbr', False),
        'show_straight': inputs.get('show_straight', True),
        'show_moving_up': inputs.get('show_moving_up', True),
        'show_moving_down': inputs.get('show_moving_down', True)
    }

    return results_table_rows, context