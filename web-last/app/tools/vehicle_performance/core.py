# =========================================
# Vehicle Performance Tool Core Calculations Module
# =========================================
# Pure mathematical functions for analyzing locomotive and vehicle performance.
# Contains physics-based calculations for resistive forces, tractive effort,
# speed calculations, and performance analysis across different conditions.
#
# Purpose: Calculate vehicle performance metrics including maximum speeds,
#          tractive forces, and performance tables for various operating conditions.
# Used by: vehicle_performance service and API endpoints
# Dependencies: constants.py (physical constants and conversion factors)

import math  # For trigonometric and power functions
from typing import Dict, Any, List, Tuple  # Type hints for better code documentation
from .constants import GRAVITY, AIR_DENSITY, ROLLING_RESISTANCE_COEFFICIENT, MPS_TO_KMH, KW_TO_HP

def calculate_resistive_forces(mass_kg: float, speed_kmh: float, slope_percent: float,
                              curve_radius_m: float, friction_mu: float) -> Dict[str, float]:
    """
    Calculate all resistive forces acting on the vehicle.

    This function computes the four main forces that oppose vehicle motion:
    rolling resistance, gradient resistance, curve resistance, and air resistance.

    Args:
        mass_kg (float): Vehicle mass in kilograms
        speed_kmh (float): Vehicle speed in km/h
        slope_percent (float): Road/rail gradient as percentage (e.g., 5.0 for 5%)
        curve_radius_m (float): Curve radius in meters (use large number for straight track)
        friction_mu (float): Coefficient of friction (typically 0.3-0.7 for rail)

    Returns:
        Dict[str, float]: Individual and total resistive forces in Newtons:
            - rolling_resistance: Force due to wheel/track deformation
            - gradient_resistance: Force due to slope (component of gravity)
            - curve_resistance: Force due to curved path (centrifugal effects)
            - air_resistance: Force due to air drag
            - total_resistance: Sum of all resistive forces

    Physics:
        - Rolling: F_rr = μ_rr × m × g (simplified coefficient)
        - Gradient: F_grad = m × g × (slope/100)
        - Curve: F_curve = m × v² / R (centripetal force requirement)
        - Air: F_air = 0.5 × ρ × v² × Cd × A (drag equation, simplified)

    Note:
        Curve resistance uses float('inf') for straight track (no curve resistance)
    """
    speed_mps = speed_kmh / MPS_TO_KMH  # Convert speed to m/s for calculations

    # Rolling resistance - force to deform wheels and track
    rolling_resistance = mass_kg * GRAVITY * ROLLING_RESISTANCE_COEFFICIENT

    # Gradient resistance - component of gravity along slope
    gradient_resistance = mass_kg * GRAVITY * (slope_percent / 100)

    # Curve resistance - additional force needed for curved path
    curve_resistance = 0.0
    if curve_radius_m > 0 and curve_radius_m != float('inf'):
        # Centripetal force requirement: F = m × v² / R
        curve_resistance = (mass_kg * GRAVITY * math.pow(speed_mps, 2)) / (curve_radius_m * GRAVITY)

    # Air resistance - aerodynamic drag
    air_resistance = 0.5 * AIR_DENSITY * math.pow(speed_mps, 2) * 1.0  # Cd × A = 1.0 (simplified)

    # Total resistance is sum of all opposing forces
    total_resistance = rolling_resistance + gradient_resistance + curve_resistance + air_resistance

    return {
        'rolling_resistance': rolling_resistance,    # Rolling resistance (N)
        'gradient_resistance': gradient_resistance,  # Gradient resistance (N)
        'curve_resistance': curve_resistance,        # Curve resistance (N)
        'air_resistance': air_resistance,            # Air resistance (N)
        'total_resistance': total_resistance         # Total resistance (N)
    }

