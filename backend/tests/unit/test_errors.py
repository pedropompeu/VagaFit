from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel

from app.core.errors import AppError, NotFoundError


class Payload(BaseModel):
    name: str


def _add_routes(app: FastAPI) -> None:
    @app.get("/_test/not-found")
    async def not_found() -> None:
        raise NotFoundError("Currículo não encontrado.")

    @app.get("/_test/custom")
    async def custom() -> None:
        raise AppError("Cota esgotada.", code="quota_exceeded", status_code=429)

    @app.post("/_test/validate")
    async def validate(payload: Payload) -> Payload:
        return payload

    @app.get("/_test/boom")
    async def boom() -> None:
        raise RuntimeError("segredo interno que não pode vazar")


async def test_app_error_uses_standard_format(app: FastAPI, client: AsyncClient) -> None:
    _add_routes(app)

    response = await client.get("/_test/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Currículo não encontrado."}
    }


async def test_app_error_accepts_custom_code_and_status(app: FastAPI, client: AsyncClient) -> None:
    _add_routes(app)

    response = await client.get("/_test/custom")

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "quota_exceeded"


async def test_unknown_route_uses_standard_format(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "Not Found"}}


async def test_validation_error_uses_standard_format(app: FastAPI, client: AsyncClient) -> None:
    _add_routes(app)

    response = await client.post("/_test/validate", json={})

    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "validation_error"
    assert body["details"][0]["loc"] == ["body", "name"]


async def test_unhandled_error_hides_internal_message(app: FastAPI, client: AsyncClient) -> None:
    _add_routes(app)

    response = await client.get("/_test/boom")

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": "Erro interno inesperado."}
    }
    assert "segredo" not in response.text
