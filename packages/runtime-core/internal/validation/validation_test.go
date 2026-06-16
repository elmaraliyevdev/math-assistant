package validation_test

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"math-assistant/runtime-core/internal/domain"
	"math-assistant/runtime-core/internal/validation"
)

func testEngine(t *testing.T) validation.Engine {
	t.Helper()
	paths, err := validation.DefaultSchemaPaths()
	if err != nil {
		t.Fatalf("schema paths: %v", err)
	}
	engine, err := validation.NewEngine(validation.Config{SchemaPaths: paths})
	if err != nil {
		t.Fatalf("new engine: %v", err)
	}
	return engine
}

func loadFixtureJSON(t *testing.T, paths ...string) []byte {
	t.Helper()
	for _, p := range paths {
		data, err := os.ReadFile(p)
		if err == nil {
			return data
		}
	}
	t.Fatalf("fixture not found in %v", paths)
	return nil
}

func unmarshalGame(t *testing.T, data []byte) *domain.GameVersion {
	t.Helper()
	var game domain.GameVersion
	if err := json.Unmarshal(data, &game); err != nil {
		t.Fatalf("unmarshal game: %v", err)
	}
	return &game
}

func hasCode(report *validation.ValidationReport, code string) bool {
	for _, e := range report.Errors {
		if e.Code == code {
			return true
		}
	}
	for _, w := range report.Warnings {
		if w.Code == code {
			return true
		}
	}
	return false
}

func repoRoot(t *testing.T) string {
	t.Helper()
	wd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	dir := wd
	for {
		if _, err := os.Stat(filepath.Join(dir, "packages", "game-schema")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			t.Fatal("repo root not found")
		}
		dir = parent
	}
}

func goldenPath(t *testing.T, fixtureDir string) string {
	return filepath.Join(repoRoot(t), "tests", "golden", fixtureDir, "game.canonical.json")
}

func testdataPath(name string) string {
	return filepath.Join("testdata", name)
}

