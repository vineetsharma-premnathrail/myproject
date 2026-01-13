"""
Hydraulic Tool API Router Module
===============================
Purpose:
    FastAPI router for hydraulic motor/pump calculation endpoints.
    Provides REST API access to hydraulic drive system sizing calculations.
Layer:
    Backend / Tools / Hydraulic / API
Endpoints:
    - POST /calculate: Main hydraulic calculation endpoint
    - POST /download_report: Download DOCX report endpoint
Calculation Modes:
    - calc_cc: Calculate motor displacement and pump requirements
    - calc_speed: Calculate achievable speeds for given specifications
Dependencies:
    - schemas.py: Input validation models
    - validation.py: Input processing and validation
    - service.py: Business logic and calculation orchestration
    - reports.pdf_builder.py: DOCX report generation
Security:
    - Requires authenticated user (handled by parent router)
    - Input validation prevents malicious data
    - Error handling prevents information leakage
Output Formats:
    - JSON results for web display
    - DOCX reports for professional documentation
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .schemas import HydraulicInput
from .validation import validate_hydraulic_inputs
from .service import perform_hydraulic_calculation
from .reports.pdf_builder import create_hydraulic_docx_report

router = APIRouter()

@router.post("/calculate")
async def calculate_hydraulic(raw: HydraulicInput):
    """
    Calculate hydraulic motor/pump parameters for rail vehicle drive systems.

    Main endpoint for hydraulic calculations. Processes vehicle and system parameters
    to determine required motor displacement, pump specifications, or achievable speeds.
    Supports both sizing calculations and performance analysis.

    Args:
        raw (HydraulicInput): Validated input data including:
            - Vehicle parameters (weight, axles, wheel diameter)
            - Target speed or motor/pump specifications
            - System configuration (gear ratios, efficiencies)
            - Operating conditions (slope, curve resistance)
            - Calculation mode (calc_cc or calc_speed)

    Returns:
        dict: Calculation results with structure:
            {
                "report": "formatted_text_report",
                "results": {
                    "detailed_calculations": {...},
                    "motor_specs": {...},
                    "pump_specs": {...},
                    "performance_data": {...}
                }
            }

    Raises:
        HTTPException: For validation errors or calculation failures
            - 400: Invalid input data
            - 500: Internal calculation error

    Calculation Modes:
        - calc_cc: Determines motor displacement and pump requirements for target speed
        - calc_speed: Calculates achievable speeds for given motor/pump specs

    Example:
        POST /calculate
        {
            "calc_mode": "calc_cc",
            "weight": "100",
            "axles": "4",
            "speed": "30",
            "pressure": "200",
            "num_motors": "4",
            ...
        }
    """
    try:
        # Validate and process input data
        inputs, inputs_raw = validate_hydraulic_inputs(raw)

        # Perform hydraulic calculations
        results, report = perform_hydraulic_calculation(inputs, inputs_raw)

        # Return results in expected format
        return {"report": report, "results": results}

    except ValueError as e:
        # Input validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected calculation errors
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@router.post("/download_report")
async def download_hydraulic_report(raw: HydraulicInput):
    """
    Generate and download hydraulic calculation report as DOCX document.

    Creates a professional engineering report in Microsoft Word format
    containing all input parameters, calculations, and results. The report
    includes formatted tables, step-by-step calculations, and professional
    documentation suitable for engineering records.

    Args:
        raw (HydraulicInput): Same input parameters as calculate endpoint

    Returns:
        StreamingResponse: DOCX file download with headers:
            - Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
            - Content-Disposition: attachment; filename=Hydraulic_Report.docx

    Raises:
        HTTPException: For validation errors or report generation failures
            - 400: Invalid input data
            - 500: Report generation error

    Dependencies:
        - python-docx library for DOCX generation
        - Valid input data (same validation as calculate endpoint)

    Report Contents:
        - Input parameters summary
        - Step-by-step calculations
        - Motor and pump specifications
        - Performance analysis
        - Professional formatting and tables
    """
    try:
        # Validate input data (reuse same validation as calculate endpoint)
        inputs, inputs_raw = validate_hydraulic_inputs(raw)

        # Perform calculations to get results
        results, _ = perform_hydraulic_calculation(inputs, inputs_raw)

        # Generate DOCX report
        stream = create_hydraulic_docx_report(inputs, results, inputs_raw)

        # Return as downloadable file
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=Hydraulic_Report.docx"}
        )

    except ValueError as e:
        # Input validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Report generation errors
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")