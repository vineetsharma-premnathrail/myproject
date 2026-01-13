# =========================================
# Vehicle Performance Tool API Router Module
# =========================================
# FastAPI router endpoints for comprehensive locomotive performance analysis.
#
# Purpose: Provide REST API endpoints for locomotive performance evaluation
# including tractive effort analysis, speed calculations, gear optimization,
# and generation of detailed engineering reports for railway vehicle design.
#
# Engineering Context:
# - Exposes physics-based locomotive performance calculations through web API
# - Supports both calculation results and formatted report generation
# - Critical for locomotive procurement, transmission design, and performance optimization
#
# API Endpoints:
# - POST /calculate: Perform comprehensive performance analysis and return results
# - POST /download-report: Generate and download DOCX engineering report
#
# Used by: main FastAPI application (tools/vehicle-performance routes)
# Dependencies: schemas.py, validation.py, service.py, reports/pdf_builder.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from .schemas import VehiclePerformanceInput
from .validation import validate_vehicle_performance_inputs
from .service import VehiclePerformanceCalculator
from .reports.pdf_builder import create_vehicle_performance_docx_report

# Create FastAPI router for vehicle performance tool endpoints
router = APIRouter(tags=["vehicle-performance"])

@router.post("/calculate")
async def calculate_vehicle_performance(raw_input: VehiclePerformanceInput) -> Dict[str, Any]:
    """
    Calculate comprehensive locomotive performance characteristics.

    Performs detailed engineering analysis of locomotive performance including
    tractive effort curves, speed capabilities across different gears, shunting
    capacity analysis, and performance optimization across various operating conditions.

    Engineering Application:
    - Analyzes tractive effort vs speed characteristics for each gear
    - Calculates maximum speeds on level track, gradients, and curves
    - Evaluates shunting capacity and low-speed performance
    - Supports locomotive procurement and transmission optimization

    Request Body:
        VehiclePerformanceInput schema containing:
        - loco_gvw: Locomotive gross weight (kg)
        - peak_power: Maximum engine power (kW)
        - wheel_dia: Drive wheel diameter (m)
        - num_axles: Number of powered axles
        - rear_axle_ratio: Final drive ratio
        - gear_ratios: Transmission gear ratios (list)
        - friction_mu: Wheel-rail friction coefficient
        - max_speed: Maximum design speed (km/h)
        - max_slope: Maximum operating gradient (%)
        - max_curve: Maximum curve radius/angle
        - shunting_load: Maximum shunting load (tonnes)
        - min_rpm, max_rpm: Engine speed range (RPM)
        - torque_curve: Optional engine torque characteristics

    Returns:
        dict: Comprehensive performance analysis results containing:
            - traction_snapshot: Performance summary by gear (max speeds, tractive effort)
            - tractive_effort_graph: Data for tractive effort vs speed curves
            - shunting_capability_graph: Data for shunting performance analysis
            - speed_vs_slope_table: Speed capabilities vs gradient analysis

    Response Format:
        {
            "traction_snapshot": {
                "gear_1": {"max_speed_level": 45.2, "max_speed_slope": 38.1, ...},
                "gear_2": {"max_speed_level": 62.8, "max_speed_slope": 52.9, ...},
                ...
            },
            "tractive_effort_graph": {
                "speed_points": [0, 10, 20, ...],
                "tractive_effort_gear1": [45000, 42000, 38000, ...],
                "tractive_effort_gear2": [32000, 31000, 29000, ...],
                ...
            },
            "shunting_capability_graph": {...},
            "speed_vs_slope_table": [...]
        }

    Analysis Components:

    Traction Snapshot:
    - Maximum speeds for each gear on level track, design slope, and design curve
    - Tractive effort at maximum power for each gear
    - Performance limits based on adhesion, power, and design constraints

    Tractive Effort Graph:
    - Speed vs tractive effort curves for each gear ratio
    - Shows available tractive force across the speed range
    - Critical for train performance simulation

    Shunting Capability Graph:
    - Low-speed performance analysis for yard operations
    - Tractive effort available for shunting different load weights
    - Important for locomotive utilization planning

    Speed vs Slope Table:
    - Maximum speeds achievable at different gradients
    - Supports route performance analysis and timetable planning

    Raises:
        HTTPException (500): Calculation or validation errors with details
                            - Invalid input parameters
                            - Mathematical errors in performance calculations
                            - Missing dependencies (numpy, etc.)
                            - Data processing failures

    Example:
        >>> response = await calculate_vehicle_performance({
        ...     "loco_gvw": 120000,
        ...     "peak_power": 2000,
        ...     "wheel_dia": 1.25,
        ...     "num_axles": 4,
        ...     "rear_axle_ratio": 3.5,
        ...     "gear_ratios": [8.5, 6.2, 4.5, 3.2, 2.1],
        ...     "friction_mu": 0.35,
        ...     "max_speed": 100,
        ...     "max_slope": 2.0,
        ...     "max_curve": 6.0,
        ...     "shunting_load": 2000,
        ...     "min_rpm": 400,
        ...     "max_rpm": 2100
        ... })
        >>> print(f"Gear 1 max speed: {response['traction_snapshot']['gear_1']['max_speed_level']:.1f} km/h")
        Gear 1 max speed: 45.2 km/h
    """
    try:
        # Validate and process input parameters
        inputs, inputs_raw = validate_vehicle_performance_inputs(raw_input)

        # Initialize performance calculator with validated inputs
        calculator = VehiclePerformanceCalculator(inputs)

        # Perform comprehensive performance analysis
        results = {
            'traction_snapshot': calculator.run_tractive_calculation(),
            'tractive_effort_graph': calculator.calculate_plot_data()['tractive_effort_plot'],
            'shunting_capability_graph': calculator.calculate_plot_data()['shunting_capability_plot'],
            'speed_vs_slope_table': calculator.calculate_speed_for_shunting_load()
        }

        # Return structured performance analysis results
        return results

    except Exception as e:
        # Enhanced error reporting for debugging performance calculation issues
        import traceback
        print(f"Vehicle Performance Calculation Error: {str(e)}")
        print(f"Input data: {raw_input.dict()}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download-report")