func buildValidBaseGame() *domain.GameVersion {
	paysFalse := false
	scatterPays := true
	highestOnly := true
	return &domain.GameVersion{
		SchemaVersion: "1.0.0",
		GameVersion: domain.GameVersionMeta{
			ID:            "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
			ProjectID:     "f0e1d2c3-b4a5-9678-9012-3456789abcde",
			VersionNumber: 1,
			Status:        "draft",
			CreatedAt:     "2026-06-14T10:00:00Z",
			Source:        "dsl-compiler",
			Label:         "Valid Base Game",
		},
		Metadata: domain.Metadata{
			Title: "Base 5x3",
			RtpTarget: &domain.RtpTarget{Percent: 96.0, Tolerance: 0.1},
		},
		GameConfig: domain.GameConfig{
			Grid:             domain.GridSpec{Reels: 5, Rows: 3, IndexOrigin: "top-left"},
			DefaultReelSetID: "base_game",
		},
		Symbols: map[string]domain.Symbol{
			"H1":      {ID: "H1", Type: "regular", DisplayName: "High 1"},
			"L1":      {ID: "L1", Type: "regular", DisplayName: "Low 1"},
			"SCATTER": {ID: "SCATTER", Type: "scatter", Pays: &paysFalse},
		},
		ReelSets: map[string]domain.ReelSet{
			"base_game": {
				ID: "base_game",
				Reels: []domain.ReelStrip{
					{ReelIndex: 0, Symbols: []string{"L1", "H1", "SCATTER", "L1", "H1"}},
					{ReelIndex: 1, Symbols: []string{"L1", "H1", "SCATTER", "L1", "H1"}},
					{ReelIndex: 2, Symbols: []string{"L1", "H1", "SCATTER", "L1", "H1"}},
					{ReelIndex: 3, Symbols: []string{"L1", "H1", "SCATTER", "L1", "H1"}},
					{ReelIndex: 4, Symbols: []string{"L1", "H1", "SCATTER", "L1", "H1"}},
				},
			},
		},
		Paytable: domain.Paytable{
			Lines: []domain.PaylineDefinition{{Index: 1, Path: []int{1, 1, 1, 1, 1}}},
			Pays:  []domain.PaytableEntry{{SymbolID: "H1", Count: 5, Multiplier: 100}},
		},
		WinModel: domain.WinModel{Type: "lines", Direction: "left-to-right", ScatterPaysOnReels: &scatterPays, HighestWinOnlyPerLine: &highestOnly},
		BetModel: domain.BetModel{Type: "lines", LineCount: 20, CoinValueScale: 100, DefaultCoinValue: 1, MinCoinValue: 1, MaxCoinValue: 1},
		Plugins: map[string]domain.PluginRef{
			"base_main": {
				RefID: "base_main", PluginID: "core.base-game", PluginVersion: "1.0.0",
				ConfigSchemaVersion: "1.0.0", Capabilities: []string{"spin.grid", "win.lines", "win.scatter"},
			},
		},
		StateMachines: map[string]domain.StateMachine{
			"main": {
				ID: "main", InitialStateID: "BASE",
				States: map[string]domain.State{
					"BASE": {
						ID: "BASE", PluginRefID: "base_main", StateType: "atomic_spin",
						RtpCategory: "BASE",
						PluginConfig: map[string]any{
							"reelSetId": "base_game",
							"scatterTriggers": []any{
								map[string]any{"symbolId": "SCATTER", "minCount": 3, "emitTrigger": "FREE_SPINS"},
							},
						},
						Transitions: []domain.Transition{
							{ID: "t_spin", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 1000, Effect: "stay", TargetStateID: "BASE"},
						},
					},
				},
			},
		},
		Session: domain.SessionConfig{
			RootMachineID: "main", MaxStackDepth: 4, SpinLoopMode: "single_chain",
			ContextInheritancePolicy: "mvp-v1",
			RuntimeLimits:            &domain.RuntimeLimits{MaxStepsPerSpinChain: 500},
		},
		Exposure: domain.Exposure{
			MaxWinMinorUnits: 500000, MaxWinMultiplier: 5000, CapScope: "session_spin_chain",
			EnforceCap: true, ValidationMode: "strict",
		},
		Determinism: domain.Determinism{
			RngAlgorithm: "PCG64", RngAlgorithmVersion: "1.0", SeedDerivationPolicy: "v1-hash-shard",
			MoneyRepresentation: "fixed_minor_units", MoneyScale: 10000,
		},
		Precedence:  domain.Precedence{TriggerOrder: []string{"SPIN_COMPLETE"}},
		Extensions:  map[string]any{},
	}
}

