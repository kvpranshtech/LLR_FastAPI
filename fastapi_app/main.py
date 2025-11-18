# # fastapi_app/main.py
# from fastapi import FastAPI
# from fastapi_app.routers import auth, users
#
# app = FastAPI(title="FastAPI using Django DB")
#
# app.include_router(users.router)
#
# @app.get("/")
# def root():
#     return {"message": "FastAPI connected to Django PostgreSQL DB!"}
#
#
# app = FastAPI(title="LLR FastAPI", version="1.0.0")
#
# # Include routers
# app.include_router(auth.router, prefix="/auth", tags=["authentication"])
# app.include_router(users.router, prefix="/users", tags=["users"])
# app.include_router(auth.router, prefix="/user_api/apiv2")
#
# @app.get("/")
# async def root():
#     return {"message": "LLR FastAPI is running"}
#
# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}
#
# @app.get("/test-main")
# async def test_main():
#     return {"message": "Main app is working"}
#
# @app.get("/test-routers")
# async def test_routers():
#     return {
#         "auth_router": "configured" if hasattr(auth, 'router') else "missing",
#         "users_router": "configured" if hasattr(users, 'router') else "missing"
#     }
#
#
# @app.get("/debug-routes")
# async def debug_routes():
#     routes = []
#     for route in app.routes:
#         if hasattr(route, "methods") and hasattr(route, "path"):
#             routes.append({
#                 "path": route.path,
#                 "methods": list(route.methods),
#                 "name": getattr(route, "name", "N/A")
#             })
#     return {"routes": routes}
#
#
# @app.get("/test-simple")
# async def test_simple():
#     return {"message": "Simple test works"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="LLR FastAPI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
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


# Basic endpoints
@app.get("/")
async def root():
    return {"message": "LLR FastAPI is running", "status": "success"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/test-simple")
async def test_simple():
    return {"message": "Simple test works"}


# User registration endpoints - EXACT PATHS
@app.post("/user_api/apiv2/user-register/initiate/")
async def initiate_signup(request: SignupInitiateRequest):
    return {
        "message": "Signup initiated successfully",
        "email": request.email,
        "phone_number": request.phone_number,
        "status": "pending_verification",
        "next_step": "verify_mobile_otp"
    }


@app.post("/user_api/apiv2/user-register/verify-mobile-otp/")
async def verify_mobile_otp(request: VerifyMobileOTPRequest):
    return {
        "message": "Mobile OTP verified successfully",
        "phone_number": request.phone_number,
        "status": "mobile_verified",
        "next_step": "verify_email_otp"
    }


@app.post("/user_api/apiv2/user-register/verify-email-otp/")
async def verify_email_otp(request: VerifyEmailOTPRequest):
    return {
        "message": "Email OTP verified successfully",
        "email": request.email,
        "status": "email_verified",
        "next_step": "registration_complete"
    }


@app.post("/user_api/apiv2/user-register/resend-mobile-otp/")
async def resend_mobile_otp(request: ResendOTPRequest):
    return {
        "message": "Mobile OTP resent successfully",
        "phone_number": request.phone_number,
        "status": "otp_sent"
    }


@app.post("/user_api/apiv2/user-register/resend-email-otp/")
async def resend_email_otp(request: ResendOTPRequest):
    return {
        "message": "Email OTP resent successfully",
        "email": request.email,
        "status": "otp_sent"
    }


# Debug endpoint to see all routes
@app.get("/debug-routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "N/A")
            })
    return {"routes": routes}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
