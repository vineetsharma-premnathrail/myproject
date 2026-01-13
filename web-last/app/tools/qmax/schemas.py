# =========================================
# Qmax Tool Schemas Module
# =========================================
# Pydantic data models for Qmax calculation input validation and type safety.
#
# Purpose: Define the structure and validation rules for Qmax calculation inputs,
# ensuring type safety and proper data validation before processing.
#
# Engineering Context:
# - Input parameters directly affect rail vehicle axle load calculations
# - Validation prevents invalid engineering parameters that could lead to unsafe designs
# - Type safety ensures consistent data handling across the calculation pipeline
#
# Used by: api.py (request validation), validation.py (input processing)
# Dependencies: pydantic (BaseModel for data validation)

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class QmaxInput(BaseModel):
    """
    Input schema for Qmax (Maximum Axle Load) calculations.

    This model validates user inputs for calculating maximum permissible axle loads
    for rail vehicles based on wheel-rail interaction parameters.

    Attributes:
        d (str): Worn rail diameter limit in millimeters (mm)
                - Represents the minimum allowable wheel diameter after wear
                - Critical parameter affecting contact stress distribution
                - Must be positive numeric value

        sigma_b_selection (str): Material strength selection from predefined options
                               - Rail bending stress limit based on steel grade
                               - Options: "880 N/mm²", "680 N/mm²", or "Custom"
                               - Determines allowable rail deflection under load

        sigma_b_custom (str): Custom rail bending stress value in N/mm²
                            - Used when sigma_b_selection is "Custom"
                            - Allows specialized material specifications
                            - Must be positive numeric value when used

        v_head (str): Safety factor for dynamic loading conditions
                     - Accounts for impact loads and material variations
                     - Typically 1.1-1.5 depending on application
                     - Must be positive numeric value

    Validation Rules:
    - All string inputs must be convertible to appropriate numeric types
    - d, sigma_b_custom, v_head must be positive when converted
    - sigma_b_selection must match predefined options or be "Custom"
    - Custom sigma_b value required when "Custom" is selected

    Example:
        >>> input_data = QmaxInput(
        ...     d="750",
        ...     sigma_b_selection="880 N/mm²",
        ...     sigma_b_custom="",
        ...     v_head="1.2"
        ... )
    """

    d: str = Field(..., description="Worn rail diameter limit in mm")
    sigma_b_selection: str = Field(..., description="Rail material strength selection")
    sigma_b_custom: str = Field("", description="Custom sigma_b value in N/mm²")
    v_head: str = Field(..., description="Safety factor for dynamic loading")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "d": "750",
                "sigma_b_selection": "880 N/mm²",
                "sigma_b_custom": "",
                "v_head": "1.2"
            }
        }
    )