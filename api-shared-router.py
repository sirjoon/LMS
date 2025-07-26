from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import date
import structlog

from database import get_db
from models import LeaveType, CorporateHoliday, User
from utils.auth import get_current_user

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
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


@router.get("/leave-types", response_model=List[LeaveTypeResponse])
async def get_leave_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available leave types"""
    try:
        leave_types = db.query(LeaveType).all()
        
        logger.info("Leave types retrieved", user=current_user.username, count=len(leave_types))
        return [LeaveTypeResponse.from_orm(lt) for lt in leave_types]
        
    except Exception as e:
        logger.error("Failed to get leave types", user=current_user.username, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve leave types"
        )


@router.get("/holidays", response_model=List[HolidayResponse])
async def get_holidays(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all corporate holidays"""
    try:
        holidays = db.query(CorporateHoliday).order_by(CorporateHoliday.date).all()
        
        logger.info("Holidays retrieved", user=current_user.username, count=len(holidays))
        return [HolidayResponse.from_orm(holiday) for holiday in holidays]
        
    except Exception as e:
        logger.error("Failed to get holidays", user=current_user.username, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve holidays"
        )