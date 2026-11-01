"""Models SQLAlchemy. Importar cada model aqui para o Alembic enxergar a metadata."""

from app.db.base import Base
from app.models.refresh_token import RefreshToken
from app.models.resume import Resume, ResumeChunk
from app.models.user import User

__all__ = ["Base", "RefreshToken", "Resume", "ResumeChunk", "User"]
