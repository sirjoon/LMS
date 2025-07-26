from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import date, datetime
import structlog

from database import get_db
from models import User, LeaveRequest, LeaveBalance, CorporateHoliday, RequestStatus, UserRole
from utils.auth import get_employee_user

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
class LeaveRequestCreate(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    notes: str | None = None


class LeaveBalanceResponse(BaseModel):
    leave_type_id: int
    leave_type_name: str
    remaining_days: int
    
    class Config:
        from_attributes = True


class LeaveRequestResponse(BaseModel):
    id: int
    leave_type_name: str
    start_date: date
    end_date: date
    days_requested: int
    status: str
    notes: str | None
    requested_at: datetime
    decided_at: datetime | None = None
    manager_name: str
    
    class Config:
        from_attributes = True


class CreateRequestResponse(BaseModel):
    message: str
    request_id: int
    manager_notified: str


@router.get("/balance", response_model=List[LeaveBalanceResponse])
async def get_leave_balance(
    db: Session = Depends(get_db),
    employee_user: User = Depends(get_employee_user)
):
    """Get employee's remaining leave balance for all leave types"""
    try:
        balances = db.query(LeaveBalance).filter(
            LeaveBalance.user_id == employee_user.id
        ).all()
        
        response_list = []
        for balance in balances:
            response_list.append(LeaveBalanceResponse(
                leave_type_id=balance.leave_type_id,
                leave_type_name=balance.leave_type.name,
                remaining_days=balance.remaining_days
            ))
        
        logger.info("Leave balance retrieved", employee=employee_user.username, balances_count=len(response_list))
        return response_list
        
    except Exception as e:
        logger.error("Failed to get leave balance", employee=employee_user.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leave balance"
        )


@router.post("/requests", response_model=CreateRequestResponse)
async def create_leave_request(
    request_data: LeaveRequestCreate,
    db: Session = Depends(get_db),
    employee_user: User = Depends(get_employee_user)
):
    """Create a new leave request"""
    try:
        # Validate employee has a manager
        if not employee_user.manager_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee does not have an assigned manager"
            )
        
        # Validate dates
        if request_data.start_date > request_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before or equal to end date"
            )
        
        if request_data.start_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot request leave for past dates"
            )
        
        # Calculate business days requested
        days_requested = _calculate_business_days(request_data.start_date, request_data.end_date)
        
        if days_requested <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No business days in the requested date range"
            )
        
        # Check if dates overlap with corporate holidays
        overlapping_holidays = db.query(CorporateHoliday).filter(
            CorporateHoliday.date >= request_data.start_date,
            CorporateHoliday.date <= request_data.end_date
        ).all()
        
        if overlapping_holidays:
            holiday_dates = [h.date.strftime("%Y-%m-%d") for h in overlapping_holidays]
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Leave request overlaps with corporate holidays: {', '.join(holiday_dates)}"
            )
        
        # Check employee's leave balance
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.user_id == employee_user.id,
            LeaveBalance.leave_type_id == request_data.leave_type_id
        ).first()
        
        if not balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave balance not found for this leave type"
            )
        
        if balance.remaining_days < days_requested:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient leave balance. Available: {balance.remaining_days} days, Requested: {days_requested} days"
            )
        
        # Create leave request
        leave_request = LeaveRequest(
            employee_id=employee_user.id,
            manager_id=employee_user.manager_id,
            leave_type_id=request_data.leave_type_id,
            start_date=request_data.start_date,
            end_date=request_data.end_date,
            status=RequestStatus.PENDING,
            notes=request_data.notes
        )
        
        db.add(leave_request)
        db.commit()
        db.refresh(leave_request)
        
        # Mock email notification to manager
        manager = db.query(User).filter(User.id == employee_user.manager_id).first()
        mock_email_message = f"EMAIL: New leave request from {employee_user.username} ({request_data.start_date} to {request_data.end_date}) - {days_requested} days"
        print(mock_email_message)
        
        logger.info(
            "Leave request created",
            request_id=leave_request.id,
            employee=employee_user.username,
            manager=manager.username if manager else "Unknown",
            days_requested=days_requested,
            leave_type_id=request_data.leave_type_id
        )
        
        return CreateRequestResponse(
            message="Leave request submitted successfully",
            request_id=leave_request.id,
            manager_notified=manager.username if manager else "Unknown"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create leave request", employee=employee_user.username, error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create leave request"
        )


@router.get("/requests", response_model=List[LeaveRequestResponse])
async def get_leave_requests_history(
    db: Session = Depends(get_db),
    employee_user: User = Depends(get_employee_user)
):
    """Get employee's leave request history"""
    try:
        requests = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == employee_user.id
        ).order_by(LeaveRequest.requested_at.desc()).all()
        
        response_list = []
        for req in requests:
            days_requested = _calculate_business_days(req.start_date, req.end_date)
            
            response_list.append(LeaveRequestResponse(
                id=req.id,
                leave_type_name=req.leave_type.name,
                start_date=req.start_date,
                end_date=req.end_date,
                days_requested=days_requested,
                status=req.status.value,
                notes=req.notes,
                requested_at=req.requested_at,
                decided_at=req.decided_at,
                manager_name=req.manager.username if req.manager else "No Manager"
            ))
        
        logger.info("Leave request history retrieved", employee=employee_user.username, requests_count=len(response_list))
        return response_list
        
    except Exception as e:
        logger.error("Failed to get leave request history", employee=employee_user.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leave request history"
        )


def _calculate_business_days(start_date: date, end_date: date) -> int:
    """Calculate business days between two dates (excluding weekends)"""
    days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Monday = 0, Sunday = 6, so weekdays are 0-4
        if current_date.weekday() < 5:
            days += 1
        current_date = date.fromordinal(current_date.toordinal() + 1)
    
    return days