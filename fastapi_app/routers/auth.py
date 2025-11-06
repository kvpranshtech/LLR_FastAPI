from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import random
from datetime import datetime, timedelta

from fastapi_app.database import SessionLocal
from fastapi_app.schemas.auth import (
    SignupInitiateRequest, SignupResponse, EmailOTPVerifyRequest,
    MobileOTPVerifyRequest, ResendMobileOTPRequest, ResendEmailOTPRequest,
    OTPVerifyResponse, ErrorResponse
)
from fastapi_app.models.existing import User, EmailAddress, UserProfile, UserAcceptPolicies
from fastapi_app.core.security import get_password_hash
from fastapi_app.core.utils import send_email, send_phone_otp, verify_mobile_otp

router = APIRouter(prefix="/auth", tags=["authentication"])


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


VALID_PLATFORMS = ['phone', 'mobile', 'web', 'ios', 'android']


def validate_platform(platform: str) -> str:
    if not platform:
        return 'phone'
    if platform.lower() not in [p.lower() for p in VALID_PLATFORMS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platform specified"
        )
    return platform.lower()


@router.post("/signup/initiate", response_model=SignupResponse)
async def initiate_signup(
        request: SignupInitiateRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    try:
        platform = validate_platform(request.platform)

        # Check if user already exists
        if db.query(User).filter(User.email == request.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already exists"
            )

        if db.query(User).filter(User.username == request.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create user
        user = User(
            email=request.email,
            username=request.username,
            is_active=False  # User will be activated after verification
        )
        user.password = get_password_hash(request.password1)
        user.email_otp = str(random.randint(100000, 999999))
        user.email_otp_created_at = datetime.utcnow()

        db.add(user)
        db.flush()  # Get the user ID without committing

        # Create user profile
        user_profile = UserProfile(
            user_id=user.id,
            phone_number=request.phone_number,
            phone_verified=False,
            registration_platform=platform
        )
        db.add(user_profile)

        # Create email address entry
        email_address = EmailAddress(
            user_id=user.id,
            email=request.email,
            otp=user.email_otp,
            verified=False,
            primary=True
        )
        db.add(email_address)

        # Save policy acceptances
        if request.accept_privacy_policy:
            privacy_policy = UserAcceptPolicies(
                user_id=user.id,
                policy_type=UserAcceptPolicies.PolicyType.PRIVACY_POLICY,
                user_ipaddress="0.0.0.0",  # You can get this from request
                user_browser="FastAPI"  # You can get this from request headers
            )
            db.add(privacy_policy)

        if request.accept_terms_of_service:
            terms_policy = UserAcceptPolicies(
                user_id=user.id,
                policy_type=UserAcceptPolicies.PolicyType.TERMS_OF_SERVICES,
                user_ipaddress="0.0.0.0",
                user_browser="FastAPI"
            )
            db.add(terms_policy)

        if request.accept_refund_policy:
            refund_policy = UserAcceptPolicies(
                user_id=user.id,
                policy_type=UserAcceptPolicies.PolicyType.REFUND_POLICY,
                user_ipaddress="0.0.0.0",
                user_browser="FastAPI"
            )
            db.add(refund_policy)

        db.commit()

        # Send OTPs in background
        background_tasks.add_task(send_email_otp, request.email, user.email_otp)

        # Send mobile OTP
        mobile_response = send_phone_otp(request.phone_number)
        if mobile_response.get('error'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send mobile OTP: {mobile_response['error']}"
            )

        return SignupResponse(
            message="Registration initiated successfully. Please verify your email and phone number.",
            user_id=user.id,
            email=user.email,
            phone_number=request.phone_number,
            email_otp=user.email_otp,  # Remove this in production
            verification_required=True,
            platform=platform
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/signup/verify-email-otp", response_model=OTPVerifyResponse)
async def verify_email_otp(
        request: EmailOTPVerifyRequest,
        db: Session = Depends(get_db)
):
    # Find email address
    email_obj = db.query(EmailAddress).filter(
        EmailAddress.email == request.email,
        EmailAddress.otp == request.otp,
        EmailAddress.verified == False
    ).first()

    if not email_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    # Check OTP expiration (10 minutes)
    if email_obj.otp_created_at:
        expiry_time = email_obj.otp_created_at + timedelta(minutes=10)
        if datetime.utcnow() > expiry_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired"
            )

    try:
        # Verify email
        email_obj.verified = True
        email_obj.verification_date = datetime.utcnow()

        # Check if phone is also verified and activate user
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == email_obj.user_id
        ).first()

        if user_profile and user_profile.phone_verified:
            email_obj.user.is_active = True

        db.commit()

        return OTPVerifyResponse(
            message="Email OTP verified successfully.",
            is_active=email_obj.user.is_active
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.post("/signup/verify-mobile-otp", response_model=OTPVerifyResponse)
async def verify_mobile_otp(
        request: MobileOTPVerifyRequest,
        db: Session = Depends(get_db)
):
    # Verify mobile OTP with external service
    verification_response = verify_mobile_otp(
        mobile_number=request.phone_number,
        otp=request.otp
    )

    if verification_response.get('error'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    try:
        # Find user profile
        user_profile = db.query(UserProfile).filter(
            UserProfile.phone_number == request.phone_number
        ).order_by(UserProfile.id.desc()).first()

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        # Update user profile
        user_profile.otp_verified = True
        user_profile.phone_verified = True
        user_profile.otp_expiration = datetime.utcnow() + timedelta(minutes=10)

        # Check if email is verified
        email_address = db.query(EmailAddress).filter(
            EmailAddress.user_id == user_profile.user_id,
            EmailAddress.email == request.email
        ).first()

        email_verified = False
        if email_address and email_address.verified:
            user_profile.user.is_active = True
            email_verified = True
        else:
            # Resend email OTP if not verified
            new_otp = str(random.randint(100000, 999999))
            user_profile.otp = new_otp
            if email_address:
                email_address.otp = new_otp
            # Send email OTP
            send_email_otp(request.email, new_otp)

        db.commit()

        return OTPVerifyResponse(
            message="Mobile OTP verified successfully.",
            is_active=user_profile.user.is_active,
            email_verified=email_verified
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.post("/signup/resend-mobile-otp")
async def resend_mobile_otp(
        request: ResendMobileOTPRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Send mobile OTP
    mobile_response = send_phone_otp(request.phone_number)
    if mobile_response.get('error'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send mobile OTP: {mobile_response['error']}"
        )

    return {"message": "Mobile OTP resent successfully."}


@router.post("/signup/resend-email-otp")
async def resend_email_otp(
        request: ResendEmailOTPRequest,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate new OTP
    new_otp = str(random.randint(100000, 999999))
    user.email_otp = new_otp
    user.email_otp_created_at = datetime.utcnow()

    # Update email address
    email_address = db.query(EmailAddress).filter(
        EmailAddress.user_id == user.id,
        EmailAddress.email == request.email
    ).first()
    if email_address:
        email_address.otp = new_otp

    db.commit()

    # Send email OTP
    background_tasks.add_task(send_email_otp, request.email, new_otp)

    return {"message": "Email OTP resent successfully."}


# Helper function to send email OTP
def send_email_otp(email: str, otp: str):
    subject = 'Email Verification OTP'
    message = f'Your OTP for email verification is: {otp}'
    try:
        send_email(email, subject, message)
        return True
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Failed to send email OTP: {str(e)}")
        return False