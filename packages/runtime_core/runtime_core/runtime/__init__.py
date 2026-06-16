"""Runtime Core — deterministic RNG, events, session, stack, and transitions."""

from runtime_core.runtime.events import (
    EVENT_VERSION,
    EventContext,
    EventCorrelation,
    EventLogger,
    EventLogMode,
    EventType,
    RuntimeEvent,
    should_emit,
    validate_payload,
)
from runtime_core.runtime.exceptions import RNGError, RuntimeError
from runtime_core.runtime.frames import FrameContext, HeldSymbol, new_frame_context
from runtime_core.runtime.lifecycle import LifecycleOutcome, apply_transition
from runtime_core.runtime.rng import (
    RNG,
    ChainScope,
    FrameStream,
    RNGAlgorithm,
    RNGService,
    RNGServiceConfig,
    SeedDerivationPolicy,
    default_rng_service_config,
)
from runtime_core.runtime.session import (
    BetContext,
    EffectiveLimits,
    ExposureState,
    NewSessionParams,
    SessionContext,
    new_session_context,
    new_session_params_from_request,
)
from runtime_core.runtime.spin_chain import (
    AccumulatorDelta,
    ChainFault,
    LimitHit,
    SimulationProfile,
    SpinChainRequest,
    SpinChainResult,
)
from runtime_core.runtime.stack import ExecutionStack, StateMachineFrame, build_frame
from runtime_core.runtime.transitions import (
    TransitionResolution,
    TransitionResolveResult,
    resolve_transition,
)
from runtime_core.runtime.version import ENGINE_VERSION

__all__ = [
    "ENGINE_VERSION",
    "EVENT_VERSION",
    "AccumulatorDelta",
    "BetContext",
    "ChainFault",
    "ChainScope",
    "EffectiveLimits",
    "EventContext",
    "EventCorrelation",
    "EventLogMode",
    "EventLogger",
    "EventType",
    "ExecutionStack",
    "ExposureState",
    "FrameContext",
    "FrameStream",
    "HeldSymbol",
    "LifecycleOutcome",
    "LimitHit",
    "NewSessionParams",
    "RNG",
    "RNGAlgorithm",
    "RNGError",
    "RNGService",
    "RNGServiceConfig",
    "RuntimeError",
    "RuntimeEvent",
    "SeedDerivationPolicy",
    "SessionContext",
    "SimulationProfile",
    "SpinChainRequest",
    "SpinChainResult",
    "StateMachineFrame",
    "TransitionResolution",
    "TransitionResolveResult",
    "apply_transition",
    "build_frame",
    "default_rng_service_config",
    "new_frame_context",
    "new_session_context",
    "new_session_params_from_request",
    "resolve_transition",
    "should_emit",
    "validate_payload",
]
