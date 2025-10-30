"""Operational data store for the call center application."""
from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator, Optional

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, MetaData, String, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .config import get_config
from .models import AgentStatus, InteractionChannel, Role


metadata = MetaData(schema="public")


class Base(AsyncAttrs, DeclarativeBase):
    metadata = metadata


class AgentRecord(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(128))
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"))
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus, name="agent_status"))
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    interactions: Mapped[list["InteractionRecord"]] = relationship(back_populates="agent")


class QueueRecord(Base):
    __tablename__ = "queues"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    business_hours: Mapped[dict] = mapped_column(JSON, default=dict)
    overflow_queue: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    recording_retention_days: Mapped[int] = mapped_column(Integer, default=60)

    interactions: Mapped[list["InteractionRecord"]] = relationship(back_populates="queue")


class InteractionRecord(Base):
    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(64))
    queue_name: Mapped[str] = mapped_column(ForeignKey("queues.name"))
    channel: Mapped[InteractionChannel] = mapped_column(Enum(InteractionChannel, name="channel"))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(ForeignKey("agents.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    queue: Mapped[QueueRecord] = relationship(back_populates="interactions")
    agent: Mapped[Optional[AgentRecord]] = relationship(back_populates="interactions")


class AuditRecord(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    actor: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(128))
    details: Mapped[dict] = mapped_column(JSON, default=dict)


class RecordingRecord(Base):
    __tablename__ = "recordings"

    interaction_id: Mapped[str] = mapped_column(ForeignKey("interactions.id"), primary_key=True)
    location: Mapped[str] = mapped_column(String(255))
    encrypted_blob: Mapped[bytes] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def create_engine():
    config = get_config()
    return create_async_engine(config.database_url, echo=False, future=True)


async def create_session_factory() -> async_sessionmaker[AsyncSession]:
    engine = create_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_agent(session: AsyncSession, agent_id: str) -> Optional[AgentRecord]:
    result = await session.execute(select(AgentRecord).where(AgentRecord.id == agent_id))
    return result.scalar_one_or_none()


async def list_active_interactions(session: AsyncSession) -> list[InteractionRecord]:
    result = await session.execute(
        select(InteractionRecord).where(InteractionRecord.status.in_(["queued", "assigned", "in_progress"]))
    )
    return list(result.scalars())


async def iter_audit_records(session: AsyncSession) -> AsyncIterator[AuditRecord]:
    result = await session.stream(select(AuditRecord).order_by(AuditRecord.timestamp))
    async for row in result:
        yield row[0]


__all__ = [
    "AgentRecord",
    "AuditRecord",
    "InteractionRecord",
    "QueueRecord",
    "RecordingRecord",
    "create_engine",
    "create_session_factory",
    "get_agent",
    "iter_audit_records",
    "list_active_interactions",
]

