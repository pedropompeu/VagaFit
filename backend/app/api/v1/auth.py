"""Rotas de autenticação. O refresh token só circula no cookie httpOnly (nunca no corpo)."""

from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Request, Response, status
from fastapi.responses import JSONResponse

from app.api.deps import AuthServiceDep, CurrentUserDep, SettingsDep
from app.core.config import Settings, get_settings
from app.core.errors import ErrorResponse, UnauthorizedError, error_response
from app.core.rate_limit import rate_limit
from app.schemas.auth import (
    AuthResponse,
    DeleteAccountRequest,
    LoginRequest,
    RegisterRequest,
    UserRead,
)
from app.services.auth import AuthResult

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = get_settings().refresh_cookie_name
RefreshCookie = Annotated[str | None, Cookie(alias=REFRESH_COOKIE, include_in_schema=False)]

_OpenAPIResponses = dict[int | str, dict[str, Any]]

_ERR_401: _OpenAPIResponses = {401: {"model": ErrorResponse, "description": "Não autenticado"}}
_ERR_429: _OpenAPIResponses = {429: {"model": ErrorResponse, "description": "Muitas tentativas"}}


def _set_refresh_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=token,
        max_age=settings.refresh_token_ttl_seconds,
        path=settings.refresh_cookie_path,
        secure=settings.cookie_secure,
        httponly=True,
        samesite="strict",
    )


def _clear_refresh_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=settings.refresh_cookie_path,
        secure=settings.cookie_secure,
        httponly=True,
        samesite="strict",
    )


def _auth_response(result: AuthResult, response: Response, settings: Settings) -> AuthResponse:
    _set_refresh_cookie(response, result.refresh_token, settings)
    return AuthResponse(
        access_token=result.access.token,
        expires_in=result.access.expires_in,
        user=UserRead.model_validate(result.user),
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Criar conta",
    description="Cria a conta, abre a sessão e devolve o access token. Limite: 3/min por IP.",
    responses={409: {"model": ErrorResponse, "description": "E-mail já cadastrado"}, **_ERR_429},
)
@rate_limit("3/minute")
async def register(
    request: Request,
    response: Response,
    body: RegisterRequest,
    service: AuthServiceDep,
    settings: SettingsDep,
) -> AuthResponse:
    result = await service.register(email=body.email, password=body.password)
    return _auth_response(result, response, settings)


@router.post(
    "/login",
    summary="Entrar",
    description="Mensagem de erro genérica para e-mail ou senha. Limite: 5/min por IP.",
    responses={**_ERR_401, **_ERR_429},
)
@rate_limit("5/minute")
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    service: AuthServiceDep,
    settings: SettingsDep,
) -> AuthResponse:
    result = await service.login(email=body.email, password=body.password)
    return _auth_response(result, response, settings)


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Renovar o access token",
    description=(
        "Usa o refresh token do cookie, gira o token e devolve um novo access token. "
        "Reuso de um refresh já girado revoga todas as sessões daquele login."
    ),
    responses=_ERR_401,
)
async def refresh(
    response: Response,
    service: AuthServiceDep,
    settings: SettingsDep,
    refresh_token: RefreshCookie = None,
) -> AuthResponse | JSONResponse:
    try:
        result = await service.refresh(refresh_token)
    except UnauthorizedError as exc:
        # Resposta montada aqui para também apagar o cookie inválido.
        error = error_response(exc.status_code, exc.code, exc.message, headers=exc.headers)
        _clear_refresh_cookie(error, settings)
        return error
    return _auth_response(result, response, settings)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sair",
    description="Revoga a sessão do cookie e apaga o cookie. Idempotente.",
)
async def logout(
    response: Response,
    service: AuthServiceDep,
    settings: SettingsDep,
    refresh_token: RefreshCookie = None,
) -> None:
    await service.logout(refresh_token)
    _clear_refresh_cookie(response, settings)


@router.get("/me", summary="Usuário atual", responses=_ERR_401)
async def me(user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir a conta",
    description=(
        "Exclusão definitiva, com todos os dados do usuário (LGPD). Exige a senha atual. "
        "Senha errada responde 403."
    ),
    responses={**_ERR_401, 403: {"model": ErrorResponse, "description": "Senha incorreta"}},
)
async def delete_me(
    body: DeleteAccountRequest,
    user: CurrentUserDep,
    response: Response,
    service: AuthServiceDep,
    settings: SettingsDep,
) -> None:
    await service.delete_account(user, password=body.password)
    _clear_refresh_cookie(response, settings)