func buildNestedFSHAW() *domain.GameVersion {
	base := buildValidBaseGame()
	base.GameVersion.Label = "Golden Fixture 4 — Nested FS + H&W"
	base.Metadata.Title = "Example Nested Slot"
	base.Symbols["H2"] = domain.Symbol{ID: "H2", Type: "regular", DisplayName: "High 2"}
	base.Symbols["L2"] = domain.Symbol{ID: "L2", Type: "regular", DisplayName: "Low 2"}
	base.Symbols["WILD"] = domain.Symbol{ID: "WILD", Type: "wild", Substitutes: []string{"H1", "H2", "L1", "L2"}}
	base.Symbols["BONUS"] = domain.Symbol{ID: "BONUS", Type: "bonus", Pays: boolPtr(false)}
	base.ReelSets["free_spins"] = domain.ReelSet{
		ID: "free_spins",
		Reels: []domain.ReelStrip{
			{ReelIndex: 0, Symbols: []string{"L1", "H1", "SCATTER", "H1", "BONUS"}},
			{ReelIndex: 1, Symbols: []string{"L1", "H1", "SCATTER", "H1", "BONUS"}},
			{ReelIndex: 2, Symbols: []string{"L1", "H1", "SCATTER", "H1", "BONUS"}},
			{ReelIndex: 3, Symbols: []string{"L1", "H1", "SCATTER", "H1", "BONUS"}},
			{ReelIndex: 4, Symbols: []string{"L1", "H1", "SCATTER", "H1", "BONUS"}},
		},
	}
	base.ReelSets["hold_and_win"] = domain.ReelSet{
		ID: "hold_and_win",
		Reels: []domain.ReelStrip{
			{ReelIndex: 0, Symbols: []string{"BONUS", "L1", "BONUS", "L2", "BONUS"}},
			{ReelIndex: 1, Symbols: []string{"L2", "BONUS", "L1", "BONUS", "L2"}},
			{ReelIndex: 2, Symbols: []string{"BONUS", "BONUS", "L1", "L2", "BONUS"}},
			{ReelIndex: 3, Symbols: []string{"L1", "BONUS", "L2", "BONUS", "BONUS"}},
			{ReelIndex: 4, Symbols: []string{"BONUS", "L1", "BONUS", "BONUS", "L2"}},
		},
	}
	base.Plugins["fs_main"] = domain.PluginRef{
		RefID: "fs_main", PluginID: "core.free-spins", PluginVersion: "1.0.0",
		ConfigSchemaVersion: "1.0.0", Capabilities: []string{"spin.grid", "win.lines", "win.scatter", "feature.retrigger", "feature.nested"},
	}
	base.Plugins["haw_main"] = domain.PluginRef{
		RefID: "haw_main", PluginID: "core.hold-and-win", PluginVersion: "1.0.0",
		ConfigSchemaVersion: "1.0.0", Capabilities: []string{"spin.grid", "state.multistep", "jackpot.local"},
	}
	base.Plugins["mult_fs"] = domain.PluginRef{
		RefID: "mult_fs", PluginID: "core.multiplier", PluginVersion: "1.0.0",
		ConfigSchemaVersion: "1.0.0", Capabilities: []string{"multiplier.apply"},
	}
	base.Plugins["mult_haw"] = domain.PluginRef{
		RefID: "mult_haw", PluginID: "core.multiplier", PluginVersion: "1.0.0",
		ConfigSchemaVersion: "1.0.0", Capabilities: []string{"multiplier.apply"},
	}
	main := base.StateMachines["main"]
	main.States["BASE"] = domain.State{
		ID: "BASE", PluginRefID: "base_main", StateType: "atomic_spin", RtpCategory: "BASE",
		PluginConfig: map[string]any{
			"reelSetId": "base_game",
			"scatterTriggers": []any{map[string]any{"symbolId": "SCATTER", "minCount": 3, "emitTrigger": "FREE_SPINS"}},
			"bonusTriggers":   []any{map[string]any{"symbolId": "BONUS", "minCount": 6, "emitTrigger": "HOLD_AND_WIN"}},
		},
		Transitions: []domain.Transition{
			{ID: "t_base_to_fs", Trigger: "FREE_SPINS", PriorityTier: "FEATURE_ENTRY", Priority: 200, Effect: "goto", TargetStateID: "FREE_SPINS"},
			{ID: "t_base_to_haw", Trigger: "HOLD_AND_WIN", PriorityTier: "FEATURE_ENTRY_SPAWN", Priority: 100, Effect: "spawn", TargetMachineID: "hold_and_win"},
			{ID: "t_base_spin", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 1000, Effect: "stay", TargetStateID: "BASE"},
		},
	}
	main.States["FREE_SPINS"] = domain.State{
		ID: "FREE_SPINS", PluginRefID: "fs_main", StateType: "atomic_spin", RtpCategory: "FREE_SPINS",
		PluginConfig: map[string]any{
			"reelSetId": "free_spins",
			"awardsByScatterCount": map[string]any{"3": 10, "4": 15, "5": 20},
			"retrigger": map[string]any{
				"enabled": true, "awardsByScatterCount": map[string]any{"3": 5, "4": 10, "5": 15},
			},
			"multiplierRefId": "mult_fs",
			"bonusTriggers":   []any{map[string]any{"symbolId": "BONUS", "minCount": 6, "emitTrigger": "HOLD_AND_WIN"}},
		},
		Transitions: []domain.Transition{
			{ID: "t_fs_to_haw", Trigger: "HOLD_AND_WIN", PriorityTier: "FEATURE_ENTRY_SPAWN", Priority: 100, Effect: "spawn", TargetMachineID: "hold_and_win"},
			{ID: "t_fs_complete", Trigger: "FEATURE_COMPLETE", PriorityTier: "FEATURE_EXIT", Priority: 900, Effect: "goto", TargetStateID: "BASE"},
		},
	}
	base.StateMachines["hold_and_win"] = domain.StateMachine{
		ID: "hold_and_win", InitialStateID: "HAW_RESPINS",
		States: map[string]domain.State{
			"HAW_RESPINS": {
				ID: "HAW_RESPINS", PluginRefID: "haw_main", StateType: "multi_step", RtpCategory: "HOLD_AND_WIN",
				PluginConfig: map[string]any{
					"reelSetId": "hold_and_win", "triggerSymbolId": "BONUS", "triggerSymbolCount": 6,
					"initialRespins": 3, "gridCapacity": 15,
					"jackpotTiers": map[string]any{"mini": 20, "major": 100, "grand": 500},
					"multiplierRefId": "mult_haw",
				},
				Progression: &domain.Progression{
					CounterField: "respinsRemaining", DecrementsOn: "each_step", MinValue: intPtr(0),
					TerminatesWhen: "respinsRemaining == 0 OR gridFull == true",
				},
				Transitions: []domain.Transition{
					{ID: "t_haw_pop", Trigger: "FEATURE_COMPLETE", PriorityTier: "FEATURE_EXIT", Priority: 900, Effect: "pop"},
				},
			},
		},
	}
	base.Session.MaxStackDepth = 4
	base.Session.RuntimeLimits = &domain.RuntimeLimits{MaxStepsPerSpinChain: 500, MaxRespinsPerFeature: 100}
	base.Exposure = domain.Exposure{
		MaxWinMinorUnits: 1200000, MaxWinMultiplier: 5000, CapScope: "session_spin_chain",
		EnforceCap: true, ValidationMode: "strict",
	}
	base.Precedence = domain.Precedence{TriggerOrder: []string{"HOLD_AND_WIN", "FREE_SPINS", "FEATURE_COMPLETE", "SPIN_COMPLETE"}}
	base.RtpCategoryRegistry = &domain.RtpCategoryRegistry{
		Extends: "platform:v1",
		Categories: map[string]domain.RtpCategoryDef{
			"BASE":         {Label: "Base Game", DecompositionGroup: "base"},
			"FREE_SPINS":   {Label: "Free Spins", DecompositionGroup: "feature"},
			"HOLD_AND_WIN": {Label: "Hold and Win", DecompositionGroup: "feature"},
		},
	}
	return base
}

