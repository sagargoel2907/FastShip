from contextlib import asynccontextmanager

from fastapi import FastAPI
from rich import panel, print
from scalar_fastapi import get_scalar_api_reference

from app.core.exceptions import add_exception_handlers

from .database.session import create_db_and_tables
from .api.router import master_router

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    print(panel.Panel("Server started", border_style="green"))
    await create_db_and_tables()
    yield
    print(panel.Panel("Server shutdown", border_style="red"))


description = ""
app = FastAPI(
    lifespan=lifespan_handler,
    title="FastShip",
    description=description,
    version="0.1.0",
    contact={"name": "Sagar Goel", "email": "sagargoel2907@gmail.com"},
    docs_url=None,
    redoc_url=None
)

app.include_router(router=master_router)
add_exception_handlers(app)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])


@app.get("/docs", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url, title="Scalar Docs", dark_mode=True
    )
