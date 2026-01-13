# =========================================
# Load Distribution Tool Schemas Module
# =========================================
# Pydantic data models for load distribution input validation and type safety.
#
# Purpose: Define the structure and validation rules for load distribution inputs,
# ensuring type safety and proper validation before engineering calculations.
#
# Engineering Context:
# - Input parameters directly affect vehicle stability and safety analysis
# - Validation prevents invalid load distribution scenarios
# - Type safety ensures consistent data handling across calculation pipeline
#
# Used by: api.py (request validation), validation.py (input processing)
# Dependencies: pydantic (BaseModel for validation), constants.py (CONFIG_*)

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Literal
from .constants import CONFIG_BOGIE, CONFIG_TRUCK

class LoadDistributionInput(BaseModel):
    """
    Input schema for load distribution analysis in rail vehicles.

    This model validates user inputs for analyzing load distribution across
    axles and wheels in rail vehicles to ensure safe operation and compliance
    with railway safety standards.

    Attributes:
        config_type (Literal["Bogie", "Truck", "Axle"]): Vehicle configuration type
                    - "Bogie": Articulated bogie design (higher load variation tolerance)
                    - "Truck": Rigid truck design (stricter load balance required)
                    - "Axle": Single axle analysis (specialized applications)

        total_load (float): Total vehicle load in tonnes
                    - Must be positive (physical constraint)
                    - Represents gross vehicle weight for analysis

        front_percent (float): Percentage of total load carried by front axle (0-100%)
                      - Determines longitudinal load distribution
                      - Affects vehicle balance and braking performance

        q1_percent (float): Percentage of front axle load carried by Q1 wheel (0-100%)
                   - Q1: Front axle, left wheel (driver's side)
                   - Determines lateral load distribution on front axle

        q3_percent (float): Percentage of rear axle load carried by Q3 wheel (0-100%)
                   - Q3: Rear axle, left wheel (driver's side)
                   - Determines lateral load distribution on rear axle

    Validation Rules:
    - config_type: Must be one of the predefined configuration types
    - total_load: Must be positive (represents physical vehicle weight)
    - front_percent: Must be between 0-100% (load distribution constraint)
    - q1_percent, q3_percent: Must be between 0-100% (wheel load distribution)
    - All numeric values converted to appropriate float types

    Wheel Load Convention:
    - Q1: Front axle, left wheel (when facing direction of travel)
    - Q2: Front axle, right wheel
    - Q3: Rear axle, left wheel
    - Q4: Rear axle, right wheel

    Safety Analysis:
    The ΔQ/Q ratio (maximum wheel load difference / average wheel load)
    will be calculated and compared against configuration-specific limits:
    - Bogie: ≤ 60% (more flexible articulated design)
    - Truck: ≤ 50% (stricter rigid frame requirements)

    Example:
        >>> input_data = LoadDistributionInput(
        ...     config_type="Bogie",
        ...     total_load=85.5,
        ...     front_percent=55.0,
        ...     q1_percent=52.0,
        ...     q3_percent=48.0
        ... )

    Note:
        Input validation ensures physically meaningful load distribution
        scenarios and prevents calculation errors that could lead to
        unsafe vehicle operation recommendations.
    """

    config_type: Literal["Bogie", "Truck", "Axle"]
    total_load: float
    front_percent: float
    q1_percent: float
    q3_percent: float

    @field_validator('total_load', 'front_percent', 'q1_percent', 'q3_percent')
    @classmethod
    def validate_positive(cls, v):
        """Validate that load and percentage values are positive."""
        if v <= 0:
            raise ValueError('Load and percentage values must be positive')
        return v

    @field_validator('front_percent')
    @classmethod
    def validate_percentage(cls, v):
        """Validate that front axle percentage is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError('Front axle percentage must be between 0 and 100')
        return v

    @field_validator('q1_percent', 'q3_percent')
    @classmethod
    def validate_q_percentage(cls, v):
        """Validate that wheel load percentages are between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError('Wheel load percentages must be between 0 and 100')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "config_type": "Bogie",
                "total_load": 85.5,
                "front_percent": 55.0,
                "q1_percent": 52.0,
                "q3_percent": 48.0
            }
        }
    )