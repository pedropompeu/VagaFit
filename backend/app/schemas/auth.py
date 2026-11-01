import re
import uuid
from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

# Validação simples de formato. Sem verificação de e-mail no MVP, o formato é só higiene.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128  # teto evita DoS no argon2 com senha gigante (S7)


def _normalize_email(value: str) -> str:
    value = value.strip().lower()
    if not _EMAIL_RE.match(value):
        raise ValueError("E-mail inválido.")
    return value


Email = Annotated[
    str,
    StringConstraints(max_length=254),
    AfterValidator(_normalize_email),
    Field(examples=["ana@exemplo.com"]),
]
NewPassword = Annotated[
    str,
    Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        examples=["uma-senha-longa"],
    ),
]
# No login e na confirmação não se revela a política de senha: só o teto.
AnyPassword = Annotated[str, Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)]


class RegisterRequest(BaseModel):
    email: Email
    password: NewPassword


class LoginRequest(BaseModel):
    email: Email
    password: AnyPassword


class DeleteAccountRequest(BaseModel):
    password: AnyPassword


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    created_at: datetime


class AuthResponse(BaseModel):
    """Access token no corpo (o front guarda em memória). O refresh vai no cookie httpOnly."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105 - tipo do token, não é segredo
    expires_in: int = Field(description="Validade do access token, em segundos.", examples=[900])
    user: UserRead
