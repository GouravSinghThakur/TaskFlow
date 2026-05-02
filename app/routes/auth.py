from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user, require_admin_role
from app.core.security import create_access_token
from app.crud.user import authenticate_user, create_user, get_user_by_email, get_all_users, get_user_by_id, update_user_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse, RoleUpdate

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def _build_token_response(user: User) -> dict:
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

@router.post(
    "/signup",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        400: {"description": "Email already registered"},
        422: {"description": "Validation error (weak password, invalid email, …)"},
    },
)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    db_user = create_user(
        db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
    )
    return _build_token_response(db_user)

@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and obtain a JWT token",
    responses={
        401: {"description": "Invalid email or password"},
        422: {"description": "Validation error"},
    },
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = authenticate_user(db, form_data.username, form_data.password)
    if not db_user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _build_token_response(db_user)

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current authenticated user",
    responses={401: {"description": "Not authenticated"}},
)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh the JWT access token",
    responses={401: {"description": "Not authenticated"}},
)
def refresh_token(current_user: User = Depends(get_current_user)):
    return _build_token_response(current_user)

@router.post(
    "/logout",
    summary="Logout (client-side token invalidation)",
    responses={401: {"description": "Not authenticated"}},
)
def logout(current_user: User = Depends(get_current_user)):
    return {
        "message": "Successfully logged out. Please discard the token on the client.",
        "user_id": current_user.id,
    }

from typing import Annotated, List  # noqa: E402 (local import keeps grouping clean)

@router.get(
    "/admin/users",
    response_model=List[UserResponse],
    summary="List all users (Admin only)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Admin role required"},
    },
)
def list_all_users(
    current_user: Annotated[User, Depends(require_admin_role)],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[UserResponse]:
    users, _ = get_all_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]

@router.patch(
    "/admin/users/{user_id}/role",
    response_model=UserResponse,
    summary="Change a user's role (Admin only)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Admin role required"},
        404: {"description": "User not found"},
    },
)
def change_user_role(
    user_id: int,
    payload: RoleUpdate,
    current_user: Annotated[User, Depends(require_admin_role)],
    db: Session = Depends(get_db),
) -> UserResponse:
    target = get_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )

    updated = update_user_role(db, user_id, payload.role)
    return UserResponse.model_validate(updated)
