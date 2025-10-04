from httpx import AsyncClient

from app.tests import example


async def test_app(client: AsyncClient):
    response = await client.get("/scalar")
    assert response.status_code == 200


async def test_seller_login(client: AsyncClient):
    response = await client.post(
        "/seller/token",
        data={
            "grant_type": "password",
            "username": example.SELLER["email"],
            "password": example.SELLER["password"],
        },
    )

    print(response.json())
