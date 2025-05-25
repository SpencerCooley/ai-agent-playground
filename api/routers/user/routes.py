from fastapi import APIRouter, Depends, HTTPException
from types_definitions.user import PublicUser
from dependencies.dependencies import get_current_user
from types_definitions.user import UserCredentials, AuthToken, LogoutSuccess, CreateUserObject, PublicUser
from dependencies.dependencies import get_db
from sqlalchemy.orm import Session
import controllers

router = APIRouter(
    prefix="/user",
    tags=["Users"],
    # dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=PublicUser)
async def create_new_user(user: CreateUserObject, db: Session = Depends(get_db)):
    created_user = controllers.user.create(db, user)
    if created_user == None:
        email = user.email
        raise HTTPException(
            status_code=409, detail=f"A user with email {email} already exists")
    return created_user

@router.get("/me", response_model=PublicUser)
async def get_current_user(current_user: PublicUser = Depends(get_current_user)):
    return current_user
