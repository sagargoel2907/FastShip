from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.database.models import ShipmentStatus


class ShipmentEventRead(BaseModel):
    id: UUID
    status: ShipmentStatus
    description: str
    location: int
    created_at: datetime
    