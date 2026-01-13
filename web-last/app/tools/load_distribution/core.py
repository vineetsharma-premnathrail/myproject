# =========================================
# Load Distribution Tool Core Calculations Module
# =========================================
# Pure mathematical functions for load distribution analysis on rail vehicles.
# Contains calculations for axle load distribution, wheel loads, and safety metrics.
# No I/O operations, no formatting - just pure calculations.
#
# Purpose: Analyze load distribution across axles and wheels for rail vehicle safety
# Used by: load_distribution service and API endpoints
# Dependencies: constants.py (safety limits and configuration)

from typing import Dict, Any  # Type hints for better code documentation
from .constants import BOGIE_DELTA_Q_LIMIT, TRUCK_DELTA_Q_LIMIT, CONFIG_BOGIE  # Safety limits and config types

def calculate_front_rear_loads(total_load: float, front_percent: float) -> tuple[float, float]:
    """
    Calculate the load distribution between front and rear axles.

    This function splits the total vehicle load between front and rear axles
    based on the specified front axle percentage.

    Args:
        total_load (float): Total vehicle load in appropriate units (tonnes/kN)
        front_percent (float): Percentage of total load carried by front axle (0-100)

    Returns:
        tuple[float, float]: (front_load, rear_load) - Load on each axle

    Example:
        If total_load = 100 and front_percent = 60, returns (60.0, 40.0)
    """
    front_load = (front_percent / 100) * total_load  # Front axle load
    rear_load = total_load - front_load              # Rear axle load (remainder)
    return front_load, rear_load

def calculate_wheel_loads(front_load: float, rear_load: float, q1_percent: float, q3_percent: float) -> Dict[str, float]:
    """
    Calculate individual wheel loads (Q1, Q2, Q3, Q4) for a two-axle vehicle.

    Rail vehicles typically have two axles (front and rear), each with two wheels.
    This function distributes the axle loads to individual wheels based on
    the specified load distribution percentages.

    Wheel numbering convention:
    - Q1: Front axle, left wheel
    - Q2: Front axle, right wheel
    - Q3: Rear axle, left wheel
    - Q4: Rear axle, right wheel

    Args:
        front_load (float): Total load on front axle
        rear_load (float): Total load on rear axle
        q1_percent (float): Percentage of front axle load on Q1 wheel (0-100)
        q3_percent (float): Percentage of rear axle load on Q3 wheel (0-100)

    Returns:
        Dict[str, float]: Wheel loads with keys 'Q1', 'Q2', 'Q3', 'Q4'

    Note:
        Q2 = front_load - Q1, Q4 = rear_load - Q3 (force balance)
    """
    # Calculate Q1 (front left wheel) as percentage of front axle load
    q1_val = (q1_percent / 100) * front_load
    # Q2 (front right wheel) gets the remaining front axle load
    q2_val = front_load - q1_val

    # Calculate Q3 (rear left wheel) as percentage of rear axle load
    q3_val = (q3_percent / 100) * rear_load
    # Q4 (rear right wheel) gets the remaining rear axle load
    q4_val = rear_load - q3_val

    return {
        "Q1": q1_val,  # Front left wheel
        "Q2": q2_val,  # Front right wheel
        "Q3": q3_val,  # Rear left wheel
        "Q4": q4_val   # Rear right wheel
    }

def find_min_max_q_values(q_values: Dict[str, float]) -> tuple[str, float, str, float]:
    """
    Find the minimum and maximum wheel loads from the Q values.

    This identifies which wheel carries the lightest load (QL) and which
    carries the heaviest load (QH), which is important for safety analysis.

    Args:
        q_values (Dict[str, float]): Dictionary with keys 'Q1', 'Q2', 'Q3', 'Q4'

    Returns:
        tuple[str, float, str, float]: (ql_name, ql_value, qh_name, qh_value)
            - ql_name: Name of wheel with minimum load ('Q1', 'Q2', 'Q3', or 'Q4')
            - ql_value: Minimum load value
            - qh_name: Name of wheel with maximum load
            - qh_value: Maximum load value
    """
    # Find wheel with minimum load
    ql_name = min(q_values, key=lambda k: q_values[k])  # Key with minimum value
    ql_value = q_values[ql_name]               # Minimum load value

    # Find wheel with maximum load
    qh_name = max(q_values, key=lambda k: q_values[k])  # Key with maximum value
    qh_value = q_values[qh_name]               # Maximum load value

    return ql_name, ql_value, qh_name, qh_value

def calculate_average_heavy_axle_load(q_values: Dict[str, float], front_load: float, rear_load: float) -> tuple[str, float]:
    """
    Calculate the average load on the heavier axle (Q value).

    In load distribution analysis, Q represents the average load on the axle
    that carries more weight. This is used in safety calculations to ensure
    load distribution doesn't exceed allowable limits.

    Args:
        q_values (Dict[str, float]): Individual wheel loads
        front_load (float): Total front axle load
        rear_load (float): Total rear axle load

    Returns:
        tuple[str, float]: (formula_string, q_value)
            - formula_string: Shows which wheels were averaged ("(Q1 + Q2) / 2" or "(Q3 + Q4) / 2")
            - q_value: Average load on the heavier axle

    Note:
        If front_load >= rear_load, uses front axle (Q1 + Q2) / 2
        If rear_load > front_load, uses rear axle (Q3 + Q4) / 2
    """
    if front_load >= rear_load:
        # Front axle is heavier - average Q1 and Q2
        q_formula_str = "(Q1 + Q2) / 2"
        q_value = (q_values["Q1"] + q_values["Q2"]) / 2
    else:
        # Rear axle is heavier - average Q3 and Q4
        q_formula_str = "(Q3 + Q4) / 2"
        q_value = (q_values["Q3"] + q_values["Q4"]) / 2

    return q_formula_str, q_value

