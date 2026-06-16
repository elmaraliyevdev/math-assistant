"""Direct tests for validation issue constructors (coverage)."""

from runtime_core.validation import issues


def test_issue_constructors_cover_registry_codes() -> None:
    samples = [
        issues.schema_enum("$.x", "a,b"),
        issues.schema_pattern("$.id"),
        issues.schema_range("$.n", "too big"),
        issues.schema_additional_property("$.root", "extra"),
        issues.graph_spawn_target_missing("m", "s", "t", "child"),
        issues.graph_dead_end("m", "s"),
        issues.graph_spawn_no_pop("child"),
        issues.graph_infinite_loop("m", "s"),
        issues.graph_stack_depth_exceeded(5, 3),
        issues.graph_duplicate_transition_id("m", "s", "t"),
        issues.graph_duplicate_state_id("m", "s"),
        issues.graph_duplicate_machine_id("m"),
        issues.graph_priority_conflict("m", "s", "TRIG"),
        issues.graph_ambiguous_transitions("m", "s", "TRIG"),
        issues.graph_plugin_capability_missing("ref", "cap"),
        issues.graph_plugin_symbol_missing("path", "SYM"),
        issues.graph_plugin_reel_mismatch("path", 5, 3),
        issues.graph_exposure_cap_exceeded(100, 50),
        issues.graph_rtp_category_unknown("path", "X"),
        issues.graph_priority_tier_unknown("path", "T"),
        issues.graph_priority_tier_missing("path"),
        issues.graph_priority_out_of_range("path", "T"),
        issues.graph_invalid_pop("path"),
        issues.graph_multiple_initial_states("m"),
        issues.graph_plugin_config_invalid("path", "detail"),
        issues.graph_exposure_multiplier_invalid(),
        issues.graph_exposure_cap_invalid(),
        issues.graph_exposure_scope_invalid("bad"),
        issues.graph_limits_frames_exceed_stack(10, 4),
        issues.graph_limits_respins_exceeded("path", 5, 3),
    ]
    assert all(sample.code.startswith(("SV-", "GV-")) for sample in samples)