func boolPtr(v bool) *bool { return &v }
func intPtr(v int) *int    { return &v }

func TestValidBaseGame(t *testing.T) {
	engine := testEngine(t)
	report, err := engine.Validate(context.Background(), buildValidBaseGame())
	if err != nil {
		t.Fatalf("validate: %v", err)
	}
	if !report.Valid {
		t.Fatalf("expected valid base game, errors: %+v", report.Errors)
	}
	if report.Metadata.ValidatorVersion != validation.ValidatorVersion {
		t.Fatalf("unexpected validator version: %s", report.Metadata.ValidatorVersion)
	}
}

func TestValidNestedFSHAW(t *testing.T) {
	engine := testEngine(t)
	report, err := engine.Validate(context.Background(), buildNestedFSHAW())
	if err != nil {
		t.Fatalf("validate: %v", err)
	}
	if !report.Valid {
		t.Fatalf("expected valid nested game, errors: %+v", report.Errors)
	}
}

func TestInvalidTransitionTarget(t *testing.T) {
	game := buildValidBaseGame()
	main := game.StateMachines["main"]
	base := main.States["BASE"]
	base.Transitions = []domain.Transition{
		{ID: "t_bad", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 1000, Effect: "goto", TargetStateID: "MISSING"},
	}
	main.States["BASE"] = base
	game.StateMachines["main"] = main
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-003") {
		t.Fatalf("expected GV-003, got valid=%v errors=%+v", report.Valid, report.Errors)
	}
}

