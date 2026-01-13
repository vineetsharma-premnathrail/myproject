"""
Braking Tool Schemas Module
==========================
Purpose:
    Pydantic models for input validation and data structure definition.
    Defines the expected format for braking calculation inputs from the frontend.
Layer:
    Backend / Tools / Braking / Schemas
Validation:
    - Automatic type conversion and validation
    - Required vs optional field handling
    - Default values for optional parameters
    - Input sanitization and bounds checking
Fields:
    Vehicle Parameters:
        - mass_kg: Vehicle total mass in kilograms
        - reaction_time: Driver reaction time in seconds
        - num_wheels: Number of wheels for force distribution
    Calculation Mode:
        - calc_mode: "Rail" or "Rail+Road" calculation type
    Rail Parameters:
        - rail_speed_input: Comma-separated speeds (km/h)
        - rail_gradient_input: Comma-separated gradients
        - rail_gradient_type: Unit type for gradients
    Road Parameters (Optional):
        - road_speed_input: Comma-separated road speeds
        - road_gradient_input: Comma-separated road gradients
        - road_gradient_type: Unit type for road gradients
        - mu: Friction coefficient for road calculations
    Documentation:
        - doc_no: Document number for reports
        - made_by, checked_by, approved_by: Quality assurance fields
        - wheel_dia: Wheel diameter for advanced calculations
"""

from pydantic import BaseModel, Field
from typing import Optional

class BrakingInput(BaseModel):
    """
    Input validation model for braking calculations.

    Defines all possible input parameters for rail and road braking calculations.
    Automatically validates data types, required fields, and provides defaults
    for optional parameters.

    Required Fields:
        - mass_kg: Vehicle mass (must be > 0)
        - reaction_time: Driver reaction time (must be >= 0)
        - num_wheels: Number of wheels (must be > 0)
        - calc_mode: Calculation mode ("Rail" or "Rail+Road")
        - rail_speed_input: Comma-separated rail speeds
        - rail_gradient_input: Comma-separated rail gradients
        - rail_gradient_type: Gradient unit type

    Optional Fields:
        - road_speed_input: Road speeds (empty string if not used)
        - road_gradient_input: Road gradients (empty string if not used)
        - road_gradient_type: Road gradient units (default: "Percentage (%)")
        - mu: Friction coefficient (default: 0.7)
        - doc_no: Document number (default: empty)
        - made_by: Author name (default: empty)
        - checked_by: Checker name (default: empty)
        - approved_by: Approver name (default: empty)
        - wheel_dia: Wheel diameter in mm (default: 0)
    """

    # Required vehicle parameters
    mass_kg: float = Field(..., gt=0, description="Vehicle total mass in kilograms")
    reaction_time: float = Field(..., ge=0, description="Driver reaction time in seconds")
    num_wheels: int = Field(..., gt=0, description="Number of wheels for force distribution")

    # Calculation mode selection
    calc_mode: str = Field(..., description="Calculation mode: 'Rail' or 'Rail+Road'")

    # Rail-specific parameters (always required)
    rail_speed_input: str = Field(..., description="Comma-separated rail speeds in km/h (e.g., '30,40,50')")
    rail_gradient_input: str = Field(..., description="Comma-separated rail gradients")
    rail_gradient_type: str = Field(..., description="Rail gradient unit type: 'Degree (°)', '1 in G', or 'Percentage (%)'")

    # Road-specific parameters (optional, used in Rail+Road mode)
    road_speed_input: Optional[str] = Field("", description="Comma-separated road speeds in km/h")
    road_gradient_input: Optional[str] = Field("", description="Comma-separated road gradients")
    road_gradient_type: Optional[str] = Field("Percentage (%)", description="Road gradient unit type")
    mu: Optional[float] = Field(0.7, gt=0, le=1, description="Friction coefficient for road calculations")

    # Documentation and quality assurance fields
    doc_no: Optional[str] = Field("", description="Document number for report generation")
    made_by: Optional[str] = Field("", description="Name of person who created the calculation")
    checked_by: Optional[str] = Field("", description="Name of person who checked the calculation")
    approved_by: Optional[str] = Field("", description="Name of person who approved the calculation")
    wheel_dia: Optional[float] = Field(0, ge=0, description="Wheel diameter in mm (for advanced calculations)")