def calculate_torque_from_power(power_kw: float, rpm: float) -> float:
    """
    Calculate engine torque from power and rotational speed.

    This function converts electrical/mechanical power to torque using the
    fundamental relationship between power, torque, and angular velocity.

    Args:
        power_kw (float): Power in kilowatts
        rpm (float): Rotational speed in revolutions per minute

    Returns:
        float: Torque in Newton-meters (Nm)

    Physics:
        Power (Watts) = Torque (Nm) × Angular Velocity (rad/s)
        Angular Velocity = RPM × 2π / 60
        Therefore: Torque = Power / Angular Velocity

    Formula:
        T = (P × 1000 × 60) / (RPM × 2π)
        Where P is in kW, result is in Nm

    Note:
        Returns 0 if RPM is 0 to avoid division by zero
    """
    if rpm == 0:
        return 0.0  # Avoid division by zero

    # Power (W) = Torque (Nm) × RPM × 2π / 60
    # Therefore: Torque = (Power × 1000 × 60) / (RPM × 2π)
    return (power_kw * 1000 * 60) / (rpm * 2 * math.pi)

def calculate_wheel_force(torque_nm: float, wheel_radius_m: float, gear_ratio: float,
                         mechanical_efficiency: float = 0.95) -> float:
    """
    Calculate tractive force at the wheels from engine torque.

    This function converts engine torque to the actual force available at the
    wheels, accounting for gear reduction and mechanical losses.

    Args:
        torque_nm (float): Engine torque in Newton-meters
        wheel_radius_m (float): Wheel radius in meters
        gear_ratio (float): Gear reduction ratio (engine RPM / wheel RPM)
        mechanical_efficiency (float): Mechanical efficiency (0.85-0.95 typical)

    Returns:
        float: Tractive force at wheels in Newtons

    Physics:
        Force = Torque × Gear Ratio × Efficiency / Wheel Radius
        This comes from: Power = Force × Velocity = Torque × Angular Velocity

    Note:
        Higher gear ratios provide more force but lower speeds
        Mechanical efficiency accounts for losses in transmission
    """
    return (torque_nm * gear_ratio * mechanical_efficiency) / wheel_radius_m

def calculate_max_speed_for_conditions(mass_kg: float, available_power_kw: float,
                                     slope_percent: float, curve_radius_m: float,
                                     gear_ratio: float, wheel_radius_m: float,
                                     friction_mu: float) -> float:
    """
    Calculate maximum achievable speed for given operating conditions.

    This function finds the highest speed where the vehicle's tractive force
    equals or exceeds the total resistive forces (equilibrium point).

    Args:
        mass_kg (float): Vehicle mass in kg
        available_power_kw (float): Available engine power in kW
        slope_percent (float): Road/rail gradient percentage
        curve_radius_m (float): Curve radius in meters
        gear_ratio (float): Transmission gear ratio
        wheel_radius_m (float): Wheel radius in meters
        friction_mu (float): Coefficient of friction

    Returns:
        float: Maximum speed in km/h where traction equals resistance

    Method:
        Iteratively tests speeds from 0-200 km/h in 5 km/h steps
        For each speed, calculates required tractive force vs available force
        Returns the highest speed where available force >= required force

    Physics:
        At equilibrium: Tractive Force = Total Resistive Force
        Tractive force decreases with speed (constant power assumption)
        Resistive force increases with speed (mainly air resistance)

    Note:
        Uses simplified constant-power model (real engines have torque curves)
        Returns 0 if no speed can overcome resistance at these conditions
    """
    max_speed_kmh = 0.0

    # Test speeds from 0 to 200 km/h to find equilibrium point
    for speed_kmh in range(0, 200, 5):  # 0 to 200 km/h in 5 km/h steps
        # Calculate total resistance at this speed
        resistances = calculate_resistive_forces(mass_kg, speed_kmh, slope_percent,
                                                curve_radius_m, friction_mu)
        total_resistance = resistances['total_resistance']

        # Calculate available tractive force at this speed
        # Convert vehicle speed to wheel RPM for torque calculation
        rpm = (speed_kmh / MPS_TO_KMH) * gear_ratio * 60 / (2 * math.pi * wheel_radius_m)

        if rpm > 0:
            # Calculate torque available at this RPM
            torque = calculate_torque_from_power(available_power_kw, rpm)

            # Calculate tractive force (gear_ratio already accounted for in RPM)
            tractive_force = calculate_wheel_force(torque, wheel_radius_m, 1.0)

            # Check if tractive force can overcome resistance
            if tractive_force >= total_resistance:
                max_speed_kmh = speed_kmh  # This speed is achievable
            else:
                break  # Higher speeds will have even less traction

    return max_speed_kmh

