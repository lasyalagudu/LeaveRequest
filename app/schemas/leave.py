# app/schemas/leave.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional
from enum import Enum
import re

# ============================================
# ENUMS FOR BETTER TYPE SAFETY
# ============================================

class LeaveActionType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"

class LeaveStatusType(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED" 
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

# ============================================
# ENHANCED LEAVE APPLICATION SCHEMA
# ============================================

class LeaveApply(BaseModel):
    """Leave application with comprehensive validation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Auto-strip whitespace
        validate_assignment=True,   # Validate on assignment
        extra='forbid'              # Don't allow extra fields
    )
    
    # Employee ID with constraints
    employee_id: int = Field(
        gt=0, 
        description="Must be a positive integer",
        example=123
    )
    
    # Date fields with basic constraints
    start_date: date = Field(
        description="Leave start date",
        example="2024-12-01"
    )
    
    end_date: date = Field(
        description="Leave end date", 
        example="2024-12-05"
    )
    
    # Reason with comprehensive constraints
    reason: Optional[str] = Field(
        None,
        min_length=3,
        max_length=500,
        description="Reason for leave (optional but recommended)",
        example="Family vacation"
    )
    
    # ============================================
    # FIELD VALIDATORS
    # ============================================
    
    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v):
        """Validate start date constraints"""
        today = date.today()
        
        # Allow same day application (remove if not needed)
        if v < today:
            raise ValueError("Start date cannot be in the past")
        
        # Don't allow too far in future (1 year limit)
        max_future_date = date(today.year + 1, today.month, today.day)
        if v > max_future_date:
            raise ValueError("Start date cannot be more than 1 year in advance")
        
        return v
    
    @field_validator('end_date')
    @classmethod  
    def validate_end_date(cls, v, info):
        """Validate end date against start date and other constraints"""
        start_date = info.data.get('start_date')
        today = date.today()
        
        # Basic past date check
        if v < today:
            raise ValueError("End date cannot be in the past")
        
        # Cross-field validation with start_date
        if start_date:
            if v < start_date:
                raise ValueError("End date cannot be before start date")
            
            # Maximum leave duration (e.g., 30 days)
            duration = (v - start_date).days + 1
            if duration > 30:
                raise ValueError("Leave duration cannot exceed 30 days")
            
            # Minimum duration (prevent same-day leaves if needed)
            # Uncomment if you want minimum duration
            # if duration < 1:
            #     raise ValueError("Leave must be at least 1 day")
        
        return v
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        """Validate reason content"""
        if v is None:
            return v
        
        # Check for meaningful content (not just whitespace/special chars)
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError("Reason must contain meaningful text")
        
        # Prevent common spam patterns
        spam_patterns = [
            r'^(.)\1{10,}',  # Repeated characters (aaaaaaaaaa)
            r'^[^a-zA-Z]*$', # Only special characters/numbers
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, v):
                raise ValueError("Please provide a meaningful reason")
        
        return v.strip()

# ============================================
# ENHANCED LEAVE ACTION SCHEMA
# ============================================

class LeaveAction(BaseModel):
    """Leave approval/rejection with validation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )
    
    # Use enum for type safety
    action: LeaveActionType = Field(
        description="Action to take on leave request",
        example="APPROVE"
    )
    
    # Approver note with constraints
    approver_note: Optional[str] = Field(
        None,
        min_length=3,
        max_length=1000,
        description="Optional note from approver",
        example="Approved for team coverage"
    )
    
    @field_validator('approver_note')
    @classmethod
    def validate_approver_note(cls, v, info):
        """Validate approver note requirements"""
        if v is None:
            return v
        
        action = info.data.get('action')
        
        # Require note for rejections
        if action == LeaveActionType.REJECT and not v.strip():
            raise ValueError("Approver note is required when rejecting leave")
        
        # Validate meaningful content
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError("Approver note must contain meaningful text")
        
        return v.strip()

