from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_doc_url(client: AsyncClient):
    response = await client.get("/docs")
    assert response.status_code == 200

