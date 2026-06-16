"""Monitoring service async tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.distributed.monitoring_service import MonitoringService


@pytest.mark.asyncio
async def test_queue_summary_counts() -> None:
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session.scalar = AsyncMock(side_effect=[2, 1, 5, 0])
    session.execute = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=[])))

    factory = MagicMock(return_value=session)
    monitoring = MonitoringService(factory)

    with patch("app.distributed.celery_app.celery_app") as celery:
        celery.control.inspect.return_value.reserved.return_value = {}
        summary = await monitoring.queue_summary()
        assert summary.pending_tasks == 2
        assert summary.running_tasks == 1
        assert summary.completed_tasks == 5