# ============================================
# ENHANCED LEAVE OUTPUT SCHEMA  
# ============================================

class LeaveOut(BaseModel):
    """Leave request output with validation"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(gt=0, description="Leave request ID")
    employee_id: int = Field(gt=0, description="Employee ID")
    start_date: date = Field(description="Leave start date")
    end_date: date = Field(description="Leave end date") 
    days: int = Field(ge=1, description="Number of leave days")
    status: LeaveStatusType = Field(description="Current leave status")
    reason: Optional[str] = Field(None, description="Leave reason")
    
    # Additional fields you might want to add
    created_at: Optional[datetime] = Field(None, description="When request was created")
    approved_at: Optional[datetime] = Field(None, description="When request was approved")
    approver_note: Optional[str] = Field(None, description="Note from approver")
    
    @field_validator('days')
    @classmethod
    def validate_days(cls, v, info):
        """Validate calculated days match date range"""
        start_date = info.data.get('start_date')
        end_date = info.data.get('end_date')
        
        if start_date and end_date:
            calculated_days = (end_date - start_date).days + 1
            if v != calculated_days:
                raise ValueError("Days field doesn't match date range")
        
        return v

# ============================================
# ENHANCED LEAVE BALANCE SCHEMA
# ============================================

class LeaveBalanceOut(BaseModel):
    """Leave balance output with validation"""
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid'
    )
    
    employee_id: int = Field(gt=0, description="Employee ID")
    allocation: int = Field(ge=0, description="Total annual leave allocation")
    used: int = Field(ge=0, description="Leave days used")
    remaining: int = Field(ge=0, description="Remaining leave days")
    
    # Additional useful fields
    pending: Optional[int] = Field(None, ge=0, description="Leave days pending approval")
    carry_forward: Optional[int] = Field(None, ge=0, description="Days carried forward from previous year")
    
    @field_validator('remaining')
    @classmethod
    def validate_balance_consistency(cls, v, info):
        """Ensure balance calculations are consistent"""
        allocation = info.data.get('allocation', 0)
        used = info.data.get('used', 0)
        
        expected_remaining = allocation - used
        if v != expected_remaining:
            raise ValueError(f"Balance inconsistency: remaining should be {expected_remaining}")
        
        return v
    
    @field_validator('used')  
    @classmethod
    def validate_used_not_exceed_allocation(cls, v, info):
        """Ensure used days don't exceed allocation"""
        allocation = info.data.get('allocation', 0)
        if v > allocation:
            raise ValueError("Used leave cannot exceed allocation")
        return v

# ============================================
# ADDITIONAL UTILITY SCHEMAS
# ============================================

class LeaveDateRange(BaseModel):
    """Utility schema for date range queries"""
    start_date: date = Field(description="Start date for query")
    end_date: date = Field(description="End date for query")
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        start_date = info.data.get('start_date')
        if start_date and v < start_date:
            raise ValueError("End date must be after start date")
        
        # Limit query range to prevent performance issues
        if start_date:
            days_diff = (v - start_date).days
            if days_diff > 365:
                raise ValueError("Date range cannot exceed 365 days")
        
        return v

class LeaveSearchFilters(BaseModel):
    """Schema for leave search/filter parameters"""
    model_config = ConfigDict(extra='forbid')
    
    employee_id: Optional[int] = Field(None, gt=0)
    status: Optional[LeaveStatusType] = None
    date_range: Optional[LeaveDateRange] = None
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Items per page")

# ============================================
# BULK OPERATIONS SCHEMAS
# ============================================

class BulkLeaveAction(BaseModel):
    """Schema for bulk leave actions"""
    leave_ids: list[int] = Field(min_length=1, max_length=50)
    action: LeaveActionType
    approver_note: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('leave_ids')
    @classmethod
    def validate_leave_ids(cls, v):
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate leave IDs not allowed")
        
        # Validate all IDs are positive
        if any(id <= 0 for id in v):
            raise ValueError("All leave IDs must be positive")
        
        return v