def calculate_safety_metrics(q_value: float, ql_value: float, config_type: str) -> Dict[str, Any]:
    """
    Calculate safety metrics and determine if load distribution is acceptable.

    The key safety metric is ΔQ/Q, which measures the load imbalance relative
    to the average load on the heavier axle. This must not exceed regulatory limits.

    Safety Criteria:
    - ΔQ = Q - QL (difference between average heavy axle load and minimum wheel load)
    - ΔQ/Q = ΔQ ÷ Q (normalized imbalance ratio)
    - Must be ≤ limit (different for bogie vs truck configurations)

    Args:
        q_value (float): Average load on heavier axle
        ql_value (float): Minimum wheel load
        config_type (str): Vehicle configuration ("bogie" or "truck")

    Returns:
        Dict[str, Any]: Safety analysis results containing:
            - delta_q: Absolute load difference (Q - QL)
            - delta_q_by_q: Normalized imbalance ratio (ΔQ/Q)
            - limit: Regulatory limit for this configuration
            - status: "success" or "fail"
            - status_msg: Human-readable result message
    """
    # Calculate load imbalance
    delta_q = q_value - ql_value  # Absolute difference
    delta_q_by_q = delta_q / q_value if q_value != 0 else 0  # Normalized ratio

    # Get regulatory limit based on vehicle type
    limit = BOGIE_DELTA_Q_LIMIT if config_type == CONFIG_BOGIE else TRUCK_DELTA_Q_LIMIT

    # Determine pass/fail status
    if delta_q_by_q <= limit:
        status = "success"
        status_msg = f"PASS: ΔQ/Q ({delta_q_by_q:.2%}) is within the {limit:.0%} limit."
    else:
        status = "fail"
        status_msg = f"FAIL: ΔQ/Q ({delta_q_by_q:.2%}) exceeds the {limit:.0%} limit."

    return {
        'delta_q': delta_q,           # Absolute load difference
        'delta_q_by_q': delta_q_by_q, # Normalized imbalance ratio
        'limit': limit,               # Regulatory limit
        'status': status,             # Pass/fail status
        'status_msg': status_msg      # Human-readable message
    }

def perform_load_distribution_calculation(config_type: str, total_load: float, front_percent: float,
                                        q1_percent: float, q3_percent: float) -> Dict[str, Any]:
    """
    Main calculation function that orchestrates all load distribution analysis.

    This function performs the complete load distribution analysis by calling
    all the individual calculation functions in the correct sequence.

    Args:
        config_type (str): Vehicle configuration ("bogie" or "truck")
        total_load (float): Total vehicle load
        front_percent (float): Percentage of load on front axle (0-100)
        q1_percent (float): Percentage of front axle load on Q1 wheel (0-100)
        q3_percent (float): Percentage of rear axle load on Q3 wheel (0-100)

    Returns:
        Dict[str, Any]: Complete analysis results including:
            - Individual wheel loads (Q1, Q2, Q3, Q4)
            - Axle loads (front_load, rear_load)
            - Min/max wheel analysis (ql_name, ql_value, qh_name, qh_value)
            - Average heavy axle load (q_formula_str, q_value)
            - Safety metrics and pass/fail status
    """
    # Step 1: Calculate front and rear axle loads
    front_load, rear_load = calculate_front_rear_loads(total_load, front_percent)

    # Step 2: Calculate individual wheel loads
    q_values = calculate_wheel_loads(front_load, rear_load, q1_percent, q3_percent)

    # Step 3: Find minimum and maximum wheel loads
    ql_name, ql_value, qh_name, qh_value = find_min_max_q_values(q_values)

    # Step 4: Calculate average load on heavier axle
    q_formula_str, q_value = calculate_average_heavy_axle_load(q_values, front_load, rear_load)

    # Step 5: Calculate safety metrics and determine pass/fail
    safety_metrics = calculate_safety_metrics(q_value, ql_value, config_type)

    # Step 6: Combine all results into comprehensive output
    results = {
        'q_values': q_values,        # Individual wheel loads
        'front_load': front_load,    # Front axle total load
        'rear_load': rear_load,      # Rear axle total load
        'ql_name': ql_name,          # Wheel with minimum load
        'ql_value': ql_value,        # Minimum load value
        'qh_name': qh_name,          # Wheel with maximum load
        'qh_value': qh_value,        # Maximum load value
        'q_formula_str': q_formula_str,  # Formula used for Q calculation
        'q_value': q_value,          # Average load on heavier axle
        **safety_metrics              # Safety analysis results
    }

    return results