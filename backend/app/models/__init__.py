"""Models SQLAlchemy. Importar cada model aqui para o Alembic enxergar a metadata."""

from app.db.base import Base
from app.models.analysis import Analysis
from app.models.job import Job
from app.models.refresh_token import RefreshToken
from app.models.resume import Resume, ResumeChunk
from app.models.screening import ScreeningAnswer
from app.models.user import User

__all__ = [
    "Analysis",
    "Base",
    "Job",
    "RefreshToken",
    "Resume",
    "ResumeChunk",
    "ScreeningAnswer",
    "User",
]
