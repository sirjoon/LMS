from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    manager = relationship("User", remote_side=[id], back_populates="employees")
    employees = relationship("User", back_populates="manager")
    
    # Leave-related relationships
    leave_balances = relationship("LeaveBalance", back_populates="user", cascade="all, delete-orphan")
    leave_requests_as_employee = relationship(
        "LeaveRequest", 
        back_populates="employee", 
        foreign_keys="LeaveRequest.employee_id",
        cascade="all, delete-orphan"
    )
    leave_requests_as_manager = relationship(
        "LeaveRequest", 
        back_populates="manager", 
        foreign_keys="LeaveRequest.manager_id"
    )
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class LeaveType(Base):
    __tablename__ = "leave_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False, unique=True)
    default_quota = Column(Integer, nullable=False)
    
    # Relationships
    leave_balances = relationship("LeaveBalance", back_populates="leave_type")
    leave_requests = relationship("LeaveRequest", back_populates="leave_type")
    
    def __repr__(self):
        return f"<LeaveType(name='{self.name}', default_quota={self.default_quota})>"


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    remaining_days = Column(Integer, nullable=False, default=0)
    
    # Relationships
    user = relationship("User", back_populates="leave_balances")
    leave_type = relationship("LeaveType", back_populates="leave_balances")
    
    def __repr__(self):
        return f"<LeaveBalance(user_id={self.user_id}, leave_type_id={self.leave_type_id}, remaining_days={self.remaining_days})>"


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum(RequestStatus), nullable=False, default=RequestStatus.PENDING)
    notes = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    employee = relationship("User", back_populates="leave_requests_as_employee", foreign_keys=[employee_id])
    manager = relationship("User", back_populates="leave_requests_as_manager", foreign_keys=[manager_id])
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    
    def __repr__(self):
        return f"<LeaveRequest(id={self.id}, employee_id={self.employee_id}, status='{self.status}')>"


class CorporateHoliday(Base):
    __tablename__ = "corporate_holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    description = Column(String(100), nullable=False)
    
    def __repr__(self):
        return f"<CorporateHoliday(date='{self.date}', description='{self.description}')>"