"""
Braking Tool Units and Utilities Module
======================================
Purpose:
    Utility functions for unit conversions, data parsing, and compliance checking.
    Handles the various unit systems used in braking calculations.
Layer:
    Backend / Tools / Braking / Utilities
Functions:
    - parse_list: Parse comma-separated strings into float lists
    - calculate_angle: Convert gradients to angles in degrees
    - get_compliance: Check stopping distances against EN standards
    - escape_latex: Sanitize strings for LaTeX PDF generation
Unit Conversions:
    Gradient Types:
        - Degree (°): Direct angle measurement
        - 1 in G: Gradient ratio (e.g., 1:30 = 1/30 = 0.0333)
        - Percentage (%): Rise over run percentage
    Speed: km/h to m/s conversions in core calculations
    Distance: Meters for all calculations
Compliance:
    - EN 15746-2:2021-05 standards for maximum stopping distances
    - Speed-dependent limits for safety compliance
    - Pass/Fail indicators for report generation
"""

import math
import re
from typing import List

def parse_list(input_str: str) -> List[float]:
    """
    Parse comma-separated string into list of floats.

    Safely converts user input strings (e.g., "10, 20, 30") into
    numerical lists for calculation processing. Handles various
    formatting issues and empty inputs gracefully.

    Args:
        input_str (str): Comma-separated numbers as string
            Examples: "10,20,30", "10, 20", "10", ""

    Returns:
        List[float]: List of parsed float values
            Empty list if input is empty or invalid

    Examples:
        >>> parse_list("10, 20, 30")
        [10.0, 20.0, 30.0]
        >>> parse_list("10")
        [10.0]
        >>> parse_list("")
        []
    """
    if not input_str:
        return []

    try:
        # Split by comma, strip whitespace, filter empty strings, convert to float
        return [float(x.strip()) for x in str(input_str).split(',') if x.strip()]
    except (ValueError, AttributeError):
        # Return empty list for any parsing errors
        return []

def calculate_angle(gradient_val: float, gradient_type: str) -> float:
    """
    Convert gradient value to angle in degrees.

    Handles different gradient measurement systems used in rail engineering:
    - Degrees: Direct angle measurement
    - 1 in G: Gradient ratio (e.g., 1:30 means 1 unit rise per 30 units run)
    - Percentage: Rise over run as percentage

    Args:
        gradient_val (float): The gradient value to convert
        gradient_type (str): Type of gradient measurement
            - "Degree (°)": Direct degrees
            - "1 in G": Gradient ratio
            - "Percentage (%)": Percentage

    Returns:
        float: Angle in degrees (0-90° range)

    Examples:
        >>> calculate_angle(5.0, "Degree (°)")
        5.0
        >>> calculate_angle(30.0, "1 in G")  # 1:30 gradient
        1.91  # approximately arctan(1/30)
        >>> calculate_angle(2.0, "Percentage (%)")
        1.15  # approximately arctan(2/100)
    """
    if gradient_val == 0:
        return 0.0

    if gradient_type == "Degree (°)":
        # Direct angle measurement
        return float(gradient_val)
    elif gradient_type == "1 in G":
        # Convert gradient ratio to angle
        # 1 in G means 1 unit rise per G units run
        # Angle = arctan(1/G)
        return math.degrees(math.atan(1 / gradient_val)) if gradient_val != 0 else 0
    else:  # Percentage
        # Convert percentage to angle
        # Percentage means (rise/run) * 100
        # Angle = arctan(percentage/100)
        return math.degrees(math.atan(gradient_val / 100))

def get_compliance(speed: float, total_dist: float) -> str:
    """
    Check if stopping distance complies with EN standards.

    Compares calculated stopping distance against maximum allowable
    distances defined in DIN EN 15746-2:2021-05 standards.

    Args:
        speed (float): Vehicle speed in km/h
        total_dist (float): Calculated stopping distance in meters

    Returns:
        str: Compliance status message
            - "✓ Standard Followed" if within limits
            - "✗ Standard Exceeded" if exceeds limits
            - "Standard Not Found" if no standard defined for speed

    Examples:
        >>> get_compliance(30, 45)
        '✓ Standard Followed'
        >>> get_compliance(30, 60)
        '✗ Standard Exceeded'
    """
    from .constants import MAX_STOPPING_DISTANCES

    # Find the appropriate speed limit (use highest speed limit that is <= current speed)
    allowed_distance = None
    for limit_speed in sorted(MAX_STOPPING_DISTANCES.keys(), reverse=True):
        if speed >= limit_speed:
            allowed_distance = MAX_STOPPING_DISTANCES[limit_speed]
            break

    if allowed_distance is None:
        return "Standard Not Found"

    if total_dist <= allowed_distance:
        return "✓ Standard Followed"
    else:
        return "✗ Standard Exceeded"

def escape_latex(s: str) -> str:
    """
    Escape special LaTeX characters for PDF report generation.

    Sanitizes text strings to prevent LaTeX compilation errors
    when including user input in PDF reports.

    Args:
        s (str): Input string that may contain LaTeX special characters

    Returns:
        str: LaTeX-safe string with special characters escaped

    Examples:
        >>> escape_latex("User & Company_Name")
        'User \\& Company\\_Name'
    """
    if not isinstance(s, str):
        return s

    # LaTeX special characters that need escaping
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }

    # Escape each special character
    result = str(s)
    for char, escape_seq in latex_special_chars.items():
        result = result.replace(char, escape_seq)

    return result
    mapping = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}', '\\': r'\textbackslash{}', ';': r'\;', ':': r'\:',
    }
    return re.sub(r'[&%$#_{}~^;:\\\\]', lambda m: mapping.get(m.group(0)), s)