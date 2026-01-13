# =========================================
# Load Distribution Tool API Router Module
# =========================================
# FastAPI router endpoints for load distribution analysis in rail vehicles.
#
# Purpose: Provide REST API endpoints for analyzing load distribution across
# axles and wheels in rail vehicles and generating professional engineering reports.
#
# Engineering Context:
# - Exposes railway engineering calculations through web API
# - Supports both calculation results and formatted report generation
# - Critical for rail vehicle design, safety compliance, and optimization
#
# API Endpoints:
# - POST /calculate: Perform load distribution analysis and return results
# - POST /download-report: Generate and download DOCX engineering report
#
# Used by: main FastAPI application (tools/load-distribution routes)
# Dependencies: schemas.py, validation.py, service.py, reports/pdf_builder.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from .schemas import LoadDistributionInput
from .validation import validate_load_distribution_inputs
from .service import perform_load_distro_calc, format_load_distro_steps
from .reports.pdf_builder import create_load_distro_docx

# Create FastAPI router for load distribution tool endpoints
router = APIRouter(tags=["load-distribution"])

@router.post("/calculate")
async def calculate_load_distribution(raw_input: LoadDistributionInput) -> Dict[str, Any]:
    """
    Calculate load distribution across axles and wheels in rail vehicles.

    Performs engineering analysis of load distribution to ensure vehicle stability
    and safety compliance. Calculates individual wheel loads and validates against
    configuration-specific safety limits for balanced load distribution.

    Engineering Application:
    - Analyzes axle load distribution (front/rear balance)
    - Calculates individual wheel loads (Q1, Q2, Q3, Q4)
    - Validates ΔQ/Q ratio against safety limits
    - Supports railway vehicle design and safety certification

    Request Body:
        LoadDistributionInput schema containing:
        - config_type: Vehicle configuration ("Bogie", "Truck", or "Axle")
        - total_load: Total vehicle load in tonnes
        - front_percent: Percentage of load on front axle (0-100%)
        - q1_percent: Percentage of front axle load on Q1 wheel (0-100%)
        - q3_percent: Percentage of rear axle load on Q3 wheel (0-100%)

    Returns:
        dict: Analysis results containing:
            - report: Formatted step-by-step calculation string
            - results: Complete analysis results with wheel loads and safety status

    Response Format:
        {
            "report": "# Load Distribution Analysis Report\\n...",
            "results": {
                "config_type": "Bogie",
                "total_load": 85.5,
                "front_load": 46.525,
                "rear_load": 38.975,
                "q_values": {"Q1": 24.194, "Q2": 22.331, "Q3": 18.734, "Q4": 20.241},
                "delta_q_by_q": 0.128,
                "limit": 0.6,
                "status": "SAFE"
            }
        }

    Wheel Load Convention:
    - Q1: Front axle, left wheel (when facing direction of travel)
    - Q2: Front axle, right wheel
    - Q3: Rear axle, left wheel
    - Q4: Rear axle, right wheel

    Safety Analysis:
    - ΔQ/Q ratio: (max wheel load - min wheel load) / average wheel load
    - Compared against configuration limits (Bogie: ≤60%, Truck: ≤50%)
    - Status: "SAFE" if within limits, "UNSAFE" if exceeded

    Raises:
        HTTPException (500): Calculation or validation errors with details
                            - Invalid input parameters
                            - Mathematical errors in load distribution
                            - Data processing failures

    Example:
        >>> response = await calculate_load_distribution({
        ...     "config_type": "Bogie",
        ...     "total_load": 85.5,
        ...     "front_percent": 55.0,
        ...     "q1_percent": 52.0,
        ...     "q3_percent": 48.0
        ... })
        >>> print(response["results"]["status"])
        SAFE
    """
    try:
        # Validate and process input parameters
        inputs, inputs_raw = validate_load_distribution_inputs(raw_input)

        # Perform load distribution analysis
        results = perform_load_distro_calc(
            inputs['config_type'],
            inputs['total_load'],
            inputs['front_percent'],
            inputs['q1_percent'],
            inputs['q3_percent']
        )

        # Generate detailed engineering report
        report = format_load_distro_steps(inputs, results)

        # Return structured response
        return {"report": report, "results": results}

    except Exception as e:
        # Handle any calculation or validation errors
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download-report")
async def download_load_distribution_report(raw_input: LoadDistributionInput):
    """
    Generate and download professional load distribution analysis report as DOCX.

    Creates a formatted Microsoft Word document containing the complete
    engineering analysis report with input parameters, calculation methodology,
    wheel load results, and safety compliance assessment.

    Engineering Documentation:
    - Professional report format for railway engineering records
    - Includes all input parameters and analysis steps
    - Suitable for regulatory submissions and design reviews
    - Timestamped for version control and audit trails

    Request Body:
        Same as /calculate endpoint - LoadDistributionInput schema

    Returns:
        StreamingResponse: DOCX file download with proper headers
                          - Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
                          - Content-Disposition: attachment; filename=Load_Report.docx

    File Contents:
        - Report generation timestamp
        - Input parameters section with engineering context
        - Calculation results summary with safety status
        - Individual wheel loads (Q1-Q4) with units
        - ΔQ/Q ratio analysis and compliance assessment
        - Optional diagram image if available

    Raises:
        HTTPException (500): Report generation or validation errors
                            - Missing python-docx library
                            - Invalid input parameters
                            - File generation failures

    Example:
        >>> response = await download_load_distribution_report({
        ...     "config_type": "Bogie",
        ...     "total_load": 85.5,
        ...     "front_percent": 55.0,
        ...     "q1_percent": 52.0,
        ...     "q3_percent": 48.0
        ... })
        >>> # Returns DOCX file download

    Note:
        Requires python-docx library for document generation.
        Falls back to error if library is not installed.
        Includes diagram image if Diagram.png exists in project root.
    """
    try:
        # Validate and process input parameters
        inputs, inputs_raw = validate_load_distribution_inputs(raw_input)

        # Perform load distribution analysis (results needed for report)
        results = perform_load_distro_calc(
            inputs['config_type'],
            inputs['total_load'],
            inputs['front_percent'],
            inputs['q1_percent'],
            inputs['q3_percent']
        )

        # Generate DOCX report with analysis results
        stream = create_load_distro_docx(inputs, results)

        # Return file download response
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=Load_Report.docx"}
        )

    except Exception as e:
        # Handle any report generation or validation errors
        raise HTTPException(status_code=500, detail=str(e))

def format_load_distro_steps(inputs: Dict[str, Any], results: Dict[str, Any]) -> str:
    """
    Format load distribution calculation steps (compatibility function).

    This function provides backward compatibility by importing and calling
    the format_load_distro_steps function from the service module. It ensures
    consistent report formatting across different API entry points.

    Args:
        inputs (Dict[str, Any]): Validated input parameters
        results (Dict[str, Any]): Calculation results from analysis

    Returns:
        str: Formatted calculation report string

    Note:
        This is a compatibility wrapper - the actual formatting logic
        is implemented in the service module for better separation of concerns.
    """
    from .service import format_load_distro_steps as service_format
    return service_format(inputs, results)