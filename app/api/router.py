from fastapi import APIRouter
from .routers import seller, shipment

master_router = APIRouter()

master_router.include_router(router=shipment.router)
master_router.include_router(router=seller.router)