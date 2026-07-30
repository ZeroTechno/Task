import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Auth & Protection API")

security = HTTPBearer()


class AuthCredentials(BaseModel):
    email: str
    password: str

# I will add the roles of the codes and stages below
# --- STAGE 0 & PUBLIC ENDPOINTS ---

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Server running and connected to Supabase"}

@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


# --- STAGE 1: SIGNUP & LOGIN ---

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: AuthCredentials):
    if not credentials.email.strip() or not credentials.password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email.strip(),
            "password": credentials.password.strip()
        })
        if not response.user:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {"message": "User created successfully", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(credentials: AuthCredentials):
    if not credentials.email.strip() or not credentials.password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email.strip(),
            "password": credentials.password.strip()
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": response.user
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")


# --- STAGE 3: TOKEN VERIFICATION DEPENDENCY ---

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Verify token with Supabase Auth
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user_response.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# --- STAGE 2 & 3: PROTECTED PROFILE ROUTE ---

@app.get("/protected/profile")
def get_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }