"""FastAPI dependency injection."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.collaboration.service import CollaborationService
from app.config import Settings
from app.distributed.monitoring_service import MonitoringService
from app.services.auth_service import AuthService
from app.ai.service import AIService
from app.services.audit_service import AuditService
from app.services.dashboard_service import DashboardService
from app.services.engine_service import EngineService
from app.services.export_service import ExportService
from app.services.game_service import GameService
from app.services.game_version_service import GameVersionService
from app.services.mathematics_service import MathematicsService
from app.services.notification_service import NotificationService
from app.services.invitation_service import InvitationService
from app.services.organization_service import OrganizationService
from app.services.settings_service import SettingsService
from app.services.simulation_service import SimulationService
from app.services.validation_service import ValidationService


def get_settings(request: Request) -> Settings:
    settings = getattr(request.app.state, "settings", None)
    if settings is None:
        msg = "application settings not configured"
        raise RuntimeError(msg)
    return settings


def get_engine_service(request: Request) -> EngineService:
    return EngineService(settings=get_settings(request))


def get_validation_service(request: Request) -> ValidationService:
    service = getattr(request.app.state, "validation_service", None)
    if service is None:
        msg = "validation service not configured"
        raise RuntimeError(msg)
    return service


def _session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    factory = getattr(request.app.state, "session_factory", None)
    if factory is None:
        msg = "database session factory not configured"
        raise RuntimeError(msg)
    return factory


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory = _session_factory(request)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_auth_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> AuthService:
    return AuthService.from_session(session, get_settings(request))


def get_organization_service(
    session: AsyncSession = Depends(get_db_session),
) -> OrganizationService:
    return OrganizationService.from_session(session)


def get_invitation_service(
    session: AsyncSession = Depends(get_db_session),
) -> InvitationService:
    return InvitationService.from_session(session)


def get_game_service(
    session: AsyncSession = Depends(get_db_session),
) -> GameService:
    return GameService.from_session(session)


def get_game_version_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> GameVersionService:
    return GameVersionService.from_session(
        session,
        get_validation_service(request),
    )


def get_simulation_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> SimulationService:
    dispatcher = getattr(request.app.state, "simulation_dispatcher", None)
    queue = getattr(request.app.state, "simulation_queue", None)
    if queue is None and dispatcher is not None:
        queue = dispatcher.queue
    settings = getattr(request.app.state, "settings", None)
    return SimulationService.from_session(session, queue=queue, settings=settings)


def get_notification_service(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationService:
    return NotificationService.from_session(session)


def get_audit_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuditService:
    return AuditService.from_session(session)


def get_settings_service(
    session: AsyncSession = Depends(get_db_session),
) -> SettingsService:
    return SettingsService.from_session(session)


def get_dashboard_service(
    session: AsyncSession = Depends(get_db_session),
) -> DashboardService:
    return DashboardService.from_session(session)


def get_export_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> ExportService:
    dispatcher = getattr(request.app.state, "simulation_dispatcher", None)
    queue = getattr(request.app.state, "simulation_queue", None)
    if queue is None and dispatcher is not None:
        queue = dispatcher.queue
    return ExportService.from_session(session, queue=queue)


def get_mathematics_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> MathematicsService:
    dispatcher = getattr(request.app.state, "simulation_dispatcher", None)
    queue = getattr(request.app.state, "simulation_queue", None)
    if queue is None and dispatcher is not None:
        queue = dispatcher.queue
    return MathematicsService.from_session(session, queue=queue)


def get_ai_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> AIService:
    dispatcher = getattr(request.app.state, "simulation_dispatcher", None)
    queue = getattr(request.app.state, "simulation_queue", None)
    if queue is None and dispatcher is not None:
        queue = dispatcher.queue
    return AIService.from_session(session, queue=queue)


def get_collaboration_service(
    session: AsyncSession = Depends(get_db_session),
) -> CollaborationService:
    return CollaborationService.from_session(session)


def get_contact_service(
    session: AsyncSession = Depends(get_db_session),
) -> ContactService:
    from app.services.contact_service import ContactService

    return ContactService.from_session(session)


def get_demo_service(
    session: AsyncSession = Depends(get_db_session),
) -> DemoService:
    from app.services.demo_service import DemoService

    return DemoService.from_session(session)


def get_monitoring_service(
    request: Request,
) -> MonitoringService:
    return MonitoringService(session_factory=_session_factory(request))
