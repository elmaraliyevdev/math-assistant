package validators_test

import (
	"testing"

	"math-assistant/runtime-core/internal/domain"
	"math-assistant/runtime-core/internal/validation/validators"
)

func baseGame() *domain.GameVersion {
	paysFalse := false
	return &domain.GameVersion{
		Session: domain.SessionConfig{RootMachineID: "main", MaxStackDepth: 4},
		StateMachines: map[string]domain.StateMachine{
			"main": {
				ID: "main", InitialStateID: "BASE",
				States: map[string]domain.State{
					"BASE": {
						ID: "BASE", PluginRefID: "base_main", StateType: "atomic_spin", RtpCategory: "BASE",
						Transitions: []domain.Transition{
							{ID: "t1", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 1000, Effect: "stay", TargetStateID: "BASE"},
						},
					},
				},
			},
		},
		Symbols: map[string]domain.Symbol{"SCATTER": {ID: "SCATTER", Type: "scatter", Pays: &paysFalse}},
	}
}

func TestValidateStateMachinesMissingInitial(t *testing.T) {
	game := baseGame()
	game.StateMachines["main"] = domain.StateMachine{ID: "main", InitialStateID: "MISSING", States: map[string]domain.State{}}
	findings := validators.ValidateStateMachines(game)
	if len(findings) == 0 {
		t.Fatal("expected findings")
	}
}

func TestValidateReachabilityDeadEnd(t *testing.T) {
	game := baseGame()
	st := game.StateMachines["main"].States["BASE"]
	st.Terminal = false
	st.Transitions = nil
	game.StateMachines["main"].States["BASE"] = st
	findings := validators.ValidateReachability(game)
	found := false
	for _, f := range findings {
		if f.Code == "GV-006" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-006, got %+v", findings)
	}
}

func TestValidateSpawnNoPop(t *testing.T) {
	game := baseGame()
	game.StateMachines["child"] = domain.StateMachine{
		ID: "child", InitialStateID: "C",
		States: map[string]domain.State{"C": {ID: "C", Transitions: nil, Terminal: true}},
	}
	st := game.StateMachines["main"].States["BASE"]
	st.Transitions = append(st.Transitions, domain.Transition{
		ID: "spawn", Trigger: "HOLD_AND_WIN", Effect: "spawn", TargetMachineID: "child",
	})
	game.StateMachines["main"].States["BASE"] = st
	findings := validators.ValidateReachability(game)
	found := false
	for _, f := range findings {
		if f.Code == "GV-008" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-008, got %+v", findings)
	}
}

func TestValidateStackDepth(t *testing.T) {
	game := baseGame()
	game.StateMachines["child"] = domain.StateMachine{ID: "child", InitialStateID: "C", States: map[string]domain.State{"C": {ID: "C"}}}
	st := game.StateMachines["main"].States["BASE"]
	st.Transitions = append(st.Transitions, domain.Transition{ID: "s", Trigger: "X", Effect: "spawn", TargetMachineID: "child"})
	game.StateMachines["main"].States["BASE"] = st
	game.Session.MaxStackDepth = 1
	findings := validators.ValidateStackDepth(game)
	if len(findings) != 1 || findings[0].Code != "GV-012" {
		t.Fatalf("unexpected findings: %+v", findings)
	}
}

func TestValidateProgressionMultiStepLoop(t *testing.T) {
	game := baseGame()
	game.StateMachines["main"].States["LOOP"] = domain.State{
		ID: "LOOP", StateType: "multi_step",
		Transitions: []domain.Transition{{ID: "l", Trigger: "STEP", Effect: "stay", TargetStateID: "LOOP"}},
	}
	findings := validators.ValidateProgression(game)
	found := false
	for _, f := range findings {
		if f.Code == "GV-011" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-011, got %+v", findings)
	}
}

func TestValidateTransitionsInvalidPop(t *testing.T) {
	game := baseGame()
	st := game.StateMachines["main"].States["BASE"]
	st.Transitions = []domain.Transition{{ID: "p", Trigger: "FEATURE_COMPLETE", Effect: "pop", TargetStateID: "BASE"}}
	game.StateMachines["main"].States["BASE"] = st
	findings := validators.ValidateTransitions(game, nil)
	found := false
	for _, f := range findings {
		if f.Code == "GV-010" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-010, got %+v", findings)
	}
}

func TestLoadPriorityTierRegistry(t *testing.T) {
	root := schemaRoot(t)
	reg, err := validators.LoadPriorityTierRegistry(root)
	if err != nil {
		t.Fatal(err)
	}
	if _, ok := reg.Resolve("FEATURE_ENTRY_SPAWN"); !ok {
		t.Fatal("expected tier")
	}
	if _, ok := reg.Resolve("SPIN_IDLE"); !ok {
		t.Fatal("expected alias")
	}
}

func TestLoadRtpCategoryRegistry(t *testing.T) {
	root := schemaRoot(t)
	reg, err := validators.LoadRtpCategoryRegistry(root)
	if err != nil {
		t.Fatal(err)
	}
	if !reg.IsKnown("BASE") {
		t.Fatal("expected BASE category")
	}
}

