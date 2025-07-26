from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, date
import structlog

from database import get_db
from models import User, LeaveRequest, LeaveBalance, RequestStatus
from utils.auth import get_manager_user

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
class LeaveRequestResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    employee_email: str
    leave_type_name: str
    start_date: date
    end_date: date
    days_requested: int
    status: str
    notes: str | None
    requested_at: datetime
    decided_at: datetime | None = None
    
    class Config:
        from_attributes = True


class DecisionResponse(BaseModel):
    message: str
    request_id: int
    new_status: str


@router.get("/requests/pending", response_model=List[LeaveRequestResponse])
async def get_pending_requests(
    db: Session = Depends(get_db),
    manager_user: User = Depends(get_manager_user)
):
    """Get all pending leave requests for this manager"""
    try:
        requests = db.query(LeaveRequest).filter(
            LeaveRequest.manager_id == manager_user.id,
            LeaveRequest.status == RequestStatus.PENDING
        ).all()
        
        response_list = []
        for req in requests:
            # Calculate days requested (business days only, excluding weekends)
            days_requested = _calculate_business_days(req.start_date, req.end_date)
            
            response_list.append(LeaveRequestResponse(
                id=req.id,
                employee_id=req.employee_id,
                employee_name=req.employee.username,
                employee_email=req.employee.email,
                leave_type_name=req.leave_type.name,
                start_date=req.start_date,
                end_date=req.end_date,
                days_requested=days_requested,
                status=req.status.value,
                notes=req.notes,
                requested_at=req.requested_at,
                decided_at=req.decided_at
            ))
        
        logger.info("Pending requests retrieved", manager=manager_user.username, count=len(response_list))
        return response_list
        
    except Exception as e:
        logger.error("Failed to get pending requests", manager=manager_user.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending requests"
        )


@router.post("/requests/{request_id}/approve", response_model=DecisionResponse)
async def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    manager_user: User = Depends(get_manager_user)
):
    """Approve a leave request and update employee balance"""
    try:
        # Get the request
        request = db.query(LeaveRequest).filter(
            LeaveRequest.id == request_id,
            LeaveRequest.manager_id == manager_user.id,
            LeaveRequest.status == RequestStatus.PENDING
        ).first()
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found or not pending"
            )
        
        # Calculate days to deduct
        days_requested = _calculate_business_days(request.start_date, request.end_date)
        
        # Get employee's leave balance
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.user_id == request.employee_id,
            LeaveBalance.leave_type_id == request.leave_type_id
        ).first()
        
        if not balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee leave balance not found"
            )
        
        # Check if employee has enough balance
        if balance.remaining_days < days_requested:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient leave balance"
            )
        
        # Update request status and balance atomically
        request.status = RequestStatus.APPROVED
        request.decided_at = datetime.utcnow()
        balance.remaining_days -= days_requested
        
        db.commit()
        
        # Mock email notification
        print(f"EMAIL: Leave request approved for {request.employee.username} ({request.start_date} to {request.end_date})")
        
        logger.info(
            "Leave request approved",
            request_id=request_id,
            employee=request.employee.username,
            manager=manager_user.username,
            days_deducted=days_requested
        )
        
        return DecisionResponse(
            message="Leave request approved successfully",
            request_id=request_id,
            new_status=RequestStatus.APPROVED.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to approve request", request_id=request_id, manager=manager_user.username, error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve leave request"
        )


@router.post("/requests/{request_id}/reject", response_model=DecisionResponse)
async def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    manager_user: User = Depends(get_manager_user)
):
    """Reject a leave request"""
    try:
        # Get the request
        request = db.query(LeaveRequest).filter(
            LeaveRequest.id == request_id,
            LeaveRequest.manager_id == manager_user.id,
            LeaveRequest.status == RequestStatus.PENDING
        ).first()
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave request not found or not pending"
            )
        
        # Update request status
        request.status = RequestStatus.REJECTED
        request.decided_at = datetime.utcnow()
        
        db.commit()
        
        # Mock email notification
        print(f"EMAIL: Leave request rejected for {request.employee.username} ({request.start_date} to {request.end_date})")
        
        logger.info(
            "Leave request rejected",
            request_id=request_id,
            employee=request.employee.username,
            manager=manager_user.username
        )
        
        return DecisionResponse(
            message="Leave request rejected",
            request_id=request_id,
            new_status=RequestStatus.REJECTED.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to reject request", request_id=request_id, manager=manager_user.username, error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject leave request"
        )


@router.get("/requests/history", response_model=List[LeaveRequestResponse])
async def get_request_history(
    db: Session = Depends(get_db),
    manager_user: User = Depends(get_manager_user)
):
    """Get all leave requests (history) for this manager"""
    try:
        requests = db.query(LeaveRequest).filter(
            LeaveRequest.manager_id == manager_user.id
        ).order_by(LeaveRequest.requested_at.desc()).all()
        
        response_list = []
        for req in requests:
            days_requested = _calculate_business_days(req.start_date, req.end_date)
            
            response_list.append(LeaveRequestResponse(
                id=req.id,
                employee_id=req.employee_id,
                employee_name=req.employee.username,
                employee_email=req.employee.email,
                leave_type_name=req.leave_type.name,
                start_date=req.start_date,
                end_date=req.end_date,
                days_requested=days_requested,
                status=req.status.value,
                notes=req.notes,
                requested_at=req.requested_at,
                decided_at=req.decided_at
            ))
        
        logger.info("Request history retrieved", manager=manager_user.username, count=len(response_list))
        return response_list
        
    except Exception as e:
        logger.error("Failed to get request history", manager=manager_user.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve request history"
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