from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, LeaveType, LeaveBalance, CorporateHoliday, UserRole
from datetime import date
import structlog

logger = structlog.get_logger()

# Demo data
demo_users = [
    {"username": "admin", "email": "admin@example.com", "role": UserRole.ADMIN},
    {"username": "manager", "email": "manager@example.com", "role": UserRole.MANAGER},
    {"username": "alice", "email": "alice@example.com", "role": UserRole.EMPLOYEE, "manager_username": "manager"},
]

demo_leave_types = [
    {"name": "Vacation", "default_quota": 15},
    {"name": "Sick", "default_quota": 10},
    {"name": "Maternity", "default_quota": 90},
    {"name": "Paternity", "default_quota": 15},
    {"name": "Floating", "default_quota": 2},
]

demo_holidays = [
    {"date": "2024-01-01", "description": "New Year's Day"},
    {"date": "2024-07-04", "description": "Independence Day"},
    {"date": "2024-12-25", "description": "Christmas Day"},
    {"date": "2025-01-01", "description": "New Year's Day"},
    {"date": "2025-07-04", "description": "Independence Day"},
    {"date": "2025-12-25", "description": "Christmas Day"},
]


async def seed_demo_data():
    """Seed the database with demo data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info("Demo data already exists, skipping seed")
            return
        
        logger.info("Starting demo data seeding")
        
        # Create leave types first
        leave_types = {}
        for lt_data in demo_leave_types:
            leave_type = LeaveType(**lt_data)
            db.add(leave_type)
            db.flush()  # Get the ID
            leave_types[lt_data["name"]] = leave_type
            logger.info(f"Created leave type: {lt_data['name']}")
        
        # Create users
        users = {}
        for user_data in demo_users:
            user_dict = user_data.copy()
            manager_username = user_dict.pop("manager_username", None)
            
            user = User(**user_dict)
            db.add(user)
            db.flush()  # Get the ID
            users[user_dict["username"]] = user
            logger.info(f"Created user: {user_dict['username']} ({user_dict['role']})")
        
        # Set manager relationships
        for user_data in demo_users:
            manager_username = user_data.get("manager_username")
            if manager_username:
                user = users[user_data["username"]]
                manager = users[manager_username]
                user.manager_id = manager.id
                logger.info(f"Set {user.username}'s manager to {manager.username}")
        
        # Create leave balances for employees
        for username, user in users.items():
            if user.role == UserRole.EMPLOYEE:
                for leave_type in leave_types.values():
                    balance = LeaveBalance(
                        user_id=user.id,
                        leave_type_id=leave_type.id,
                        remaining_days=leave_type.default_quota
                    )
                    db.add(balance)
                    logger.info(f"Created balance: {user.username} - {leave_type.name}: {leave_type.default_quota} days")
        
        # Create corporate holidays
        for holiday_data in demo_holidays:
            holiday = CorporateHoliday(
                date=date.fromisoformat(holiday_data["date"]),
                description=holiday_data["description"]
            )
            db.add(holiday)
            logger.info(f"Created holiday: {holiday_data['date']} - {holiday_data['description']}")
        
        # Commit all changes
        db.commit()
        logger.info("Demo data seeding completed successfully")
        
    except Exception as e:
        logger.error("Failed to seed demo data", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()