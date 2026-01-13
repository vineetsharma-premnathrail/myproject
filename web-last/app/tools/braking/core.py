# =========================================
# Braking Tool Core Calculations Module
# =========================================
# Pure mathematical functions for braking force calculations.
# Contains all the physics and engineering formulas for rail and road braking.
# No I/O operations, no formatting - just pure calculations.
#
# Purpose: Calculate braking forces, deceleration, distances for rail and road vehicles
# Used by: braking service and API endpoints
# Dependencies: constants.py (braking data), units.py (unit conversions)

import math  # Mathematical functions (sin, cos, radians, etc.)
from typing import Dict, Any, List, Tuple  # Type hints for better code documentation
from .constants import G, BRAKING_DATA  # Gravity constant and braking distance data
from .units import parse_list, calculate_angle  # Unit conversion utilities

def calculate_max_rail_force(mass_kg: float, reaction_time: float) -> float:
    """
    Calculate the maximum braking force required for rail mode.

    This function iterates through all speed/distance pairs in BRAKING_DATA
    to find the worst-case scenario (highest required braking force).

    Physics: F = m * a, where a = v²/(2*d) from kinematic equation v² = u² + 2as

    Args:
        mass_kg (float): Vehicle mass in kilograms
        reaction_time (float): Driver reaction time in seconds (not used in this calc)

    Returns:
        float: Maximum braking force in Newtons required for safe stopping
    """
    max_force = 0.0  # Initialize with zero
    # Iterate through all speed/distance pairs in braking data
    for speed, dist in sorted(BRAKING_DATA.items()):
        v_ms = speed / 3.6  # Convert km/h to m/s
        # Calculate required deceleration: v² = 2*a*distance => a = v²/(2*d)
        decel_required = (v_ms**2) / (2 * dist)
        # Calculate force required: F = m*a
        force_required = mass_kg * decel_required
        # Keep track of the maximum force needed
        if force_required > max_force:
            max_force = force_required
    return max_force

def calculate_rail_scenario_forces(
    max_braking_force: float,
    weight_n: float,
    angle_deg: float,
    scenario: str
) -> Tuple[float, float]:
    """
    Calculate net force and effective gravity for different rail scenarios.

    Rail vehicles experience different forces based on track gradient:
    - Straight: Only braking force needed
    - Uphill: Braking + gravity component (harder to stop)
    - Downhill: Braking - gravity component (easier to stop)

    Args:
        max_braking_force (float): Maximum braking force from calculate_max_rail_force
        weight_n (float): Vehicle weight in Newtons (mass * gravity)
        angle_deg (float): Track gradient angle in degrees
        scenario (str): "Straight Track", "Moving up", or "Moving down"

    Returns:
        Tuple[float, float]: (net_force, effective_gravity_force)
    """
    # Calculate gravity component along the slope: F_grav = weight * sin(θ)
    grav_force_slope = weight_n * math.sin(math.radians(angle_deg))

    if scenario == "Straight Track":
        # No slope effect - only braking force needed
        f_net = max_braking_force
        eff_grav = 0
    elif scenario == "Moving up":
        # Uphill - gravity opposes motion, increases required braking force
        f_net = max_braking_force + grav_force_slope
        eff_grav = grav_force_slope
    elif scenario == "Moving down":
        # Downhill - gravity aids motion, reduces required braking force
        f_net = max_braking_force - grav_force_slope
        eff_grav = grav_force_slope
    else:
        # Invalid scenario - raise error
        raise ValueError(f"Invalid scenario: {scenario}. Must be 'Straight Track', 'Moving up', or 'Moving down'")

    return f_net, eff_grav

def calculate_deceleration_and_distances(
    f_net: float,
    mass_kg: float,
    v_ms: float,
    reaction_time: float
) -> Tuple[float, float, float, float]:
    """
    Calculate deceleration, braking distance, reaction distance, and total stopping distance.

    Uses kinematic equations to calculate stopping distances:
    - Reaction distance = speed × reaction time
    - Braking distance = (v²)/(2×deceleration)
    - Total distance = reaction + braking distance

    Args:
        f_net (float): Net force available for braking
        mass_kg (float): Vehicle mass in kg
        v_ms (float): Initial speed in m/s
        reaction_time (float): Driver reaction time in seconds

    Returns:
        Tuple[float, float, float, float]: (deceleration, braking_dist, reaction_dist, total_dist)
    """
    # Calculate deceleration: a = F/m (Newton's second law)
    decel = abs(f_net / mass_kg) if mass_kg > 0 else 0.0

    if decel > 0 and v_ms > 0:
        # Braking distance: v² = u² + 2as => s = (0 - v²)/(2a) = -v²/(2a)
        braking_dist = abs((0 - v_ms**2) / (2 * decel))
    else:
        braking_dist = 0.0

    # Reaction distance: distance traveled during reaction time at constant speed
    reaction_dist = v_ms * reaction_time
    # Total stopping distance
    total_dist = reaction_dist + braking_dist

    return decel, braking_dist, reaction_dist, total_dist

def calculate_road_forces(
    weight_n: float,
    angle_deg: float,
    mu: float,
    scenario: str
) -> Tuple[float, float, float, float]:
    """
    Calculate forces for road mode braking (friction-based).

    Road vehicles use tire friction for braking. The maximum braking force
    is limited by the coefficient of friction between tires and road.

    Args:
        weight_n (float): Vehicle weight in Newtons
        angle_deg (float): Road gradient angle in degrees
        mu (float): Coefficient of friction between tires and road
        scenario (str): "Straight Track", "Moving up", or "Moving down"

    Returns:
        Tuple[float, float, float, float]: (normal_force, gravity_force, friction_force, net_force)
    """
    # Normal force: component of weight perpendicular to road surface
    normal = weight_n * math.cos(math.radians(angle_deg))
    # Gravity force component parallel to road surface
    grav = weight_n * math.sin(math.radians(angle_deg))
    # Maximum friction force available: F_friction = μ × F_normal
    friction_f = mu * normal

    if scenario == "Straight Track":
        # No slope - friction force is the net braking force
        net = friction_f
    elif scenario == "Moving up":
        # Uphill - gravity increases the load, increasing friction
        net = friction_f + grav
    elif scenario == "Moving down":
        # Downhill - gravity reduces the effective braking force
        net = friction_f - grav
    else:
        # Invalid scenario - raise error
        raise ValueError(f"Invalid scenario: {scenario}. Must be 'Straight Track', 'Moving up', or 'Moving down'")

    return normal, grav, friction_f, net

def calculate_gbr(max_braking_force: float, mass_kg: float) -> float:
    """
    Calculate Gross Braking Ratio (GBR).

    GBR is the ratio of braking force to vehicle weight, expressed as a percentage.
    Higher GBR means better braking capability.

    Formula: GBR = (Braking Force / Vehicle Weight) × 100%

    Args:
        max_braking_force (float): Maximum braking force in Newtons
        mass_kg (float): Vehicle mass in kg

    Returns:
        float: Gross Braking Ratio as percentage (rounded to 2 decimal places)
    """
    # GBR = (F_brake / (mass × g)) × 100%
    return round((max_braking_force / (mass_kg * G)) * 100, 2) if mass_kg > 0 else 0