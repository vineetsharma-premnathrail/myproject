# =========================================
# Vehicle Performance Tool Schemas Module
# =========================================
# Pydantic data models for vehicle performance input validation and type safety.
#
# Purpose: Define the structure and validation rules for locomotive performance inputs,
# ensuring type safety and proper validation before physics-based performance calculations.
#
# Engineering Context:
# - Input parameters directly affect locomotive performance predictions
# - Validation prevents invalid operating scenarios that could lead to unrealistic results
# - Type safety ensures consistent data handling across the performance analysis pipeline
#
# Used by: api.py (request validation), validation.py (input processing)
# Dependencies: pydantic (BaseModel for validation)

from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Dict, Optional

class VehiclePerformanceInput(BaseModel):
    """
    Input schema for locomotive performance analysis in railway operations.

    This model validates user inputs for comprehensive locomotive performance
    evaluation including tractive effort, speed capabilities, gear optimization,
    and performance characteristics across different operating conditions.

    Attributes:
        max_curve (float): Maximum curve radius/angle the locomotive can negotiate
                          - Affects curve resistance calculations
                          - Units depend on curve_unit (degrees or meters)

        max_slope (float): Maximum gradient the locomotive can operate on
                          - Critical for uphill performance analysis
                          - Units depend on slope_unit (percentage or degrees)

        loco_gvw (float): Locomotive gross vehicle weight in kg
                          - Total weight including fuel, equipment, and structure
                          - Must be positive (affects all resistance calculations)

        max_speed (float): Maximum design speed of the locomotive in km/h
                          - Design limit for performance calculations
                          - Must be positive

        num_axles (int): Number of powered axles on the locomotive
                        - Affects total tractive effort capacity
                        - Must be positive integer

        rear_axle_ratio (float): Final drive ratio of the rear axle
                                - Affects torque multiplication and speed reduction
                                - Must be positive

        gear_ratios (List[float]): Transmission gear ratios (highest to lowest)
                                  - Determines speed-torque characteristics
                                  - At least one ratio required, all must be positive

        shunting_load (float): Maximum load for shunting operations in tonnes
                              - Affects low-speed performance calculations
                              - Can be zero for locomotive-only analysis

        peak_power (float): Maximum engine power output in kW
                           - Peak mechanical power available
                           - Must be positive

        friction_mu (float): Coefficient of friction between wheel and rail (0-1)
                            - Affects maximum tractive effort (adhesion limit)
                            - Typically 0.2-0.4 for dry rail conditions

        wheel_dia (float): Drive wheel diameter in meters
                          - Affects torque-to-force conversion
                          - Must be positive

        min_rpm (int): Minimum engine speed in RPM
                      - Idle speed for continuous operation
                      - Must be positive

        max_rpm (int): Maximum engine speed in RPM (default: 2500)
                      - Peak engine speed limit
                      - Must be positive

        torque_curve (Optional[Dict[int, float]]): Engine torque curve (RPM -> Nm)
                                                   - Defines engine characteristics
                                                   - RPM keys, torque values in Nm

        curve_unit (str): Units for curve specification (default: "degree")
                         - "degree": Curve angle in degrees
                         - "radius": Curve radius in meters

        slope_unit (str): Units for slope specification (default: "%")
                         - "%": Slope as percentage (rise/run × 100)
                         - "degree": Slope angle in degrees

    Validation Rules:
    - Physical parameters (weights, speeds, power) must be positive
    - Integer parameters (axles, RPM) must be positive
    - Friction coefficient must be between 0 and 1
    - At least one gear ratio required, all ratios must be positive
    - Curve and slope units must be valid options

    Engineering Considerations:
    - Gear ratios should be ordered from highest to lowest numerically
    - Torque curve should cover the full RPM range for accurate interpolation
    - Friction coefficient varies with rail conditions (wet/dry, clean/dirty)
    - Maximum curve/slope define the locomotive's operational envelope

    Example:
        >>> input_data = VehiclePerformanceInput(
        ...     max_curve=6.0,           # 6 degree maximum curve
        ...     max_slope=2.0,           # 2% maximum gradient
        ...     loco_gvw=120000,         # 120 tonne locomotive
        ...     max_speed=100,           # 100 km/h max speed
        ...     num_axles=4,             # 4 powered axles
        ...     rear_axle_ratio=3.5,     # 3.5:1 axle ratio
        ...     gear_ratios=[8.5, 6.2, 4.5, 3.2, 2.1],  # 5-speed transmission
        ...     shunting_load=2000,      # 2000 tonne shunting capacity
        ...     peak_power=2000,         # 2000 kW peak power
        ...     friction_mu=0.35,        # 0.35 friction coefficient
        ...     wheel_dia=1.25,          # 1.25m wheel diameter
        ...     min_rpm=400,             # 400 RPM idle
        ...     max_rpm=2100,            # 2100 RPM max
        ...     curve_unit="degree",
        ...     slope_unit="%"
        ... )

    Note:
        Input validation ensures physically meaningful locomotive specifications
        and prevents calculation errors that could lead to unsafe or unrealistic
        performance predictions. All parameters should be verified against
        manufacturer specifications for accurate analysis.
    """

    max_curve: float
    max_slope: float
    loco_gvw: float
    max_speed: float
    num_axles: int
    rear_axle_ratio: float
    gear_ratios: List[float]
    shunting_load: float
    peak_power: float
    friction_mu: float
    wheel_dia: float
    min_rpm: int
    max_rpm: int = 2500
    torque_curve: Optional[Dict[int, float]] = None
    curve_unit: str = "degree"
    slope_unit: str = "%"

    @field_validator('loco_gvw', 'max_speed', 'peak_power', 'wheel_dia')
    @classmethod
    def validate_positive(cls, v):
        """Validate that physical parameters are positive."""
        if v <= 0:
            raise ValueError('Physical parameters (weight, speed, power, wheel diameter) must be positive')
        return v

    @field_validator('num_axles', 'min_rpm', 'max_rpm')
    @classmethod
    def validate_positive_int(cls, v):
        """Validate that integer parameters are positive."""
        if v <= 0:
            raise ValueError('Integer parameters (axles, RPM values) must be positive')
        return v

    @field_validator('friction_mu')
    @classmethod
    def validate_friction(cls, v):
        """Validate that friction coefficient is within physical bounds."""
        if not 0 < v <= 1:
            raise ValueError('Friction coefficient must be between 0 and 1 (exclusive of 0)')
        return v

    @field_validator('gear_ratios')
    @classmethod
    def validate_gear_ratios(cls, v):
        """Validate that gear ratios are provided and all positive."""
        if not v:
            raise ValueError('At least one gear ratio is required for transmission analysis')
        for ratio in v:
            if ratio <= 0:
                raise ValueError('All gear ratios must be positive values')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "max_curve": 6.0,
                "max_slope": 2.0,
                "loco_gvw": 120000,
                "max_speed": 100,
                "num_axles": 4,
                "rear_axle_ratio": 3.5,
                "gear_ratios": [8.5, 6.2, 4.5, 3.2, 2.1],
                "shunting_load": 2000,
                "peak_power": 2000,
                "friction_mu": 0.35,
                "wheel_dia": 1.25,
                "min_rpm": 400,
                "max_rpm": 2100,
                "curve_unit": "degree",
                "slope_unit": "%"
            }
        }
    )