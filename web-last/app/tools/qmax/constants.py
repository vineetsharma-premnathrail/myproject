# =========================================
# Qmax Tool Constants Module
# =========================================
# Physical constants, conversion factors, and material properties for Qmax calculations.
#
# Purpose: Define all constant values used in maximum axle load calculations,
# including material strength options, empirical constants, and unit conversions.
#
# Engineering Standards:
# - Rail bending stress limits based on international railway standards
# - Empirical constant C derived from extensive field testing and research
# - Safety factors account for dynamic loading and material variations
#
# Used by: core.py (calculation formulas), validation.py (input processing)
# Dependencies: None (pure constants module)

# Rail Material Strength Options (σB - Maximum allowable bending stress in N/mm²)
# These values represent different rail steel grades and their bending strength limits
SIGMA_B_OPTIONS = {
    "880 N/mm²": 880,  # High-strength rail steel (modern heavy-duty rails)
    "680 N/mm²": 680,  # Standard rail steel (conventional rail applications)
    "Custom": None     # User-defined value for specialized applications
}

# Empirical Constant for Qmax Formula
# Derived from extensive testing of rail-wheel interaction dynamics
# Accounts for contact stress distribution and dynamic loading effects
CONSTANT_C = 8.257e-7  # Dimensionless empirical coefficient

# Default Safety Factor (v_head)
# Conservative safety margin to account for:
# - Dynamic loading variations during vehicle operation
# - Material property uncertainties
# - Track condition variations
# - Manufacturing tolerances
DEFAULT_V_HEAD = 1.1  # 10% safety margin

# Unit Conversion Factor
# Converts from kiloNewtons (kN) to metric tonnes (t)
# Based on standard gravity acceleration: 1 tonne = 9.80665 kN
KN_TO_TONNES = 1 / 9.80665  # ≈ 0.10197 t/kN

# Note: All constants are based on established railway engineering standards
# and should be validated against local regulations for specific applications.