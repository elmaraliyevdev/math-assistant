"""Domain-level API exceptions."""

from __future__ import annotations

from typing import Any


class DomainError(Exception):
    """Base class for structured API domain errors."""

    code: str
    status_code: int

    def __init__(
        self,
        *,
        message: str,
        details: Any | None = None,
    ) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class GameNotFoundError(DomainError):
    code = "GAME_NOT_FOUND"
    status_code = 404

    def __init__(self, *, game_id: str) -> None:
        super().__init__(
            message=f"game not found: {game_id}",
            details={"gameId": game_id},
        )


class GameVersionNotFoundError(DomainError):
    code = "GAME_VERSION_NOT_FOUND"
    status_code = 404

    def __init__(self, *, game_id: str, version_id: str) -> None:
        super().__init__(
            message=f"game version not found: {version_id}",
            details={"gameId": game_id, "versionId": version_id},
        )


class DuplicateGameVersionError(DomainError):
    code = "DUPLICATE_GAME_VERSION"
    status_code = 409

    def __init__(
        self,
        *,
        content_hash: str,
        existing_version_id: str,
        existing_version_name: str,
        existing_game_id: str,
        existing_game_name: str,
        created_at: str,
    ) -> None:
        super().__init__(
            message="this version already exists in your organization",
            details={
                "contentHash": content_hash,
                "existingVersionId": existing_version_id,
                "existingVersionName": existing_version_name,
                "existingGameId": existing_game_id,
                "existingGameName": existing_game_name,
                "createdAt": created_at,
            },
        )


class ValidationFailedError(DomainError):
    code = "VALIDATION_FAILED"
    status_code = 422

    def __init__(
        self,
        *,
        content_hash: str,
        findings: list[dict[str, Any]],
    ) -> None:
        super().__init__(
            message="game validation failed",
            details={
                "contentHash": content_hash,
                "findings": findings,
            },
        )


class GameVersionReferenceNotFoundError(DomainError):
    code = "GAME_VERSION_NOT_FOUND"
    status_code = 404

    def __init__(self, *, game_version_id: str) -> None:
        super().__init__(
            message=f"game version not found: {game_version_id}",
            details={"gameVersionId": game_version_id},
        )


class SimulationNotFoundError(DomainError):
    code = "SIMULATION_NOT_FOUND"
    status_code = 404

    def __init__(self, *, simulation_id: str) -> None:
        super().__init__(
            message=f"simulation not found: {simulation_id}",
            details={"simulationId": simulation_id},
        )


class SimulationResultsNotReadyError(DomainError):
    code = "SIMULATION_RESULTS_NOT_READY"
    status_code = 409

    def __init__(self, *, simulation_id: str, status: str) -> None:
        super().__init__(
            message="simulation results are not available yet",
            details={"simulationId": simulation_id, "status": status},
        )


class SimulationCancelNotAllowedError(DomainError):
    code = "SIMULATION_CANCEL_NOT_ALLOWED"
    status_code = 409

    def __init__(self, *, simulation_id: str, status: str) -> None:
        super().__init__(
            message="simulation cannot be cancelled in its current state",
            details={"simulationId": simulation_id, "status": status},
        )


class SimulationSpinCountExceededError(DomainError):
    code = "SIMULATION_SPIN_COUNT_EXCEEDED"
    status_code = 400

    def __init__(
        self,
        *,
        spin_count: int,
        max_spin_count: int,
        deployment_mode: str,
    ) -> None:
        super().__init__(
            message=(
                f"spin count {spin_count:,} exceeds the {deployment_mode} "
                f"deployment limit of {max_spin_count:,}"
            ),
            details={
                "spinCount": spin_count,
                "maxSpinCount": max_spin_count,
                "deploymentMode": deployment_mode,
            },
        )


class ActiveSimulationLimitExceededError(DomainError):
    code = "ACTIVE_SIMULATION_LIMIT_EXCEEDED"
    status_code = 429

    def __init__(
        self,
        *,
        active_simulation_count: int,
        max_active_simulations: int,
        deployment_mode: str,
    ) -> None:
        super().__init__(
            message=(
                f"active simulation limit reached ({active_simulation_count}/"
                f"{max_active_simulations}) for {deployment_mode} deployment"
            ),
            details={
                "activeSimulationCount": active_simulation_count,
                "maxActiveSimulations": max_active_simulations,
                "deploymentMode": deployment_mode,
            },
        )


class InvalidComparisonError(DomainError):
    code = "INVALID_COMPARISON"
    status_code = 400

    def __init__(self, *, message: str, details: Any | None = None) -> None:
        super().__init__(message=message, details=details)


class SimulationNoteNotFoundError(DomainError):
    code = "SIMULATION_NOTE_NOT_FOUND"
    status_code = 404

    def __init__(self, *, simulation_id: str, note_id: str) -> None:
        super().__init__(
            message=f"simulation note not found: {note_id}",
            details={"simulationId": simulation_id, "noteId": note_id},
        )


class UnauthorizedError(DomainError):
    code = "UNAUTHORIZED"
    status_code = 401

    def __init__(self, *, message: str = "authentication required") -> None:
        super().__init__(message=message, details=None)


class InvalidCredentialsError(DomainError):
    code = "INVALID_CREDENTIALS"
    status_code = 401

    def __init__(self) -> None:
        super().__init__(message="invalid email or password", details=None)