func TestOrphanStates(t *testing.T) {
	game := buildValidBaseGame()
	game.StateMachines["main"].States["ORPHAN"] = domain.State{
		ID: "ORPHAN", PluginRefID: "base_main", StateType: "atomic_spin", RtpCategory: "BASE",
		PluginConfig: map[string]any{"reelSetId": "base_game"},
		Transitions:  []domain.Transition{{ID: "t_stay", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 1000, Effect: "stay", TargetStateID: "ORPHAN"}},
	}
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-005") {
		t.Fatalf("expected GV-005, got valid=%v errors=%+v", report.Valid, report.Errors)
	}
}

func TestStackDepthExceeded(t *testing.T) {
	game := buildNestedFSHAW()
	game.Session.MaxStackDepth = 1
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-012") {
		t.Fatalf("expected GV-012, got valid=%v errors=%+v", report.Valid, report.Errors)
	}
}

func TestInvalidPluginConfiguration(t *testing.T) {
	game := buildValidBaseGame()
	main := game.StateMachines["main"]
	base := main.States["BASE"]
	base.PluginConfig = map[string]any{
		"reelSetId": "base_game",
		"scatterTriggers": []any{
			map[string]any{"symbolId": "SCATTER", "minCount": "three", "emitTrigger": "FREE_SPINS"},
		},
	}
	main.States["BASE"] = base
	game.StateMachines["main"] = main
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid {
		t.Fatalf("expected invalid plugin config, report=%+v", report)
	}
}

func TestInfiniteLoopDetection(t *testing.T) {
	game := buildValidBaseGame()
	game.Symbols["BONUS"] = domain.Symbol{ID: "BONUS", Type: "bonus", Pays: boolPtr(false)}
	game.Plugins["haw_main"] = domain.PluginRef{
		RefID: "haw_main", PluginID: "core.hold-and-win", PluginVersion: "1.0.0",
		ConfigSchemaVersion: "1.0.0", Capabilities: []string{"spin.grid", "state.multistep", "jackpot.local"},
	}
	game.ReelSets["hold_and_win"] = domain.ReelSet{
		ID: "hold_and_win",
		Reels: []domain.ReelStrip{
			{ReelIndex: 0, Symbols: []string{"BONUS", "L1", "BONUS", "L2", "BONUS"}},
			{ReelIndex: 1, Symbols: []string{"L2", "BONUS", "L1", "BONUS", "L2"}},
			{ReelIndex: 2, Symbols: []string{"BONUS", "BONUS", "L1", "L2", "BONUS"}},
			{ReelIndex: 3, Symbols: []string{"L1", "BONUS", "L2", "BONUS", "BONUS"}},
			{ReelIndex: 4, Symbols: []string{"BONUS", "L1", "BONUS", "BONUS", "L2"}},
		},
	}
	main := game.StateMachines["main"]
	main.States["LOOP"] = domain.State{
		ID: "LOOP", PluginRefID: "haw_main", StateType: "multi_step", RtpCategory: "HOLD_AND_WIN",
		PluginConfig: map[string]any{
			"reelSetId": "hold_and_win", "triggerSymbolId": "BONUS", "triggerSymbolCount": 6,
			"initialRespins": 3, "gridCapacity": 15,
		},
		Transitions: []domain.Transition{
			{ID: "t_loop", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 1000, Effect: "stay", TargetStateID: "LOOP"},
		},
	}
	game.StateMachines["main"] = main
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-011") {
		t.Fatalf("expected GV-011, got valid=%v errors=%+v", report.Valid, report.Errors)
	}
}

