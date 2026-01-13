# =========================================
# Tractive Effort Tool Constants Module
# =========================================
# Physical constants, resistance coefficients, and electrical parameters for tractive effort calculations.
#
# Purpose: Define all constant values used in train traction calculations,
# including rolling resistance coefficients, electrical system parameters,
# and resistance calculation constants based on railway engineering standards.
#
# Engineering Standards:
# - Rolling resistance coefficients based on UIC (International Union of Railways) standards
# - Electrical parameters for 25kV AC overhead electrification systems
# - Resistance constants derived from extensive field testing and research
#
# Used by: core.py (traction calculations), schemas.py (validation ranges)
# Dependencies: None (pure constants module)

# Rolling Resistance Coefficients (kg/tonne)
# These coefficients represent the force required to overcome friction between wheels and rails
# Higher at startup due to static friction, lower during running due to dynamic friction

# Starting Resistance (overcoming static friction)
WAGON_ROLLING_RESISTANCE_START = 4.0  # Wagons: higher resistance when stationary
LOCO_ROLLING_RESISTANCE_START = 6.0   # Locomotives: higher due to traction motors and gearing

# Running Resistance (dynamic friction during motion)
WAGON_ROLLING_RESISTANCE_RUNNING = 1.3505  # Wagons: lower resistance when moving
LOCO_ROLLING_RESISTANCE_RUNNING = 2.913    # Locomotives: higher due to mechanical losses

# Power Calculation Constants
# Used for converting mechanical power to electrical requirements

POWER_CONSTANT = 270  # Conversion factor for horsepower calculations (empirical)
OHE_VOLTAGE = 22500   # Overhead electrification voltage in volts (25kV AC system)
OHE_EFFICIENCY = 0.84  # Overall efficiency of overhead electric power transmission
POWER_FACTOR = 0.8    # Power factor for AC traction systems (lagging due to inductive loads)
CURRENT_CONSTANT = 735.5  # Empirical constant for current calculations

# Resistance Calculation Constants
# Constants for calculating additional resistances due to track geometry

GRADIENT_CONSTANT = 1000  # Gradient resistance conversion factor (kg/tonne per unit gradient)
CURVATURE_CONSTANT = 700  # Curvature resistance constant for radius-based calculations

# Note: All constants are based on established railway engineering standards
# and should be validated against local railway authority specifications.
# Values may vary based on specific rail conditions, vehicle types, and
# local operating practices. Regular calibration against field measurements
# is recommended for operational accuracy.