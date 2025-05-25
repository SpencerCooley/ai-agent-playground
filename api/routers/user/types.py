from pydantic import BaseModel,  EmailStr


class UserSchema(BaseModel):
    email: EmailStr
    id: int
