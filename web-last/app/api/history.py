"""
Calculation History API Module
-----------------------------
Purpose:
    Provides REST API endpoints for managing user calculation history.
    Allows saving, retrieving, renaming, and deleting calculation records.
    Supports filtering by tool type and user-specific history management.
Layer:
    Backend / API / Calculation History
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import json

from app.db.session import get_db
import app.db.models as models

router = APIRouter(prefix="/history", tags=["calculation-history"])


class CalculationSaveRequest(BaseModel):
    """
    Request model for saving a calculation to history.

    Attributes:
        user_id: ID of the user who performed the calculation
        tool_name: Name of the tool used (e.g., "braking", "hydraulic")
        calculation_name: Optional custom name for the calculation
        inputs: Dictionary of input parameters used in the calculation
        results: Dictionary of calculation results and outputs
    """
    user_id: int
    tool_name: str
    calculation_name: Optional[str] = None
    inputs: dict
    results: dict


class CalculationHistoryResponse(BaseModel):
    """
    Response model for calculation history summary.

    Attributes:
        id: Unique calculation history identifier
        tool_name: Name of the tool used
        calculation_name: Display name of the calculation
        created_at: ISO timestamp of when calculation was saved
    """
    id: int
    tool_name: str
    calculation_name: Optional[str]
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


class CalculationDetailResponse(BaseModel):
    """
    Response model for detailed calculation information.

    Attributes:
        id: Unique calculation history identifier
        tool_name: Name of the tool used
        calculation_name: Display name of the calculation
        inputs: Full input parameters as dictionary
        results: Full calculation results as dictionary
        created_at: ISO timestamp of when calculation was saved
    """
    id: int
    tool_name: str
    calculation_name: Optional[str]
    inputs: dict
    results: dict
    created_at: str


class RenameCalculationRequest(BaseModel):
    """
    Request model for renaming a calculation.

    Attributes:
        calculation_name: New name for the calculation
    """
    calculation_name: str


@router.post("/save")
def save_calculation(request: CalculationSaveRequest, db: Session = Depends(get_db)):
    """
    Save a completed calculation to the user's history.

    Parameters:
        request: CalculationSaveRequest containing calculation details
        db: Database session dependency

    Returns:
        dict: Success confirmation with calculation ID and name

    Raises:
        HTTPException: If user not found (404)

    Features:
        - Auto-generates calculation names if not provided
        - Stores inputs and results as JSON for flexible data types
        - Maintains chronological order for each tool type
    """
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate calculation name if not provided
    calc_name = request.calculation_name
    if not calc_name:
        # Count existing calculations for this tool
        count = db.query(models.CalculationHistory).filter(
            models.CalculationHistory.user_id == request.user_id,
            models.CalculationHistory.tool_name == request.tool_name
        ).count()
        calc_name = f"{request.tool_name.replace('_', ' ').title()} #{count + 1}"
    
    # Create history record
    history = models.CalculationHistory(
        user_id=request.user_id,
        tool_name=request.tool_name,
        calculation_name=calc_name,
        inputs_json=json.dumps(request.inputs),
        results_json=json.dumps(request.results)
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return {
        "message": "Calculation saved successfully",
        "id": history.id,
        "calculation_name": history.calculation_name
    }


@router.get("/list")
def get_calculation_history(
    user_id: int,
    tool_name: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Retrieve calculation history for a specific user.

    Parameters:
        user_id: ID of the user whose history to retrieve
        tool_name: Optional filter by specific tool name
        db: Database session dependency

    Returns:
        list: Array of calculation history summaries

    Features:
        - Optional filtering by tool type
        - Ordered by most recent first
        - Includes parsed input data for quick preview
    """
    query = db.query(models.CalculationHistory).filter(
        models.CalculationHistory.user_id == user_id
    )
    
    if tool_name:
        query = query.filter(models.CalculationHistory.tool_name == tool_name)
    
    # Order by most recent first
    history = query.order_by(models.CalculationHistory.created_at.desc()).all()
    
    return [
        {
            "id": h.id,
            "tool_name": h.tool_name,
            "calculation_name": h.calculation_name,
            "inputs": json.loads(h.inputs_json) if h.inputs_json else {},
            "created_at": h.created_at.strftime("%Y-%m-%d %H:%M") if h.created_at else ""
        }
        for h in history
    ]


@router.get("/detail/{calculation_id}")
def get_calculation_detail(calculation_id: int, db: Session = Depends(get_db)):
    """
    Get complete details of a specific calculation including full inputs and results.

    Parameters:
        calculation_id: ID of the calculation to retrieve
        db: Database session dependency

    Returns:
        dict: Complete calculation details with parsed JSON data

    Raises:
        HTTPException: If calculation not found (404)

    Note:
        Returns full input parameters and results for detailed analysis
    """
    history = db.query(models.CalculationHistory).filter(
        models.CalculationHistory.id == calculation_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    return {
        "id": history.id,
        "tool_name": history.tool_name,
        "calculation_name": history.calculation_name,
        "inputs": json.loads(history.inputs_json),
        "results": json.loads(history.results_json),
        "created_at": history.created_at.strftime("%Y-%m-%d %H:%M") if history.created_at else ""
    }


@router.put("/rename/{calculation_id}")
def rename_calculation(
    calculation_id: int,
    request: RenameCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Rename an existing calculation in the history.

    Parameters:
        calculation_id: ID of the calculation to rename
        request: RenameCalculationRequest with new name
        db: Database session dependency

    Returns:
        dict: Success confirmation with updated calculation info

    Raises:
        HTTPException: If calculation not found (404)

    Note:
        Trims whitespace from the new name
    """
    history = db.query(models.CalculationHistory).filter(
        models.CalculationHistory.id == calculation_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    history.calculation_name = request.calculation_name.strip()
    db.commit()
    db.refresh(history)
    
    return {
        "message": "Calculation renamed successfully",
        "id": history.id,
        "calculation_name": history.calculation_name
    }


@router.delete("/delete/{calculation_id}")
def delete_calculation(calculation_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Delete a calculation from the user's history.

    Parameters:
        calculation_id: ID of the calculation to delete
        user_id: ID of the user who owns the calculation (for security)
        db: Database session dependency

    Returns:
        dict: Success confirmation

    Raises:
        HTTPException: If calculation not found or doesn't belong to user (404)

    Security:
        Requires user_id parameter to ensure users can only delete their own calculations
    """
    history = db.query(models.CalculationHistory).filter(
        models.CalculationHistory.id == calculation_id,
        models.CalculationHistory.user_id == user_id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    db.delete(history)
    db.commit()
    
    return {"message": "Calculation deleted successfully"}
