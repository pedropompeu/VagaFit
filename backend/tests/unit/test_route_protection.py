"""Guarda mecânica de isolamento: toda rota de /api/v1 exige token, salvo a lista pública.

Uma rota nova sem `CurrentUserDep` quebra este teste.
"""

import re
import uuid

from fastapi import FastAPI
from fastapi.routing import APIRoute, iter_route_contexts
from httpx import AsyncClient

from app.api.v1.router import PUBLIC_ROUTES

_PATH_PARAM = re.compile(r"\{[^}]+\}")


def _api_routes(app: FastAPI) -> set[tuple[str, str]]:
    # O FastAPI 0.16x guarda routers incluídos como `_IncludedRouter`; `iter_route_contexts`
    # devolve cada rota com o caminho completo (prefixos aplicados).
    return {
        (method, ctx.path)
        for ctx in iter_route_contexts(app.routes)
        if isinstance(ctx.route, APIRoute) and ctx.path.startswith("/api/v1/")
        for method in ctx.methods or ()
        if method not in {"HEAD", "OPTIONS"}
    }


async def test_every_non_public_route_requires_authentication(
    app: FastAPI, client: AsyncClient
) -> None:
    protected = _api_routes(app) - PUBLIC_ROUTES
    assert protected, "nenhuma rota protegida encontrada"

    for method, path in sorted(protected):
        url = _PATH_PARAM.sub(str(uuid.uuid4()), path)
        response = await client.request(method, url, json={})

        assert response.status_code == 401, f"{method} {path} respondeu {response.status_code}"
        assert response.json()["error"]["code"] == "not_authenticated"
        assert response.headers["www-authenticate"] == "Bearer"


async def test_invalid_scheme_is_treated_as_missing(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me", headers={"Authorization": "Basic abc"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "not_authenticated"


def test_public_routes_exist(app: FastAPI) -> None:
    assert _api_routes(app) >= PUBLIC_ROUTES, "lista pública cita rota inexistente"
