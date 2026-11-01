"""Acesso a `applications`. Toda query filtra pelo dono (`user_id`)."""

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application


class ApplicationRepository:
    def __init__(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        self._session = session
        self._user_id = user_id

    def _query(self) -> Select[Application]:
        return (
            select(Application)
            .where(Application.user_id == self._user_id)
            .options(selectinload(Application.job))
        )

    async def add(self, **fields: Any) -> Application:
        application = Application(user_id=self._user_id, **fields)
        self._session.add(application)
        await self._session.flush()
        return application

    async def get(self, application_id: uuid.UUID) -> Application | None:
        result = await self._session.execute(self._query().where(Application.id == application_id))
        return result.scalar_one_or_none()

    async def get_by_job(self, job_id: uuid.UUID) -> Application | None:
        result = await self._session.execute(self._query().where(Application.job_id == job_id))
        return result.scalar_one_or_none()

    async def list_all(self, *, statuses: Sequence[str] | None = None) -> list[Application]:
        query = self._query()
        if statuses:
            query = query.where(Application.status.in_(statuses))
        result = await self._session.execute(
            query.order_by(
                Application.applied_at.desc(), Application.created_at.desc(), Application.id
            )
        )
        return list(result.scalars())

    async def delete(self, application: Application) -> None:
        await self._session.delete(application)
        await self._session.flush()
