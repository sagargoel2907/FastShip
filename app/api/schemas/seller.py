from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

class BaseSeller(BaseModel):
    name: str = Field(max_length=20)
    email: EmailStr
    zipcode: int

class SellerRead(BaseSeller):
    id: UUID

class SellerCreate(BaseSeller):
    password: str

class SellerUpdate:
    name: str | None = Field(max_length=20, default=None)
    email: EmailStr | None = Field(default=None)
