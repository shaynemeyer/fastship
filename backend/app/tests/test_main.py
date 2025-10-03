from httpx import AsyncClient


async def test_app(client: AsyncClient):
    response = await client.get("/scalar")
    assert response.status_code == 200
