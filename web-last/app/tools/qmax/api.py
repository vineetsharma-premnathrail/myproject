# =========================================
# Qmax Tool API Router Module
# =========================================
# FastAPI router endpoints for Qmax (Maximum Axle Load) calculations.
#
# Purpose: Provide REST API endpoints for calculating maximum axle loads
# and generating professional engineering reports for rail vehicle design.
#
# Engineering Context:
# - Exposes railway engineering calculations through web API
# - Supports both calculation results and formatted report generation
# - Critical for rail vehicle design, safety compliance, and optimization
#
# API Endpoints:
# - POST /calculate_qmax: Perform Qmax calculation and return results
# - POST /download_qmax_report: Generate and download DOCX engineering report
#
# Used by: main FastAPI application (tools/qmax routes)
# Dependencies: schemas.py, validation.py, service.py, reports/pdf_builder.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .schemas import QmaxInput
from .validation import validate_qmax_inputs
from .service import perform_qmax_calculation
from .reports.pdf_builder import create_qmax_docx_report

# Create FastAPI router for Qmax tool endpoints
router = APIRouter()

@router.post("/calculate_qmax")
async def calculate_qmax(raw: QmaxInput):
    """
    Calculate maximum axle load (Qmax) for rail vehicles.

    Performs engineering calculation of maximum permissible axle loads based on
    wheel diameter, rail bending stress limits, and safety factors. Returns
    both calculation results and detailed step-by-step report.

    Engineering Application:
    - Determines safe axle load limits for rail vehicle design
    - Prevents rail damage from excessive bending stress
    - Supports railway engineering compliance and optimization

    Request Body:
        QmaxInput schema containing:
        - d: Wheel diameter limit (mm)
        - sigma_b_selection: Rail material strength option
        - sigma_b_custom: Custom strength value (if applicable)
        - v_head: Safety factor for dynamic loading

    Returns:
        dict: Calculation results containing:
            - report: Formatted step-by-step calculation string
            - results: Numeric calculation results with units

    Response Format:
        {
            "report": "# Qmax Calculation Report\\n...",
            "results": {
                "d": 750.0,
                "sigma_b": 880.0,
                "v_head": 1.2,
                "qmax_kn": 123.45,
                "qmax_tonnes": 12.58
            }
        }

    Raises:
        HTTPException (500): Calculation or validation errors with details
                            - Invalid input parameters
                            - Mathematical errors in calculation
                            - Data processing failures

    Example:
        >>> response = await calculate_qmax({
        ...     "d": "750",
        ...     "sigma_b_selection": "880 N/mm²",
        ...     "sigma_b_custom": "",
        ...     "v_head": "1.2"
        ... })
        >>> print(response["results"]["qmax_kn"])
        123.45
    """
    try:
        # Validate and process input parameters
        inputs, inputs_raw = validate_qmax_inputs(raw)

        # Perform calculation and generate report
        results, report = perform_qmax_calculation(inputs, inputs_raw)

        # Return structured response
        return {"report": report, "results": results}

    except Exception as e:
        # Handle any calculation or validation errors
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download_qmax_report")
async def download_qmax_report(raw: QmaxInput):
    """
    Generate and download professional Qmax calculation report as DOCX.

    Creates a formatted Microsoft Word document containing the complete
    engineering calculation report with input parameters, step-by-step
    calculations, and final results for documentation and compliance purposes.

    Engineering Documentation:
    - Professional report format for railway engineering records
    - Includes all input parameters and calculation steps
    - Suitable for regulatory submissions and design reviews
    - Timestamped for version control and audit trails

    Request Body:
        Same as /calculate_qmax endpoint - QmaxInput schema

    Returns:
        StreamingResponse: DOCX file download with proper headers
                          - Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
                          - Content-Disposition: attachment; filename=Qmax_Report.docx

    File Contents:
        - Report generation timestamp
        - Input parameters section
        - Step-by-step calculation methodology
        - Final Qmax results in kN and tonnes
        - Engineering formula references

    Raises:
        HTTPException (500): Report generation or validation errors
                            - Missing python-docx library
                            - Invalid input parameters
                            - File generation failures

    Example:
        >>> response = await download_qmax_report({
        ...     "d": "750",
        ...     "sigma_b_selection": "880 N/mm²",
        ...     "sigma_b_custom": "",
        ...     "v_head": "1.2"
        ... })
        >>> # Returns DOCX file download

    Note:
        Requires python-docx library for document generation.
        Falls back to error if library is not installed.
    """
    try:
        # Validate and process input parameters
        inputs, inputs_raw = validate_qmax_inputs(raw)

        # Perform calculation (results needed for report)
        results, _ = perform_qmax_calculation(inputs, inputs_raw)

        # Generate DOCX report
        stream = create_qmax_docx_report(results, inputs_raw)

        # Return file download response
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=Qmax_Report.docx"}
        )

    except Exception as e:
        # Handle any report generation or validation errors
        raise HTTPException(status_code=500, detail=str(e))