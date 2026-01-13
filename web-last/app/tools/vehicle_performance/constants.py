# =========================================
# Vehicle Performance Tool Constants Module
# =========================================
# Physical constants, default values, and conversion factors for vehicle performance calculations.
#
# Purpose: Define all constant values used in locomotive performance analysis,
# including physical constants, default operating parameters, and unit conversions
# based on established engineering standards and typical railway applications.
#
# Engineering Standards:
# - Physical constants based on international standards (SI units)
# - Default values represent typical locomotive operating parameters
# - Conversion factors ensure consistent unit handling across calculations
#
# Used by: core.py (physics calculations), service.py (performance analysis)
# Dependencies: None (pure constants module)

# Fundamental Physical Constants
# Based on standard international values for engineering calculations

GRAVITY = 9.81                    # Standard gravity acceleration (m/s²)
AIR_DENSITY = 1.225              # Standard air density at sea level (kg/m³)
ROLLING_RESISTANCE_COEFFICIENT = 0.002  # Typical rolling resistance for steel wheels on rail

# Default Operating Parameters
# Typical values for locomotive performance analysis

DEFAULT_FRICTION_MU = 0.3        # Default coefficient of friction (wheel-rail adhesion)
DEFAULT_MIN_RPM = 500            # Default minimum engine speed (RPM)
DEFAULT_MAX_RPM = 2500           # Default maximum engine speed (RPM)

# Graph and Analysis Parameters
# Control the resolution and scope of performance calculations

SPEED_POINTS = 50                # Number of data points for speed performance curves
SLOPE_POINTS = 20                # Number of data points for slope analysis

# Unit Conversion Factors
# Ensure consistent unit handling across different calculation modules

KW_TO_HP = 1.341                 # Kilowatts to horsepower conversion (mechanical)
MPS_TO_KMH = 3.6                 # Meters per second to kilometers per hour
NM_TO_KGM = 0.10197              # Newton-meters to kilogram-meters (torque conversion)

# Note: All constants are based on established engineering standards
# and should be validated against specific locomotive specifications.
# Values may vary based on vehicle type, operating conditions, and
# local railway standards. Regular calibration against field measurements
# is recommended for operational accuracy.