func TestSchemaValidationStopsPipeline(t *testing.T) {
	game := buildValidBaseGame()
	game.SchemaVersion = ""
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid {
		t.Fatal("expected schema failure")
	}
	if !hasCode(report, "SV-001") && !strings.HasPrefix(report.Errors[0].Code, "SV-") {
		t.Fatalf("expected SV-* schema error, got %+v", report.Errors)
	}
}

func TestGoldenFixtureFiles(t *testing.T) {
	engine := testEngine(t)
	root := repoRoot(t)
	fixtures := []struct {
		dir   string
		valid bool
	}{
		{"fixture-01-base-5x3", true},
		{"fixture-04-nested-fs-hold-win", true},
	}
	for _, fx := range fixtures {
		path := filepath.Join(root, "tests", "golden", fx.dir, "game.canonical.json")
		data, err := os.ReadFile(path)
		if err != nil {
			t.Fatalf("golden fixture %s: %v", fx.dir, err)
		}
		game := unmarshalGame(t, data)
		report, err := engine.Validate(context.Background(), game)
		if err != nil {
			t.Fatalf("%s validate: %v", fx.dir, err)
		}
		if report.Valid != fx.valid {
			t.Fatalf("%s valid=%v errors=%+v", fx.dir, report.Valid, report.Errors)
		}
	}
}

func TestValidationReportShape(t *testing.T) {
	report, err := testEngine(t).Validate(context.Background(), buildValidBaseGame())
	if err != nil {
		t.Fatal(err)
	}
	if !report.Valid {
		t.Fatalf("expected valid report, errors=%+v", report.Errors)
	}
	if report.Metadata.GameContentHash == "" {
		t.Fatal("expected content hash in metadata")
	}
	if report.Metadata.Timestamp.IsZero() {
		t.Fatal("expected timestamp in metadata")
	}
}

func TestExposureCapExceeded(t *testing.T) {
	game := buildValidBaseGame()
	game.Exposure = domain.Exposure{
		MaxWinMinorUnits: 100, MaxWinMultiplier: 1, CapScope: "session_spin_chain",
		EnforceCap: true, ValidationMode: "strict",
	}
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-023") {
		t.Fatalf("expected GV-023, got %+v", report.Errors)
	}
}

func TestLimitsRespinsExceeded(t *testing.T) {
	game := buildNestedFSHAW()
	game.Session.RuntimeLimits.MaxRespinsPerFeature = 1
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-037") {
		t.Fatalf("expected GV-037, got %+v", report.Errors)
	}
}

func TestPluginRefMissing(t *testing.T) {
	game := buildValidBaseGame()
	main := game.StateMachines["main"]
	base := main.States["BASE"]
	base.PluginRefID = "missing_plugin"
	main.States["BASE"] = base
	game.StateMachines["main"] = main
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-018") {
		t.Fatalf("expected GV-018, got %+v", report.Errors)
	}
}

func TestInvalidPopTransition(t *testing.T) {
	game := buildValidBaseGame()
	main := game.StateMachines["main"]
	base := main.States["BASE"]
	base.Transitions = append(base.Transitions, domain.Transition{
		ID: "bad_pop", Trigger: "FEATURE_COMPLETE", PriorityTier: "FEATURE_EXIT", Priority: 900,
		Effect: "pop", TargetStateID: "BASE",
	})
	main.States["BASE"] = base
	game.StateMachines["main"] = main
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-010") {
		t.Fatalf("expected GV-010, got %+v", report.Errors)
	}
}

