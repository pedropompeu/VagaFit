"""Router da versão 1 da API. Cada fase registra aqui os seus routers.

Toda rota nova exige autenticação (`CurrentUserDep`), exceto as listadas em
`PUBLIC_ROUTES`. O teste `tests/unit/test_route_protection.py` garante isso.
"""

from fastapi import APIRouter

from app.api.v1 import analyses, auth, jobs, resumes

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(resumes.router)
api_router.include_router(jobs.router)
api_router.include_router(analyses.router)

# (método, caminho completo). Mudar esta lista é decisão de segurança: justificar no PR.
PUBLIC_ROUTES: frozenset[tuple[str, str]] = frozenset(
    {
        ("POST", "/api/v1/auth/register"),
        ("POST", "/api/v1/auth/login"),
        ("POST", "/api/v1/auth/refresh"),
        ("POST", "/api/v1/auth/logout"),
    }
)
