from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user import User
from types_definitions.user import CreateUserObject
from utils.password import get_password_hash

def create(db: Session, user: CreateUserObject):
    try:
        db_user = User(
            email=user.email,
            hashed_password=get_password_hash(user.password),
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None

