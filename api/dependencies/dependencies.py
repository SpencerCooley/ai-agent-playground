from fastapi import Header, Depends, status
from fastapi.exceptions import HTTPException
from typing import Annotated
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from models.user import Token, User
from sqlalchemy.orm import Session
import os
import sys
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
sys.path.append(BASE_DIR)


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

# use this as middleware for requests. pass as a depenedency
# will create one for auth


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(
            status_code=400, detail="No Jessica token provided")


async def get_db():
    DATABASE_URL = os.environ['DATABASE_URL']
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# will act as the dependency when you require a user login.
# user object will always be available through this when it is required.
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Verify the token and retrieve the user
    db_token = db.query(Token).filter(Token.token == token).first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not db_token.is_active:
        raise HTTPException(status_code=401, detail="Token is inactive")

    # Check if the token is expired
    if db_token.expires_at and db_token.expires_at < datetime.utcnow():
        # Token is expired, update is_active to False and raise an exception
        db_token.is_active = False
        db.commit()
        raise HTTPException(status_code=401, detail="Token has expired")

    return db_token.user

async def require_superuser_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to check if the current user is a superuser or admin.
    Raises 403 if user doesn't have required role.
    """
    if current_user.role not in ["superuser", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Requires superuser or admin role."
        )
    return current_user
