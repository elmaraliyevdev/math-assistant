"""Contact form service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.contact_submission import ContactSubmission
from app.db.repositories.contact_submission_repository import ContactSubmissionRepository
from app.schemas.contact import (
    ContactSubmissionListItem,
    ContactSubmissionListResponse,
    ContactSubmissionRequest,
    ContactSubmissionResponse,
)


@dataclass(frozen=True, slots=True)
class ContactService:
    submissions: ContactSubmissionRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> ContactService:
        return cls(submissions=ContactSubmissionRepository(session))

    async def submit(self, body: ContactSubmissionRequest) -> ContactSubmissionResponse:
        submission = ContactSubmission(
            type=body.type.value,
            name=body.name.strip(),
            email=body.email.strip().lower(),
            company=body.company.strip() if body.company else None,
            message=body.message.strip(),
            status="new",
        )
        created = await self.submissions.add(submission)
        return ContactSubmissionResponse(id=created.id)

    async def list_submissions(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> ContactSubmissionListResponse:
        items = await self.submissions.list_recent(limit=limit, offset=offset)
        total = await self.submissions.count_all()
        return ContactSubmissionListResponse(
            items=[
                ContactSubmissionListItem(
                    id=item.id,
                    type=item.type,
                    name=item.name,
                    email=item.email,
                    company=item.company,
                    message=item.message,
                    status=item.status,
                    created_at=item.created_at,
                )
                for item in items
            ],
            total=total,
        )
