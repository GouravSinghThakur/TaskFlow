from typing import Callable, Sequence

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.crud.user import get_user_by_id
from app.db.session import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_token(token)
    if user_id is None:
        raise credentials_exception

    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    user = get_user_by_id(db, uid)
    if user is None:
        raise credentials_exception

    return user

def require_admin_role(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Admin role required. "
                "Contact an administrator to request elevated access."
            ),
        )
    return current_user

def require_member_role(
    current_user: User = Depends(get_current_user),
) -> User:
    allowed = {UserRole.ADMIN, UserRole.MEMBER}
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )
    return current_user

def require_roles(*roles: UserRole) -> Callable:
    """Dependency factory — require the caller to hold one of the given roles.

    Use this when you need a custom combination of roles, e.g.::

        @router.get("/report")
        def report(user: Annotated[User, Depends(require_roles(UserRole.ADMIN))]):
            ...

    Args:
        *roles: One or more :class:`UserRole` values that are permitted.

    Returns:
        A FastAPI-compatible dependency callable.
    """
    allowed: frozenset[UserRole] = frozenset(roles)

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            role_names = ", ".join(r.value for r in sorted(allowed, key=lambda r: r.value))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role(s): {role_names}. Your role: {current_user.role.value}.",
            )
        return current_user

    _dependency.__name__ = f"require_roles({'|'.join(r.value for r in allowed)})"
    return _dependency
