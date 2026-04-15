"""
Pydantic models for MongoDB collections.
Defines the schema for all database documents.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# Enums
class ApplicationStatus(str, Enum):
    """Application status values."""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    AGENT_1_COMPLETE = "agent_1_complete"
    AGENT_2_COMPLETE = "agent_2_complete"
    AGENT_3_COMPLETE = "agent_3_complete"
    AGENT_4_COMPLETE = "agent_4_complete"
    AGENT_5_COMPLETE = "agent_5_complete"
    AGENT_6_COMPLETE = "agent_6_complete"
    PENDING_ADMIN = "pending_admin"
    MANUAL_REVIEW = "manual_review"  # ← Requires admin intervention
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class DecisionType(str, Enum):
    """Final decision types."""
    APPROVE = "approve"
    REJECT = "reject"
    MANUAL_REVIEW = "manual_review"


# Models
class User(BaseModel):
    """User model for applicants."""
    
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    phone: str
    pan_number: str
    full_name: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('pan_number')
    def validate_pan(cls, v):
        """Validate PAN number format."""
        import re
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pattern, v.upper()):
            raise ValueError('Invalid PAN number format')
        return v.upper()
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number."""
        import re
        pattern = r'^[6-9]\d{9}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid phone number')
        return v


class DocumentInfo(BaseModel):
    """Document information model."""
    
    filename: str
    file_path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    file_type: str
    file_size: int


class Agent1Result(BaseModel):
    """Agent 1 (Intake) result."""
    
    status: str  # "pass" or "fail"
    blacklist_check: bool
    duplicate_check: bool
    validation_errors: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Agent2Result(BaseModel):
    """Agent 2 (Document) result."""
    
    status: str
    pan_extracted: Dict[str, Any] = {}
    salary_extracted: Dict[str, Any] = {}
    cross_validation: Dict[str, bool] = {}
    ocr_confidence: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Agent3Result(BaseModel):
    """Agent 3 (Credit Scoring) result."""
    
    status: str
    credit_score: float
    default_probability: float
    risk_band: str  # "low", "medium", "high"
    shap_values: Dict[str, float] = {}
    top_factors: List[Dict[str, Any]] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Agent4Result(BaseModel):
    """Agent 4 (Rules Engine) result."""
    
    status: str
    rules_passed: List[str] = []
    rules_failed: List[str] = []
    rule_details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Agent5Result(BaseModel):
    """Agent 5 (Policy RAG) result."""
    
    status: str
    relevant_policies: List[Dict[str, Any]] = []
    policy_violations: List[str] = []
    policy_recommendations: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Agent6Result(BaseModel):
    """Agent 6 (LLM Decision) result."""
    
    status: str
    decision: DecisionType
    confidence: float
    reasoning: str
    key_factors: List[str] = []
    recommendations: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Application(BaseModel):
    """Loan application model."""
    
    application_id: str = Field(default_factory=lambda: f"APP{uuid.uuid4().hex[:12].upper()}")
    user_id: str
    
    # Application Data
    full_name: str
    age: int
    pan_number: str
    phone: str
    email: EmailStr
    monthly_income: float
    employment_type: str  # "salaried", "self_employed"
    employer_name: Optional[str] = None
    years_employed: Optional[float] = None
    loan_amount: float
    loan_purpose: str
    existing_loans: int = 0
    existing_emi: float = 0.0
    
    # Documents
    pan_document: Optional[DocumentInfo] = None
    salary_document: Optional[DocumentInfo] = None
    
    # Status
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    
    # Agent Results
    agent1_result: Optional[Agent1Result] = None
    agent2_result: Optional[Agent2Result] = None
    agent3_result: Optional[Agent3Result] = None
    agent4_result: Optional[Agent4Result] = None
    agent5_result: Optional[Agent5Result] = None
    agent6_result: Optional[Agent6Result] = None
    
    # Final Decision
    final_decision: Optional[DecisionType] = None
    admin_decision: Optional[str] = None
    admin_notes: Optional[str] = None
    decided_by: Optional[str] = None  # admin_id
    decided_at: Optional[datetime] = None
    requires_hitl: bool = False  # Human-In-The-Loop: requires admin intervention
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    
    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class Blacklist(BaseModel):
    """Blacklist model."""
    
    blacklist_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pan_number: str
    name: Optional[str] = None
    reason: str
    added_by: str  # admin_id or "system"
    added_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Admin(BaseModel):
    """Admin user model."""
    
    admin_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    hashed_password: str
    role: str = "admin"  # "admin", "super_admin"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class AuditLog(BaseModel):
    """Audit log for admin actions."""
    
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    application_id: str
    action: str  # "approved", "rejected", "reviewed"
    decision: Optional[str] = None
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None