func TestValidateTransitionConflicts(t *testing.T) {
	game := baseGame()
	game.Precedence = domain.Precedence{TriggerOrder: []string{"SPIN_COMPLETE"}}
	st := game.StateMachines["main"].States["BASE"]
	st.Transitions = []domain.Transition{
		{ID: "a", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 1000, Effect: "stay", TargetStateID: "BASE"},
		{ID: "b", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 1000, Effect: "goto", TargetStateID: "BASE"},
	}
	game.StateMachines["main"].States["BASE"] = st
	root := schemaRoot(t)
	tiers, err := validators.LoadPriorityTierRegistry(root)
	if err != nil {
		t.Fatal(err)
	}
	findings := validators.ValidateTransitions(game, tiers)
	if len(findings) == 0 {
		t.Fatal("expected conflict findings")
	}
}

func TestValidatePluginReferences(t *testing.T) {
	game := baseGame()
	game.ReelSets = map[string]domain.ReelSet{
		"base_game": {ID: "base_game", Reels: []domain.ReelStrip{{ReelIndex: 0, Symbols: []string{"SCATTER"}}}},
	}
	game.GameConfig = domain.GameConfig{Grid: domain.GridSpec{Reels: 5, Rows: 3}, DefaultReelSetID: "base_game"}
	st := game.StateMachines["main"].States["BASE"]
	st.PluginConfig = map[string]any{"reelSetId": "base_game"}
	game.StateMachines["main"].States["BASE"] = st
	findings := validators.ValidatePluginReferences(game)
	if len(findings) != 1 || findings[0].Code != "GV-022" {
		t.Fatalf("expected reel mismatch GV-022, got %+v", findings)
	}
}

func TestRtpRegistryCloneMerge(t *testing.T) {
	root := schemaRoot(t)
	reg, err := validators.LoadRtpCategoryRegistry(root)
	if err != nil {
		t.Fatal(err)
	}
	clone := reg.Clone()
	clone.MergeDocument(&domain.GameVersion{
		RtpCategoryRegistry: &domain.RtpCategoryRegistry{
			Categories: map[string]domain.RtpCategoryDef{"CUSTOM_CAT": {Label: "X", DecompositionGroup: "feature"}},
		},
	})
	if !clone.IsKnown("CUSTOM_CAT") {
		t.Fatal("expected merged category")
	}
}

func TestValidateTransitionTargetMissing(t *testing.T) {
	game := baseGame()
	st := game.StateMachines["main"].States["BASE"]
	st.Transitions = []domain.Transition{{ID: "x", Trigger: "X", Effect: "goto", TargetStateID: "NOPE"}}
	game.StateMachines["main"].States["BASE"] = st
	findings := validators.ValidateTransitions(game, nil)
	found := false
	for _, f := range findings {
		if f.Code == "GV-003" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-003, got %+v", findings)
	}
}

func TestValidateOrphanState(t *testing.T) {
	game := baseGame()
	game.StateMachines["main"].States["ORPHAN"] = domain.State{ID: "ORPHAN", Transitions: nil, Terminal: true}
	findings := validators.ValidateReachability(game)
	found := false
	for _, f := range findings {
		if f.Code == "GV-005" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-005, got %+v", findings)
	}
}

func TestValidateDuplicateTransition(t *testing.T) {
	game := baseGame()
	st := game.StateMachines["main"].States["BASE"]
	st.Transitions = append(st.Transitions, st.Transitions[0])
	game.StateMachines["main"].States["BASE"] = st
	findings := validators.ValidateTransitions(game, nil)
	found := false
	for _, f := range findings {
		if f.Code == "GV-013" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-013, got %+v", findings)
	}
}

func TestValidateSpawnTargetMissing(t *testing.T) {
	game := baseGame()
	st := game.StateMachines["main"].States["BASE"]
	st.Transitions = []domain.Transition{{ID: "s", Trigger: "X", Effect: "spawn", TargetMachineID: "missing"}}
	game.StateMachines["main"].States["BASE"] = st
	findings := validators.ValidateTransitions(game, nil)
	found := false
	for _, f := range findings {
		if f.Code == "GV-004" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-004, got %+v", findings)
	}
}

func TestValidateRootMachineMissing(t *testing.T) {
	game := baseGame()
	game.Session.RootMachineID = "nope"
	findings := validators.ValidateStateMachines(game)
	found := false
	for _, f := range findings {
		if f.Code == "GV-002" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-002, got %+v", findings)
	}
}

func TestValidatePriorityTierMissingWarning(t *testing.T) {
	game := baseGame()
	st := game.StateMachines["main"].States["BASE"]
	st.Transitions = []domain.Transition{{ID: "x", Trigger: "X", Effect: "stay", TargetStateID: "BASE"}}
	game.StateMachines["main"].States["BASE"] = st
	root := schemaRoot(t)
	tiers, err := validators.LoadPriorityTierRegistry(root)
	if err != nil {
		t.Fatal(err)
	}
	findings := validators.ValidateTransitions(game, tiers)
	found := false
	for _, f := range findings {
		if f.Code == "GV-028" {
			found = true
		}
	}
	if !found {
		t.Fatalf("expected GV-028, got %+v", findings)
	}
}

func schemaRoot(t *testing.T) string {
	t.Helper()
	// relative from validators test cwd
	candidates := []string{
		"../../../game-schema",
		"../../../../game-schema",
	}
	for _, c := range candidates {
		reg, err := validators.LoadPriorityTierRegistry(c)
		if err == nil {
			_ = reg
			return c
		}
	}
	t.Fatal("schema root not found")
	return ""
}
