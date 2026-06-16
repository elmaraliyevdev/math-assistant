"""Session context construction for Runtime Core R1."""

from __future__ import annotations

from dataclasses import dataclass, field

from runtime_core.domain.game_version import GameVersion
from runtime_core.runtime.events import (
    EventContext,
    EventCorrelation,
    EventLogger,
    EventLogMode,
)
from runtime_core.runtime.rng import (
    ChainScope,
    RNGService,
    RNGServiceConfig,
    default_rng_service_config,
)
from runtime_core.runtime.session.models import (
    BetContext,
    EffectiveLimits,
    ExposureState,
)
from runtime_core.runtime.session.resolution import resolved_session_fields
from runtime_core.runtime.spin_chain import SpinChainRequest


@dataclass
class SessionContext:
    """Mutable per-chain runtime state (Runtime Core §7.1)."""

    game_version_content_hash: str
    engine_version: str
    spin_chain_index: int
    bet: BetContext
    total_bet_minor_units: int
    inheritance_policy: str
    rng: RNGService
    chain_rng: ChainScope
    events: EventLogger
    limits: EffectiveLimits
    exposure: ExposureState
    total_win_minor_units: int = 0
    total_uncapped_win_minor_units: int = 0
    total_truncated_minor_units: int = 0
    exposure_cap_applied: bool = False


@dataclass(frozen=True, slots=True)
class NewSessionParams:
    game: GameVersion
    engine_version: str
    master_seed: bytes
    spin_chain_index: int
    shard_index: int
    simulation_run_id: str
    bet_minor_units: int = 0
    event_log_mode: EventLogMode = EventLogMode.NONE
    rng_config: RNGServiceConfig = field(default_factory=default_rng_service_config)


def new_session_params_from_request(req: SpinChainRequest) -> NewSessionParams:
    return NewSessionParams(
        game=req.game,
        engine_version=req.resolved_engine_version(),
        master_seed=req.master_seed,
        spin_chain_index=req.spin_chain_index,
        shard_index=req.shard_index,
        simulation_run_id=req.simulation_run_id,
        bet_minor_units=req.bet_minor_units,
        event_log_mode=req.event_log_mode,
    )


def new_session_context(params: NewSessionParams) -> SessionContext:
    if params.engine_version == "":
        msg = "engineVersion is required"
        raise ValueError(msg)
    if not params.master_seed:
        msg = "masterSeed is required"
        raise ValueError(msg)
    if params.simulation_run_id == "":
        msg = "simulationRunID is required"
        raise ValueError(msg)

    game_hash, bet, total_bet, policy, limits, exposure = resolved_session_fields(
        params.game,
        params.bet_minor_units,
    )
    rng_svc = RNGService(params.rng_config)
    chain_scope = rng_svc.new_chain_scope(
        params.master_seed,
        params.shard_index,
        params.simulation_run_id,
        params.spin_chain_index,
    )
    correlation = EventCorrelation(
        simulation_run_id=params.simulation_run_id,
        spin_chain_index=params.spin_chain_index,
        game_version_content_hash=game_hash,
        engine_version=params.engine_version,
    )
    logger = EventLogger(
        mode=params.event_log_mode,
        correlation=correlation,
        context=EventContext(
            stack_depth=0,
            machine_id="",
            state_id="",
            frame_id="",
        ),
    )
    return SessionContext(
        game_version_content_hash=game_hash,
        engine_version=params.engine_version,
        spin_chain_index=params.spin_chain_index,
        bet=bet,
        total_bet_minor_units=total_bet,
        inheritance_policy=policy,
        rng=rng_svc,
        chain_rng=chain_scope,
        events=logger,
        limits=limits,
        exposure=exposure,
    )
