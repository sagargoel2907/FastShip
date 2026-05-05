from pydantic import BaseModel, Field


class ShipmentReviewCreate(BaseModel):
    rating: int = Field(gt=1, le=5)
    comment: str | None = Field(default=None)
