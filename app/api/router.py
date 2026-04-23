from fastapi import APIRouter, HTTPException, status

from .dependencies import SessionDep
from .schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from .dependencies import ShipmentServiceDep

router = APIRouter()


@router.get("/shipment/{id}", response_model=ShipmentRead)
async def get_shipment(session: SessionDep, id: int, service: ShipmentServiceDep):
    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exists"
        )
    return shipment


@router.post("/shipment", response_model=ShipmentRead)
async def create_shipment(
    session: SessionDep, shipment: ShipmentCreate, service: ShipmentServiceDep
):
    db_shipment = await service.create(shipment)
    return db_shipment


@router.patch("/shipment/{id}", response_model=ShipmentRead)
async def update_shipment(
    session: SessionDep, shipment: ShipmentUpdate, id: int, service: ShipmentServiceDep
):
    db_shipment = await service.update(shipment, id)
    if not db_shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exists"
        )
    return db_shipment


@router.delete("/shipment/{id}")
async def delete_shipment(id: int, session: SessionDep, service: ShipmentServiceDep):
    await service.delete(id)
    return {"detail": f"Shipment having id #{id} has been deleted"}
