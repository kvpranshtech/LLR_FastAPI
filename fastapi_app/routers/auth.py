from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/user-api/apiv2/user-register", tags=["user-registration"])


# Pydantic models for request data
class SignupInitiateRequest(BaseModel):
    email: str
    password: str
    phone_number: str
    reference_through: str
    accept_privacy_policy: str
    accept_terms_of_service: str
    accept_refund_policy: str


class VerifyMobileOTPRequest(BaseModel):
    phone_number: str
    otp: str


class VerifyEmailOTPRequest(BaseModel):
    email: str
    otp: str


class ResendOTPRequest(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[str] = None


# Endpoints matching your Django routes
@router.post("/initiate/")
async def initiate_signup(request: SignupInitiateRequest):
    """Equivalent to Django's initiate endpoint"""
    return {
        "message": "Signup initiated successfully",
        "email": request.email,
        "phone_number": request.phone_number,
        "status": "pending_verification"
    }


@router.post("/verify-mobile-otp/")
async def verify_mobile_otp(request: VerifyMobileOTPRequest):
    """Verify mobile OTP"""
    return {
        "message": "Mobile OTP verified successfully",
        "phone_number": request.phone_number,
        "status": "mobile_verified"
    }


@router.post("/verify-email-otp/")
async def verify_email_otp(request: VerifyEmailOTPRequest):
    """Verify email OTP"""
    return {
        "message": "Email OTP verified successfully",
        "email": request.email,
        "status": "email_verified"
    }


@router.post("/resend-mobile-otp/")
async def resend_mobile_otp(request: ResendOTPRequest):
    """Resend mobile OTP"""
    return {
        "message": "Mobile OTP resent successfully",
        "phone_number": request.phone_number
    }


@router.post("/resend-email-otp/")
async def resend_email_otp(request: ResendOTPRequest):
    """Resend email OTP"""
    return {
        "message": "Email OTP resent successfully",
        "email": request.email
    }


