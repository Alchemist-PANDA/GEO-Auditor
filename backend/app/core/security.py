from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from pydantic import BaseModel

security_scheme = HTTPBearer()

class UserSession(BaseModel):
    id: str
    email: str
    role: str

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> UserSession:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "member")
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims"
            )
        return UserSession(id=user_id, email=email, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
