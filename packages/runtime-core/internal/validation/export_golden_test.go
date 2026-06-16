package validation_test

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

// TestWriteGoldenFixtures materializes canonical JSON under tests/golden (run manually when fixtures change).
func TestWriteGoldenFixtures(t *testing.T) {
	root := repoRoot(t)
	fixtures := map[string]any{
		"fixture-01-base-5x3/game.canonical.json":           buildValidBaseGame(),
		"fixture-04-nested-fs-hold-win/game.canonical.json": buildNestedFSHAW(),
	}
	for rel, game := range fixtures {
		dir := filepath.Join(root, "tests", "golden", filepath.Dir(rel))
		if err := os.MkdirAll(dir, 0o755); err != nil {
			t.Fatal(err)
		}
		data, err := json.MarshalIndent(game, "", "  ")
		if err != nil {
			t.Fatal(err)
		}
		path := filepath.Join(root, "tests", "golden", rel)
		if err := os.WriteFile(path, append(data, '\n'), 0o644); err != nil {
			t.Fatal(err)
		}
	}
}
