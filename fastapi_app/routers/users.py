from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_app.database import SessionLocal
from fastapi_app.models.existing import User, EmailAddress, UserProfile

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users/")
def get_users(db: Session = Depends(get_db)):
    # Check if User table exists (use "is not None" instead of "if User")
    if User is None:
        raise HTTPException(
            status_code=503,
            detail="User table not available in database. Please check if the tables exist."
        )

    # Your user query logic here
    # users = db.query(User).all()
    return {"message": "Users endpoint working - table exists"}


@router.get("/users/check-tables")
def check_tables():
    """Endpoint to check table availability"""
    tables_status = {
        "auth_user": User is not None,
        "app_emailaddress": EmailAddress is not None,
        "app_userprofile": UserProfile is not None
    }
    return {"table_status": tables_status}


@router.get("/users/test")
def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Users router is working!"}