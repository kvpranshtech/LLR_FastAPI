from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from fastapi_app.models.existing import User, EmailAddress, UserProfile
from sqlalchemy.orm import Session


class SignupInitiateRequest(BaseModel):
    username: str
    email: EmailStr
    password1: str
    password2: str
    phone_number: str
    referral_code: Optional[str] = None
    referral_url: Optional[str] = None
    reference_source: Optional[str] = None
    promo_code: Optional[str] = None
    platform: Optional[str] = "phone"
    accept_privacy_policy: bool
    accept_terms_of_service: bool
    accept_refund_policy: bool

    @validator('password2')
    def passwords_match(cls, v, values):
        if 'password1' in values and v != values['password1']:
            raise ValueError('Passwords do not match')
        return v

    @validator('email')
    def email_unique(cls, v):
        # We'll check this in the endpoint with database session
        return v

    @validator('username')
    def username_unique(cls, v):
        # We'll check this in the endpoint with database session
        return v


class EmailOTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str


class MobileOTPVerifyRequest(BaseModel):
    phone_number: str
    otp: str
    email: EmailStr


class ResendMobileOTPRequest(BaseModel):
    phone_number: str
    email: EmailStr


class ResendEmailOTPRequest(BaseModel):
    email: EmailStr


class SignupResponse(BaseModel):
    message: str
    user_id: int
    email: str
    phone_number: str
    email_otp: str
    verification_required: bool
    platform: str


class OTPVerifyResponse(BaseModel):
    message: str
    is_active: bool
    email_verified: Optional[bool] = None


class ErrorResponse(BaseModel):
    error: str
    success: Optional[bool] = False
    block: Optional[bool] = False
