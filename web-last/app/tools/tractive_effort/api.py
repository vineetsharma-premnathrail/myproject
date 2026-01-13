# =========================================
# Tractive Effort Tool API Router Module
# =========================================
# FastAPI router endpoints for tractive effort and power calculations in railway operations.
#
# Purpose: Provide REST API endpoints for calculating train tractive effort requirements,
# electrical power needs, and generating professional engineering reports for railway design.
#
# Engineering Context:
# - Exposes physics-based traction calculations through web API
# - Supports both calculation results and formatted report generation
# - Critical for locomotive procurement, electrification planning, and train performance analysis
#
# API Endpoints:
# - POST /calculate: Perform tractive effort analysis and return results
# - POST /download-report: Generate and download DOCX engineering report
#
# Used by: main FastAPI application (tools/tractive-effort routes)
# Dependencies: schemas.py, validation.py, service.py, reports/pdf_builder.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from .schemas import TractiveEffortInput
from .validation import validate_tractive_effort_inputs
from .service import perform_te_calculation
from .reports.pdf_builder import create_te_docx_report

# Create FastAPI router for tractive effort tool endpoints
router = APIRouter(tags=["tractive-effort"])

@router.post("/calculate")
async def calculate_tractive_effort(raw_input: TractiveEffortInput) -> Dict[str, Any]:
    """
    Calculate tractive effort and electrical power requirements for trains.

    Performs comprehensive engineering analysis of train traction requirements
    including rolling resistance, gradient resistance, curvature resistance,
    and electrical power calculations for overhead electrification systems.

    Engineering Application:
    - Determines locomotive tractive effort capacity requirements
    - Calculates electrical power demand from overhead lines
    - Analyzes resistance components affecting train performance
    - Supports railway electrification and locomotive procurement decisions

    Request Body:
        TractiveEffortInput schema containing:
        - load: Train load (wagons/cars) in tonnes
        - loco_weight: Locomotive gross weight in tonnes
        - gradient: Track gradient (degrees or 1 in G)
        - curvature: Track curvature (radius in meters or degrees)
        - speed: Train speed in km/h
        - mode: Operating mode ("Start" or "Running")
        - grad_type: Gradient specification ("Degree" or "1 in G")
        - curvature_unit: Curvature specification ("Radius(m)" or "Degree")

    Returns:
        dict: Analysis results containing:
            - report: Formatted step-by-step calculation string
            - results: Complete calculation results with all components

    Response Format:
        {
            "report": "# Tractive Effort Calculation Report\\n...",
            "results": {
                "te": 15420.5,           # Total tractive effort in kg
                "power": 245.8,          # Rail horsepower
                "ohe_current": 456.2,    # OHE current in amperes
                "T1": 2025.3,            # Wagon rolling resistance
                "T2": 350.6,             # Loco rolling resistance
                "T3": 1000.0,            # Gradient resistance
                "T4": 45.2               # Curvature resistance
            }
        }

    Resistance Components (T1-T4):
    - T1: Wagon rolling resistance (function of load and mode)
    - T2: Locomotive rolling resistance (function of loco weight and mode)
    - T3: Gradient resistance (function of slope and total weight)
    - T4: Curvature resistance (function of curve radius/angle and speed)

    Power Calculations:
    - Rail Horsepower: Mechanical power at rail head
    - OHE Current: Electrical current required from overhead lines
    - Accounts for system efficiency and power factor

    Raises:
        HTTPException (500): Calculation or validation errors with details
                            - Invalid input parameters
                            - Mathematical errors in traction calculations
                            - Data processing failures

    Example:
        >>> response = await calculate_tractive_effort({
        ...     "load": 1500.0,
        ...     "loco_weight": 120.0,
        ...     "gradient": 1.0,
        ...     "curvature": 300.0,
        ...     "speed": 60.0,
        ...     "mode": "Running",
        ...     "grad_type": "Degree",
        ...     "curvature_unit": "Radius(m)"
        ... })
        >>> print(f"Tractive Effort Required: {response['results']['te']:.0f} kg")
        Tractive Effort Required: 15421 kg
    """
    try:
        # Validate and process input parameters
        inputs, inputs_raw = validate_tractive_effort_inputs(raw_input)

        # Perform comprehensive tractive effort analysis
        results, report = perform_te_calculation(inputs, inputs_raw)

        # Return structured response
        return {"report": report, "results": results}

    except Exception as e:
        # Handle any calculation or validation errors
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download-report")
async def download_tractive_effort_report(raw_input: TractiveEffortInput):
    """
    Generate and download professional tractive effort analysis report as DOCX.

    Creates a formatted Microsoft Word document containing the complete
    engineering analysis report with input parameters, resistance components,
    power calculations, and detailed methodology for railway engineering records.

    Engineering Documentation:
    - Professional report format for railway engineering records
    - Includes all input parameters and calculation steps
    - Suitable for regulatory submissions and design reviews
    - Timestamped for version control and audit trails

    Request Body:
        Same as /calculate endpoint - TractiveEffortInput schema

    Returns:
        StreamingResponse: DOCX file download with proper headers
                          - Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
                          - Content-Disposition: attachment; filename=TE_Report.docx

    File Contents:
        - Report generation timestamp
        - Input parameters section (load, weight, gradient, curvature, speed, mode)
        - Calculation results summary (tractive effort, power, current)
        - Resistance components breakdown (T1-T4 with explanations)
        - Engineering formula references and methodology

    Raises:
        HTTPException (500): Report generation or validation errors
                            - Missing python-docx library
                            - Invalid input parameters
                            - File generation failures

    Example:
        >>> response = await download_tractive_effort_report({
        ...     "load": 1500.0,
        ...     "loco_weight": 120.0,
        ...     "gradient": 1.0,
        ...     "curvature": 300.0,
        ...     "speed": 60.0,
        ...     "mode": "Running",
        ...     "grad_type": "Degree",
        ...     "curvature_unit": "Radius(m)"
        ... })
        >>> # Returns DOCX file download

    Note:
        Requires python-docx library for document generation.
        Falls back to error if library is not installed.
        Report includes detailed resistance component analysis
        for comprehensive engineering evaluation.
    """
    try:
        # Validate and process input parameters
        inputs, inputs_raw = validate_tractive_effort_inputs(raw_input)

        # Perform tractive effort analysis (results needed for report)
        results, _ = perform_te_calculation(inputs, inputs_raw)

        # Generate DOCX report with complete analysis
        stream = create_te_docx_report(inputs, results, inputs_raw)

        # Return file download response
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=TE_Report.docx"}
        )

    except Exception as e:
        # Handle any report generation or validation errors
        raise HTTPException(status_code=500, detail=str(e))