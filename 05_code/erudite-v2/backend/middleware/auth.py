import os
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth

security = HTTPBearer()

# Initialize Firebase Admin SDK keylessly (uses ADC on Cloud Run)
try:
    firebase_admin.initialize_app()
    print("Firebase Admin SDK successfully initialized keylessly.")
except ValueError:
    # Already initialized
    pass
except Exception as e:
    print(f"Warning: Firebase initialization fallback: {e}")

async def verify_token(request: Request) -> dict:
    """
    Middleware function to decode and verify JWT authorization headers keylessly.
    In development mode, bypasses verification and yields a mock admin user.
    """
    if os.environ.get("APP_ENV") == "development":
        return {
            "uid": "dev-user",
            "role": "admin",
            "email": "counselor@erudite.dev",
            "display_name": "Calming Counselor"
        }

    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")

    token = authorization.split("Bearer ")[1]
    try:
        # Decodes token keylessly on Google Cloud Run using project-bound permissions
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")
