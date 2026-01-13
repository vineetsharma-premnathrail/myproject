# =========================================
# Load Distribution Tool Constants Module
# =========================================
# Safety limits, configuration types, and engineering standards for load distribution analysis.
#
# Purpose: Define all constant values used in load distribution calculations,
# including safety limits for different vehicle configurations and configuration types.
#
# Engineering Standards:
# - Safety limits based on international railway standards (UIC, EN, etc.)
# - Different limits for bogie vs truck configurations due to design differences
# - Delta Q/Q ratio ensures balanced load distribution for vehicle stability
#
# Used by: core.py (safety limit checks), schemas.py (validation constraints)
# Dependencies: None (pure constants module)

# Safety Limits for Load Distribution (ΔQ/Q ratios)
# These limits ensure balanced load distribution across wheels to prevent:
# - Wheel unloading during cornering or braking
# - Excessive rail wear from concentrated loads
# - Vehicle instability and derailment risks

# Bogie Configuration Safety Limit
# Bogie vehicles have articulated connections allowing more flexibility
# Higher limit reflects bogie design characteristics
BOGIE_DELTA_Q_LIMIT = 0.6  # 60% maximum allowable ΔQ/Q ratio

# Truck Configuration Safety Limit
# Truck vehicles have rigid frames requiring stricter load balance
# Lower limit ensures stability in rigid truck designs
TRUCK_DELTA_Q_LIMIT = 0.5  # 50% maximum allowable ΔQ/Q ratio

# Vehicle Configuration Types
# Defines the supported rail vehicle configurations for load analysis

# Bogie Configuration: Articulated design with separate wheelsets
# Allows independent wheel movement and higher load variation tolerance
CONFIG_BOGIE = "Bogie"

# Truck Configuration: Rigid frame design with fixed wheelbase
# Requires stricter load balance due to limited articulation
CONFIG_TRUCK = "Truck"

# Axle Configuration: Single axle analysis (for specialized applications)
# Used for individual axle load distribution studies
CONFIG_AXLE = "Axle"

# Note: Safety limits are based on established railway engineering standards
# and should be validated against local regulations for specific applications.
# The ΔQ/Q ratio represents the maximum allowable difference between
# maximum and minimum wheel loads as a percentage of the average load.