def calculate_traction_snapshot(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate traction performance snapshot for given vehicle inputs.

    This function provides a comprehensive overview of vehicle performance
    across different gears and operating conditions.

    Args:
        inputs (Dict[str, Any]): Vehicle parameters including:
            - loco_gvw_kg: Gross vehicle weight in kg
            - peak_power_kw: Maximum engine power in kW
            - wheel_dia_m: Wheel diameter in meters
            - gear_ratios: List of available gear ratios
            - friction_mu: Coefficient of friction
            - max_slope: Maximum slope percentage
            - max_curve: Minimum curve radius in meters

    Returns:
        Dict[str, Any]: Performance data for each gear containing:
            - max_speed_level_kmh: Max speed on level ground
            - max_speed_slope_kmh: Max speed on maximum slope
            - max_speed_curve_kmh: Max speed on minimum curve radius
            - gear_ratio: The gear ratio used

    Analysis:
        Calculates performance in three scenarios:
        1. Level ground (slope=0, curve=infinity)
        2. Maximum slope (given slope, straight track)
        3. Minimum curve radius (level ground, given curve)

    Note:
        Provides realistic performance expectations for different conditions
    """
    mass_kg = inputs['loco_gvw_kg']
    power_kw = inputs['peak_power_kw']
    wheel_radius_m = inputs['wheel_dia_m'] / 2  # Convert diameter to radius
    gear_ratios = inputs.get('gear_ratios', [1.0])  # Default single gear if not specified
    friction_mu = inputs.get('friction_mu', 0.3)    # Default friction coefficient

    results = {}

    # Calculate performance for each gear ratio
    for gear_ratio in gear_ratios:
        gear_key = f"gear_{gear_ratio}"

        # Scenario 1: Maximum speed on level ground
        max_speed_level = calculate_max_speed_for_conditions(
            mass_kg, power_kw, 0, float('inf'), gear_ratio, wheel_radius_m, friction_mu
        )

        # Scenario 2: Maximum speed on given slope (straight track)
        max_slope = inputs.get('max_slope', 0)
        max_speed_slope = calculate_max_speed_for_conditions(
            mass_kg, power_kw, max_slope, float('inf'), gear_ratio, wheel_radius_m, friction_mu
        )

        # Scenario 3: Maximum speed on given curve (level ground)
        max_curve = inputs.get('max_curve', float('inf'))
        max_speed_curve = calculate_max_speed_for_conditions(
            mass_kg, power_kw, 0, max_curve, gear_ratio, wheel_radius_m, friction_mu
        )

        # Store results for this gear
        results[gear_key] = {
            'max_speed_level_kmh': max_speed_level,     # Max speed on level ground
            'max_speed_slope_kmh': max_speed_slope,     # Max speed on slope
            'max_speed_curve_kmh': max_speed_curve,     # Max speed on curve
            'gear_ratio': gear_ratio                    # Gear ratio used
        }

    return results

def calculate_speed_vs_slope_table(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Calculate a performance table showing speed vs slope for different gears.

    This function generates a lookup table that shows how vehicle speed
    capability changes with slope for each available gear.

    Args:
        inputs (Dict[str, Any]): Vehicle parameters (same as traction_snapshot)

    Returns:
        List[Dict[str, Any]]: Table rows, each containing:
            - slope_percent: Slope percentage (0 to max_slope)
            - gear_X_speed_kmh: Max speed for gear ratio X at this slope

    Table Structure:
        - 11 rows (slope from 0% to max_slope% in 10 equal steps)
        - Columns for each gear ratio showing maximum speed
        - Useful for performance charts and operating guidelines

    Example Output:
        [
            {'slope_percent': 0.0, 'gear_1.0_speed_kmh': 120.0, 'gear_2.0_speed_kmh': 80.0},
            {'slope_percent': 1.0, 'gear_1.0_speed_kmh': 110.0, 'gear_2.0_speed_kmh': 75.0},
            ...
        ]
    """
    mass_kg = inputs['loco_gvw_kg']
    power_kw = inputs['peak_power_kw']
    wheel_radius_m = inputs['wheel_dia_m'] / 2
    gear_ratios = inputs.get('gear_ratios', [1.0])
    friction_mu = inputs.get('friction_mu', 0.3)
    max_slope = inputs.get('max_slope', 10)

    table_data = []

    # Create 11 slope points from 0% to max_slope%
    slopes = [i * max_slope / 10 for i in range(11)]  # 0, 10%, 20%, ..., 100% of max_slope

    # Calculate maximum speed for each slope and gear combination
    for slope in slopes:
        row = {'slope_percent': slope}

        for gear_ratio in gear_ratios:
            # Calculate max speed for this slope (straight track)
            max_speed = calculate_max_speed_for_conditions(
                mass_kg, power_kw, slope, float('inf'), gear_ratio, wheel_radius_m, friction_mu
            )
            row[f'gear_{gear_ratio}_speed_kmh'] = max_speed

        table_data.append(row)

    return table_data

def calculate_max_traction_without_slipping(mass_kg: float, friction_mu: float, num_axles: int) -> float:
    """
    Calculate maximum tractive force without wheel slipping.

    This function determines the absolute maximum force that can be transmitted
    to the track without the wheels slipping, based on friction limits.

    Args:
        mass_kg (float): Vehicle mass in kg
        friction_mu (float): Coefficient of friction between wheel and rail
        num_axles (int): Number of driving axles

    Returns:
        float: Maximum tractive force without slipping (N)

    Physics:
        Maximum force = Normal Force × Friction Coefficient
        Normal Force = Weight on driving axles
        Assumes uniform weight distribution

    Note:
        This is a theoretical maximum - real vehicles have lower practical limits
        due to traction control systems and wheel/rail conditions
    """
    # Simplified: assume all axles are driving axles with equal weight
    return mass_kg * GRAVITY * friction_mu

def calculate_max_traction_force(inputs: Dict[str, Any]) -> float:
    """
    Calculate maximum tractive force the locomotive can generate.

    This function determines the maximum force available from the powertrain,
    considering engine torque, gear ratios, and mechanical limitations.

    Args:
        inputs (Dict[str, Any]): Vehicle parameters including:
            - peak_power_kw: Maximum engine power
            - torque_curve: Dict of torque vs RPM (optional)
            - gear_ratios: Available gear ratios
            - wheel_dia_m: Wheel diameter
            - max_rpm: Maximum engine RPM (if no torque curve)

    Returns:
        float: Maximum tractive force in Newtons

    Method:
        1. Find maximum available torque (from curve or power calculation)
        2. Use highest gear ratio for maximum force (lowest speed)
        3. Convert torque to wheel force

    Physics:
        Higher gear ratios provide more force but lower speeds
        Maximum force occurs at maximum torque and highest gear ratio

    Note:
        This represents the powertrain capability, not traction limits
    """
    torque_curve = inputs.get('torque_curve', {})
    gear_ratios = inputs.get('gear_ratios', [1.0])
    wheel_radius_m = inputs['wheel_dia_m'] / 2

    if not torque_curve:
        # No torque curve provided - use peak power at maximum RPM
        power_kw = inputs['peak_power_kw']
        rpm = inputs.get('max_rpm', 2500)  # Default max RPM
        max_torque = calculate_torque_from_power(power_kw, rpm)
    else:
        # Find maximum torque from the provided torque curve
        max_torque = max(torque_curve.values()) if torque_curve else 0

    # Use the highest gear ratio for maximum force (lowest speed)
    max_gear_ratio = max(gear_ratios)

    # Calculate maximum tractive force
    return calculate_wheel_force(max_torque, wheel_radius_m, max_gear_ratio)