func TestPriorityOutOfRange(t *testing.T) {
	game := buildValidBaseGame()
	main := game.StateMachines["main"]
	base := main.States["BASE"]
	base.Transitions = []domain.Transition{
		{ID: "t1", Trigger: "SPIN_COMPLETE", PriorityTier: "FALLBACK", Priority: 50, Effect: "stay", TargetStateID: "BASE"},
	}
	main.States["BASE"] = base
	game.StateMachines["main"] = main
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-027") {
		t.Fatalf("expected GV-027, got %+v", report.Errors)
	}
}

func TestLimitsFramesExceedStack(t *testing.T) {
	game := buildValidBaseGame()
	game.Session.RuntimeLimits.MaxFramesPerChain = 10
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-036") {
		t.Fatalf("expected GV-036, got %+v", report.Errors)
	}
}

func TestExposureValidatorDirect(t *testing.T) {
	v := validation.NewExposureValidator()
	game := buildValidBaseGame()
	game.Exposure.CapScope = "not_valid"
	report := v.Validate(game)
	if report.Valid || !hasCode(report, "GV-023") {
		t.Fatalf("expected exposure scope error, got %+v", report.Errors)
	}
}

func TestUnsupportedPluginVersion(t *testing.T) {
	game := buildValidBaseGame()
	game.Plugins["base_main"] = domain.PluginRef{
		RefID: "base_main", PluginID: "core.base-game", PluginVersion: "9.9.9",
		ConfigSchemaVersion: "1.0.0", Capabilities: []string{"spin.grid", "win.lines", "win.scatter"},
	}
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-019") {
		t.Fatalf("expected GV-019, got %+v", report.Errors)
	}
}

func TestExposureMultiplierZero(t *testing.T) {
	v := validation.NewExposureValidator()
	game := buildValidBaseGame()
	game.Exposure.MaxWinMultiplier = 0
	report := v.Validate(game)
	if report.Valid || !hasCode(report, "GV-023") {
		t.Fatalf("expected multiplier error, got %+v", report.Errors)
	}
}

func TestLimitsValidatorNil(t *testing.T) {
	report := validation.NewLimitsValidator().Validate(nil)
	if !report.Valid {
		t.Fatal("expected valid for nil game")
	}
}

func TestPluginValidatorNil(t *testing.T) {
	report := validation.NewPluginValidator(nil, nil).Validate(nil)
	if !report.Valid {
		t.Fatal("expected valid for nil game")
	}
}

func TestEngineNilGame(t *testing.T) {
	engine := testEngine(t)
	_, err := engine.Validate(context.Background(), nil)
	if err == nil {
		t.Fatal("expected nil game error")
	}
}

func TestDuplicateTransitionID(t *testing.T) {
	game := buildValidBaseGame()
	main := game.StateMachines["main"]
	base := main.States["BASE"]
	base.Transitions = append(base.Transitions, base.Transitions[0])
	main.States["BASE"] = base
	game.StateMachines["main"] = main
	report, err := testEngine(t).Validate(context.Background(), game)
	if err != nil {
		t.Fatal(err)
	}
	if report.Valid || !hasCode(report, "GV-013") {
		t.Fatalf("expected GV-013, got %+v", report.Errors)
	}
}

func TestSchemaPathsFromEnv(t *testing.T) {
	root := repoRoot(t)
	t.Setenv("MATH_ASSISTANT_SCHEMA_ROOT", filepath.Join(root, "packages", "game-schema"))
	paths, err := validation.DefaultSchemaPaths()
	if err != nil {
		t.Fatal(err)
	}
	if paths.GameSchema == "" {
		t.Fatal("expected schema path")
	}
}

func TestContextCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	_, err := testEngine(t).Validate(ctx, buildValidBaseGame())
	if err == nil {
		t.Fatal("expected context error")
	}
}
