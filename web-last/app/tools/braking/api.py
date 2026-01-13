"""
Braking Tool API Router Module
=============================
Purpose:
    FastAPI router for braking force calculation endpoints.
    Provides REST API access to braking calculations for rail and road vehicles.
Layer:
    Backend / Tools / Braking / API
Endpoints:
    - POST /braking_calculate: Main braking calculation endpoint
Dependencies:
    - schemas.py: Input validation models
    - validation.py: Input processing and validation
    - service.py: Business logic and calculation orchestration
Security:
    - Requires authenticated user (handled by parent router)
    - Input validation prevents malicious data
    - Error handling prevents information leakage
"""

from fastapi import APIRouter, HTTPException
from .schemas import BrakingInput
from .validation import validate_braking_inputs
from .service import perform_braking_calculation

router = APIRouter()

@router.post("/braking_calculate")
async def calculate_braking(raw: BrakingInput):
    """
    Calculate braking performance for rail and road vehicles.

    Main endpoint for braking force calculations. Processes user inputs,
    validates data, performs engineering calculations, and returns results
    formatted for both UI display and PDF report generation.

    Args:
        raw (BrakingInput): Validated input data including:
            - Vehicle mass, reaction time, number of wheels
            - Rail speeds and gradients (comma-separated)
            - Road speeds and gradients (for Rail+Road mode)
            - Friction coefficient and other parameters
            - Document metadata (doc_no, made_by, etc.)

    Returns:
        dict: Calculation results with structure:
            {
                "rows": [
                    {
                        "scenario": str,
                        "speed": float,
                        "gradient": float,
                        "force": float,
                        "compliance": str,
                        ...
                    }
                ]
            }

    Raises:
        HTTPException: For validation errors or calculation failures
            - 400: Invalid input data
            - 500: Internal calculation error

    Example:
        POST /braking_calculate
        {
            "mass_kg": 50000,
            "reaction_time": 1.0,
            "num_wheels": 4,
            "calc_mode": "Rail",
            "rail_speed_input": "30,40,50",
            "rail_gradient_input": "0,2,5",
            "rail_gradient_type": "Percentage (%)",
            ...
        }
    """
    try:
        # Validate and process input data
        inputs, inputs_raw = validate_braking_inputs(raw)

        # Perform braking calculations
        results, context = perform_braking_calculation(inputs)

        # Return results in expected format
        return {"rows": results}

    except ValueError as e:
        # Input validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected calculation errors
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")