async def download_vehicle_performance_report(raw_input: VehiclePerformanceInput):
    """
    Generate and download comprehensive locomotive performance analysis report as DOCX.

    Creates a formatted Microsoft Word document containing the complete
    engineering performance analysis with traction characteristics, speed curves,
    performance tables, and detailed methodology for railway engineering records.

    Engineering Documentation:
    - Professional report format for locomotive performance evaluation
    - Includes all input specifications and analysis results
    - Suitable for procurement decisions and design reviews
    - Timestamped for version control and audit trails

    Request Body:
        Same as /calculate endpoint - VehiclePerformanceInput schema

    Returns:
        StreamingResponse: DOCX file download with proper headers
                          - Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
                          - Content-Disposition: attachment; filename=Performance_Report.docx

    File Contents:
        - Report generation timestamp
        - Complete locomotive specifications
        - Traction performance snapshot (by gear)
        - Performance curves and analysis tables
        - Engineering calculation methodology
        - Speed vs slope performance data

    Report Sections:
        - Input Parameters: Complete locomotive and transmission specifications
        - Traction Performance Snapshot: Speed and tractive effort by gear
        - Performance Analysis: Detailed curves and capability analysis
        - Speed vs Slope Tables: Gradient performance characteristics

    Raises:
        HTTPException (500): Report generation or validation errors
                            - Missing python-docx library
                            - Invalid input parameters
                            - Calculation failures
                            - File generation errors

    Example:
        >>> response = await download_vehicle_performance_report({
        ...     "loco_gvw": 120000,
        ...     "peak_power": 2000,
        ...     "wheel_dia": 1.25,
        ...     "num_axles": 4,
        ...     "rear_axle_ratio": 3.5,
        ...     "gear_ratios": [8.5, 6.2, 4.5, 3.2, 2.1],
        ...     "friction_mu": 0.35,
        ...     "max_speed": 100,
        ...     "max_slope": 2.0,
        ...     "max_curve": 6.0,
        ...     "shunting_load": 2000,
        ...     "min_rpm": 400,
        ...     "max_rpm": 2100
        ... })
        >>> # Returns DOCX file download

    Note:
        Requires python-docx library for document generation.
        Falls back to error if library is not installed.
        Report includes comprehensive performance analysis
        for locomotive specification and procurement evaluation.
    """
    try:
        # Validate and process input parameters
        inputs, inputs_raw = validate_vehicle_performance_inputs(raw_input)

        # Initialize performance calculator
        calculator = VehiclePerformanceCalculator(inputs)

        # Gather all analysis results for comprehensive report
        results = {
            'traction_snapshot': calculator.run_tractive_calculation(),
            'plot_data': calculator.calculate_plot_data(),
            'speed_slope_table': calculator.calculate_speed_for_shunting_load()
        }

        # Generate comprehensive DOCX performance report
        stream = create_vehicle_performance_docx_report(inputs, results)

        # Return file download response
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=Performance_Report.docx"}
        )

    except Exception as e:
        # Handle any report generation or validation errors
        raise HTTPException(status_code=500, detail=str(e))