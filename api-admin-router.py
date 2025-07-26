from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import structlog

from database import get_db
from models import User, LeaveType, LeaveBalance, CorporateHoliday, UserRole
from utils.auth import get_admin_user

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
class CreateUserRequest(BaseModel):
    username: str
    email: str
    role: UserRole
    manager_username: Optional[str] = None
    initial_quotas: Optional[dict[int, int]] = None  # leave_type_id -> days


class UpdateBalanceRequest(BaseModel):
    leave_type_id: int
    remaining_days: int


class CreateLeaveTypeRequest(BaseModel):
    name: str
    default_quota: int


class CreateHolidayRequest(BaseModel):
    date: date
    description: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    manager_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class LeaveTypeResponse(BaseModel):
    id: int
    name: str
    default_quota: int
    
    class Config:
        from_attributes = True


class HolidayResponse(BaseModel):
    id: int
    date: date
    description: str
    
    class Config:
        from_attributes = True


@router.post("/users", response_model=UserResponse)
async def create_or_update_user(
    user_request: CreateUserRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Create or update a user"""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.username == user_request.username).first()
        
        if existing_user:
            # Update existing user
            existing_user.email = user_request.email
            existing_user.role = user_request.role
            
            # Set manager if provided
            if user_request.manager_username:
                manager = db.query(User).filter(User.username == user_request.manager_username).first()
                if not manager:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Manager not found"
                    )
                existing_user.manager_id = manager.id
            else:
                existing_user.manager_id = None
            
            user = existing_user
            logger.info("User updated", username=user.username, admin=admin_user.username)
        else:
            # Create new user
            user_data = {
                "username": user_request.username,
                "email": user_request.email,
                "role": user_request.role
            }
            
            # Set manager if provided
            if user_request.manager_username:
                manager = db.query(User).filter(User.username == user_request.manager_username).first()
                if not manager:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Manager not found"
                    )
                user_data["manager_id"] = manager.id
            
            user = User(**user_data)
            db.add(user)
            db.flush()  # Get the ID
            
            # Create initial leave balances for employees
            if user.role == UserRole.EMPLOYEE:
                leave_types = db.query(LeaveType).all()
                for leave_type in leave_types:
                    # Use custom quota if provided, otherwise use default
                    quota = user_request.initial_quotas.get(leave_type.id, leave_type.default_quota) if user_request.initial_quotas else leave_type.default_quota
                    
                    balance = LeaveBalance(
                        user_id=user.id,
                        leave_type_id=leave_type.id,
                        remaining_days=quota
                    )
                    db.add(balance)
            
            logger.info("User created", username=user.username, admin=admin_user.username)
        
        db.commit()
        db.refresh(user)
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create/update user", error=str(e), admin=admin_user.username)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create/update user"
        )


@router.patch("/leave-balances/{user_id}")
async def update_leave_balance(
    user_id: int,
    balance_request: UpdateBalanceRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update a user's leave balance for a specific leave type"""
    try:
        # Find the leave balance
        balance = db.query(LeaveBalance).filter(
            LeaveBalance.user_id == user_id,
            LeaveBalance.leave_type_id == balance_request.leave_type_id
        ).first()
        
        if not balance:
            # Create new balance if it doesn't exist
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            leave_type = db.query(LeaveType).filter(LeaveType.id == balance_request.leave_type_id).first()
            if not leave_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Leave type not found"
                )
            
            balance = LeaveBalance(
                user_id=user_id,
                leave_type_id=balance_request.leave_type_id,
                remaining_days=balance_request.remaining_days
            )
            db.add(balance)
            logger.info("Leave balance created", user_id=user_id, leave_type_id=balance_request.leave_type_id, admin=admin_user.username)
        else:
            # Update existing balance
            balance.remaining_days = balance_request.remaining_days
            logger.info("Leave balance updated", user_id=user_id, leave_type_id=balance_request.leave_type_id, admin=admin_user.username)
        
        db.commit()
        
        return {"message": "Leave balance updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update leave balance", error=str(e), admin=admin_user.username)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update leave balance"
        )


@router.post("/leave-types", response_model=LeaveTypeResponse)
async def create_leave_type(
    leave_type_request: CreateLeaveTypeRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Create a new leave type"""
    try:
        # Check if leave type already exists
        existing = db.query(LeaveType).filter(LeaveType.name == leave_type_request.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave type already exists"
            )
        
        leave_type = LeaveType(
            name=leave_type_request.name,
            default_quota=leave_type_request.default_quota
        )
        db.add(leave_type)
        db.commit()
        db.refresh(leave_type)
        
        logger.info("Leave type created", name=leave_type.name, admin=admin_user.username)
        return LeaveTypeResponse.from_orm(leave_type)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create leave type", error=str(e), admin=admin_user.username)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create leave type"
        )


@router.post("/holidays", response_model=HolidayResponse)
async def create_holiday(
    holiday_request: CreateHolidayRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Create a new corporate holiday"""
    try:
        # Check if holiday already exists for this date
        existing = db.query(CorporateHoliday).filter(CorporateHoliday.date == holiday_request.date).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Holiday already exists for this date"
            )
        
        holiday = CorporateHoliday(
            date=holiday_request.date,
            description=holiday_request.description
        )
        db.add(holiday)
        db.commit()
        db.refresh(holiday)
        
        logger.info("Holiday created", date=holiday.date, description=holiday.description, admin=admin_user.username)
        return HolidayResponse.from_orm(holiday)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create holiday", error=str(e), admin=admin_user.username)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create holiday"
        )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """List all users"""
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]