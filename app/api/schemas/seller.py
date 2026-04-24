from pydantic import BaseModel, Field, EmailStr

class BaseSeller(BaseModel):
    name: str = Field(max_length=20)
    email: EmailStr

class SellerRead(BaseSeller):
    id: int

class SellerCreate(BaseSeller):
    password: str

class SellerUpdate:
    name: str | None = Field(max_length=20, default=None)
    email: EmailStr | None = Field(default=None)
