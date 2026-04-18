"""
Auth endpoints — login / token refresh.
Add real logic here when you wire up the User model.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.schemas.auth import Token

router = APIRouter()


@router.post("/login", response_model=Token, summary="Obtain access token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login.
    Replace the stub below with a real DB user lookup and password check.
    """
    # --- TODO: fetch user from DB and verify password ---
    # user = user_service.get_by_email(db, form_data.username)
    # if not user or not verify_password(form_data.password, user.hashed_password):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Stub — always succeeds for now
    access_token = create_access_token(data={"sub": form_data.username})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", summary="Logout (client-side token removal)")
async def logout():
    """
    JWT tokens are stateless; logout is handled client-side by discarding the token.
    If you need server-side revocation, implement a token blocklist here.
    """
    return {"message": "Successfully logged out"}
