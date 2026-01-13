# =========================================
# Tractive Effort Tool Schemas Module
# =========================================
# Pydantic data models for tractive effort input validation and type safety.
#
# Purpose: Define the structure and validation rules for tractive effort inputs,
# ensuring type safety and proper validation before physics-based calculations.
#
# Engineering Context:
# - Input parameters directly affect train performance and power requirements
# - Validation prevents invalid operating scenarios that could lead to calculation errors
# - Type safety ensures consistent data handling across the traction calculation pipeline
#
# Used by: api.py (request validation), validation.py (input processing)
# Dependencies: pydantic (BaseModel for validation)

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Literal

class TractiveEffortInput(BaseModel):
    """
    Input schema for tractive effort calculations in railway operations.

    This model validates user inputs for calculating the force and power required
    to move trains, including resistance components and electrical power needs
    for different operating conditions and track geometries.

    Attributes:
        load (float): Train load (wagons/cars) in tonnes
                    - Must be non-negative (can be zero for locomotive-only calculations)
                    - Represents the total trailing load behind the locomotive

        loco_weight (float): Locomotive gross weight in tonnes
                    - Must be positive (locomotive mass affects rolling resistance)
                    - Includes locomotive body, fuel, and equipment weight

        gradient (float): Track gradient value
                    - Must be non-negative (downhill gradients reduce resistance)
                    - Units depend on grad_type (degrees or 1 in G ratio)

        curvature (float): Track curvature value
                    - Must be non-negative (straight track = 0)
                    - Units depend on curvature_unit (radius in meters or angle in degrees)

        speed (float): Train speed in km/h
                    - Must be non-negative (stationary = 0)
                    - Affects dynamic resistance calculations

        mode (Literal["Start", "Running"]): Operating mode
                    - "Start": Initial movement from rest (higher resistance)
                    - "Running": Steady-state movement (lower resistance)

        grad_type (Literal["Degree", "1 in G"]): Gradient specification method
                    - "Degree": Angle in degrees from horizontal
                    - "1 in G": Rise over run ratio (e.g., 1 in 100 = 1%)

        curvature_unit (Literal["Radius(m)", "Degree"]): Curvature specification method
                    - "Radius(m)": Curve radius in meters (larger radius = gentler curve)
                    - "Degree": Curve angle in degrees (smaller angle = gentler curve)

    Validation Rules:
    - All numeric values must be non-negative (physical constraints)
    - load can be zero (locomotive-only operation)
    - loco_weight, speed must be positive for meaningful calculations
    - gradient, curvature can be zero (level track, straight alignment)
    - mode must be either "Start" or "Running"
    - grad_type must be "Degree" or "1 in G"
    - curvature_unit must be "Radius(m)" or "Degree"

    Engineering Considerations:
    - Starting mode uses higher rolling resistance coefficients
    - Gradient affects tractive effort requirements significantly
    - Curvature adds additional resistance due to track superelevation and wheel-rail contact
    - Speed influences aerodynamic resistance (though not explicitly modeled here)

    Example:
        >>> input_data = TractiveEffortInput(
        ...     load=1500.0,           # 1500 tonne train load
        ...     loco_weight=120.0,     # 120 tonne locomotive
        ...     gradient=1.0,          # 1 degree gradient
        ...     curvature=300.0,       # 300m curve radius
        ...     speed=60.0,            # 60 km/h speed
        ...     mode="Running",        # Steady-state operation
        ...     grad_type="Degree",    # Gradient in degrees
        ...     curvature_unit="Radius(m)"  # Curvature as radius
        ... )

    Note:
        Input validation ensures physically meaningful traction scenarios
        and prevents calculation errors that could lead to unsafe or
        unrealistic locomotive power recommendations.
    """

    load: float
    loco_weight: float
    gradient: float
    curvature: float
    speed: float
    mode: Literal["Start", "Running"]
    grad_type: Literal["Degree", "1 in G"]
    curvature_unit: Literal["Radius(m)", "Degree"]

    @field_validator('load', 'loco_weight', 'gradient', 'curvature', 'speed')
    @classmethod
    def validate_positive(cls, v):
        """Validate that physical parameters are non-negative."""
        if v < 0:
            raise ValueError('Physical parameters must be non-negative (≥ 0)')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "load": 1500.0,
                "loco_weight": 120.0,
                "gradient": 1.0,
                "curvature": 300.0,
                "speed": 60.0,
                "mode": "Running",
                "grad_type": "Degree",
                "curvature_unit": "Radius(m)"
            }
        }
    )