from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
    query = db.query(User)
    total = query.count()
    users = query.order_by(User.created_at).offset(skip).limit(min(limit, 100)).all()
    return users, total

def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: UserRole = UserRole.MEMBER,
) -> User:
    db_user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def update_user_role(db: Session, user_id: int, new_role: UserRole) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if user is None:
        return None
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user