class ForbiddenError(DomainError):
    code = "FORBIDDEN"
    status_code = 403

    def __init__(
        self,
        *,
        message: str = "forbidden",
        details: Any | None = None,
    ) -> None:
        super().__init__(message=message, details=details)


class OrganizationNotFoundError(DomainError):
    code = "ORGANIZATION_NOT_FOUND"
    status_code = 404

    def __init__(self, *, organization_id: str) -> None:
        super().__init__(
            message=f"organization not found: {organization_id}",
            details={"organizationId": organization_id},
        )


class OrganizationAccessDeniedError(DomainError):
    code = "ORGANIZATION_ACCESS_DENIED"
    status_code = 404

    def __init__(self, *, organization_id: str) -> None:
        super().__init__(
            message=f"organization not found: {organization_id}",
            details={"organizationId": organization_id},
        )


class DuplicateEmailError(DomainError):
    code = "DUPLICATE_EMAIL"
    status_code = 409

    def __init__(self, *, email: str) -> None:
        super().__init__(
            message="a user with this email already exists",
            details={"email": email},
        )


class DuplicateOrganizationSlugError(DomainError):
    code = "DUPLICATE_ORGANIZATION_SLUG"
    status_code = 409

    def __init__(self, *, slug: str) -> None:
        super().__init__(
            message="an organization with this slug already exists",
            details={"slug": slug},
        )


class UserNotFoundError(DomainError):
    code = "USER_NOT_FOUND"
    status_code = 404

    def __init__(self, *, user_id: str) -> None:
        super().__init__(
            message=f"user not found: {user_id}",
            details={"userId": user_id},
        )


class MemberNotFoundError(DomainError):
    code = "MEMBER_NOT_FOUND"
    status_code = 404

    def __init__(self, *, user_id: str, organization_id: str) -> None:
        super().__init__(
            message="organization member not found",
            details={"userId": user_id, "organizationId": organization_id},
        )


class InvalidTokenError(DomainError):
    code = "INVALID_TOKEN"
    status_code = 401

    def __init__(self, *, message: str = "invalid or expired token") -> None:
        super().__init__(message=message, details=None)


class InactiveUserError(DomainError):
    code = "INACTIVE_USER"
    status_code = 403

    def __init__(self) -> None:
        super().__init__(message="user account is inactive", details=None)


class NotificationNotFoundError(DomainError):
    code = "NOTIFICATION_NOT_FOUND"
    status_code = 404

    def __init__(self, *, notification_id: str) -> None:
        super().__init__(
            message=f"notification not found: {notification_id}",
            details={"notificationId": notification_id},
        )


class RateLimitExceededError(DomainError):
    code = "RATE_LIMIT_EXCEEDED"
    status_code = 429

    def __init__(self) -> None:
        super().__init__(
            message="too many requests; try again later",
            details=None,
        )


class AccountLockedError(DomainError):
    code = "ACCOUNT_LOCKED"
    status_code = 429

    def __init__(self, *, retry_after_seconds: int) -> None:
        super().__init__(
            message="too many failed login attempts; account temporarily locked",
            details={"retryAfterSeconds": retry_after_seconds},
        )


class ReviewDecisionRequiredError(DomainError):
    code = "REVIEW_DECISION_REQUIRED"
    status_code = 422

    def __init__(self, *, status: str) -> None:
        super().__init__(
            message="a decision reason is required for this review outcome",
            details={"status": status},
        )


class InvalidWorkflowTransitionError(DomainError):
    code = "INVALID_WORKFLOW_TRANSITION"
    status_code = 422

    def __init__(self, *, current: str, target: str) -> None:
        super().__init__(
            message=f"invalid workflow transition from {current} to {target}",
            details={"current": current, "target": target},
        )


class DuplicateApprovalError(DomainError):
    code = "DUPLICATE_APPROVAL"
    status_code = 409

    def __init__(self, *, simulation_id: str, stage: str) -> None:
        super().__init__(
            message=f"approval already recorded for stage {stage}",
            details={"simulationId": simulation_id, "stage": stage},
        )


class InvitationNotFoundError(DomainError):
    code = "INVITATION_NOT_FOUND"
    status_code = 404

    def __init__(self, *, invitation_id: str) -> None:
        super().__init__(
            message=f"invitation not found: {invitation_id}",
            details={"invitationId": invitation_id},
        )


class InvitationExpiredError(DomainError):
    code = "INVITATION_EXPIRED"
    status_code = 410

    def __init__(self, *, invitation_id: str) -> None:
        super().__init__(
            message="invitation has expired",
            details={"invitationId": invitation_id},
        )


class InvitationEmailMismatchError(DomainError):
    code = "INVITATION_EMAIL_MISMATCH"
    status_code = 403

    def __init__(self) -> None:
        super().__init__(
            message="invitation email does not match your account",
            details=None,
        )


class DuplicateInvitationError(DomainError):
    code = "DUPLICATE_INVITATION"
    status_code = 409

    def __init__(self, *, email: str, organization_id: str) -> None:
        super().__init__(
            message="a pending invitation already exists for this email",
            details={"email": email, "organizationId": organization_id},
        )


class AlreadyOrganizationMemberError(DomainError):
    code = "ALREADY_ORGANIZATION_MEMBER"
    status_code = 409

    def __init__(self, *, email: str, organization_id: str) -> None:
        super().__init__(
            message="user is already a member of this organization",
            details={"email": email, "organizationId": organization_id},
        )
