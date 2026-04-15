"""User-facing loan application routes."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel
import logging

from backend.auth.dependencies import get_current_user
from backend.db.repositories.application_repo import ApplicationRepository
from backend.db.models import ApplicationStatus
from backend.utils.file_handler import FileHandler
from backend.utils.response import APIResponse
from backend.utils.validators import InputValidator
from backend.graph.executor import GraphExecutor

router = APIRouter(prefix="/api/user", tags=["user"])
logger = logging.getLogger(__name__)


@router.post("/apply")
async def submit_application(
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    age: int = Form(...),
    pan_number: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    monthly_income: float = Form(...),
    employment_type: str = Form(...),
    employer_name: Optional[str] = Form(None),
    years_employed: Optional[float] = Form(None),
    loan_amount: float = Form(...),
    loan_purpose: str = Form(...),
    existing_loans: int = Form(0),
    existing_emi: float = Form(0.0),
    pan_document: UploadFile = File(...),
    salary_document: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Submit a new loan application with documents."""

    # Validate inputs
    pan_valid, pan_error = InputValidator.validate_pan(pan_number)
    if not pan_valid:
        raise HTTPException(status_code=400, detail=pan_error)

    phone_valid, phone_error = InputValidator.validate_phone(phone)
    if not phone_valid:
        raise HTTPException(status_code=400, detail=phone_error)

    age_valid, age_error = InputValidator.validate_age(age)
    if not age_valid:
        raise HTTPException(status_code=400, detail=age_error)

    income_valid, income_error = InputValidator.validate_income(monthly_income)
    if not income_valid:
        raise HTTPException(status_code=400, detail=income_error)

    # Save uploaded documents
    pan_filename, pan_path, pan_size = await FileHandler.save_upload(
        pan_document, subfolder="pan_cards", user_id=current_user["user_id"]
    )
    salary_filename, salary_path, salary_size = await FileHandler.save_upload(
        salary_document, subfolder="salary_slips", user_id=current_user["user_id"]
    )

    # Create application record
    app_data = {
        "user_id": current_user["user_id"],
        "full_name": full_name,
        "age": age,
        "pan_number": pan_number.upper(),
        "phone": phone,
        "email": email,
        "monthly_income": monthly_income,
        "employment_type": employment_type,
        "employer_name": employer_name,
        "years_employed": years_employed,
        "loan_amount": loan_amount,
        "loan_purpose": loan_purpose,
        "existing_loans": existing_loans,
        "existing_emi": existing_emi,
        "pan_document": {
            "filename": pan_filename,
            "file_path": pan_path,
            "file_type": pan_document.content_type,
            "file_size": pan_size,
        },
        "salary_document": {
            "filename": salary_filename,
            "file_path": salary_path,
            "file_type": salary_document.content_type,
            "file_size": salary_size,
        },
    }

    application = await ApplicationRepository.create_application(app_data)

    # Start processing in background
    background_tasks.add_task(
        GraphExecutor.run_workflow,
        application.application_id,
        app_data
    )

    return APIResponse.success(
        data={
            "application_id": application.application_id,
            "status": application.status,
            "message": "Application submitted. Processing started.",
        },
        message="Application submitted successfully"
    )


@router.get("/status/{application_id}")
async def get_application_status(
    application_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get real-time status of a loan application."""
    app = await ApplicationRepository.get_application_by_id(application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return APIResponse.success(data={
        "application_id": app["application_id"],
        "status": app["status"],
        "final_decision": app.get("final_decision"),
        "created_at": str(app["created_at"]),
        "updated_at": str(app["updated_at"]),
        "agent_progress": {
            "agent1": app.get("agent1_result") is not None,
            "agent2": app.get("agent2_result") is not None,
            "agent3": app.get("agent3_result") is not None,
            "agent4": app.get("agent4_result") is not None,
            "agent5": app.get("agent5_result") is not None,
            "agent6": app.get("agent6_result") is not None,
        }
    })


@router.get("/applications")
async def get_my_applications(
    current_user: dict = Depends(get_current_user),
):
    """Get all applications for the logged-in user."""
    try:
        apps = await ApplicationRepository.get_applications_by_user(current_user["user_id"])
        return APIResponse.success(data=apps, message=f"Found {len(apps)} applications")
    except Exception as e:
        logger.error(f"Error retrieving applications for user {current_user['user_id']}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving applications: {str(e)}")