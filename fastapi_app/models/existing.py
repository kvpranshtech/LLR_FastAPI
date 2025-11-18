# fastapi_app/models/existing.py
from fastapi_app.database import metadata

# Safe table access - use .get() method
User = metadata.tables.get('auth_user')
EmailAddress = metadata.tables.get('app_emailaddress') 
UserProfile = metadata.tables.get('app_userprofile')
UserAcceptPolicies = metadata.tables.get('app_useracceptpolicies')

# Print what we found (safe check using is not None)
print("Tables found:")
print(f"  auth_user: {'✓' if User is not None else '✗ (not found)'}")
print(f"  app_emailaddress: {'✓' if EmailAddress is not None else '✗ (not found)'}")
print(f"  app_userprofile: {'✓' if UserProfile is not None else '✗ (not found)'}")
print(f"  app_useracceptpolicies: {'✓' if UserAcceptPolicies is not None else '✗ (not found)'}")

# If tables don't exist, set them to None
if User is None:
    print("Warning: auth_user table not found in database")
if EmailAddress is None:
    print("Warning: app_emailaddress table not found in database") 
if UserProfile is None:
    print("Warning: app_userprofile table not found in database")
if UserAcceptPolicies is None:
    print("Warning: app_useracceptpolicies table not found in database")