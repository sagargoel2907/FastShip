from contextlib import asynccontextmanager

from fastapi import FastAPI
from rich import panel, print
from scalar_fastapi import get_scalar_api_reference

from .database.session import create_db_and_tables
from .api.router import router


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    print(panel.Panel('Server started', border_style='green'))
    await create_db_and_tables()
    yield 
    print(panel.Panel('Server shutdown', border_style='red'))

app = FastAPI(lifespan=lifespan_handler)

app.include_router(router=router)

@app.get('/scalar-docs', include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title='Scalar Docs', dark_mode= True)
