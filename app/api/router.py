from fastapi import APIRouter
from .routers import seller, shipment, delivery_partner

master_router = APIRouter()

master_router.include_router(router=shipment.router)
master_router.include_router(router=seller.router)
master_router.include_router(router=delivery_partner.router)