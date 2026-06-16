package validation

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"github.com/santhosh-tekuri/jsonschema/v6"
)

// SchemaPaths locates canonical JSON Schema files.
type SchemaPaths struct {
	GameSchema     string
	PluginSchemaDir string
}

// SchemaValidator validates raw JSON against game-version-1.0.0.schema.json.
type SchemaValidator struct {
	gameSchema *jsonschema.Schema
	pluginDir  string
	mu         sync.Mutex
	pluginCache map[string]*jsonschema.Schema
}

// NewSchemaValidator loads schemas from the given paths.
func NewSchemaValidator(paths SchemaPaths) (*SchemaValidator, error) {
	if _, err := os.Stat(paths.GameSchema); err != nil {
		return nil, fmt.Errorf("read game schema: %w", err)
	}
	compiler := jsonschema.NewCompiler()
	compiler.DefaultDraft(jsonschema.Draft2020)
	compiler.UseLoader(jsonschema.FileLoader{})
	schemaURL := fileURL(paths.GameSchema)
	sch, err := compiler.Compile(schemaURL)
	if err != nil {
		return nil, fmt.Errorf("compile game schema: %w", err)
	}
	return &SchemaValidator{
		gameSchema:  sch,
		pluginDir:   paths.PluginSchemaDir,
		pluginCache: make(map[string]*jsonschema.Schema),
	}, nil
}

// ValidateGame runs JSON Schema validation and returns SV-xxx issues.
func (v *SchemaValidator) ValidateGame(raw []byte) (*ValidationReport, error) {
	report := NewReport(contentHash(raw))
	var doc any
	if err := json.Unmarshal(raw, &doc); err != nil {
		report.AddError(errIssue("SV-002", "$", "document is not valid JSON: "+err.Error(),
			"Provide well-formed JSON"))
		return report, nil
	}
	if err := v.gameSchema.Validate(doc); err != nil {
		mapSchemaError(report, err)
	}
	return report, nil
}

// ValidatePluginConfig validates plugin configuration JSON against a plugin schema file.
func (v *SchemaValidator) ValidatePluginConfig(pluginID, configSchemaVersion string, config map[string]any) []ValidationIssue {
	if config == nil {
		return nil
	}
	schemaFile, ok := pluginSchemaFile(pluginID, configSchemaVersion)
	if !ok {
		return []ValidationIssue{
			GraphPluginVersionUnsupported("", pluginID, configSchemaVersion),
		}
	}
	sch, err := v.loadPluginSchema(schemaFile)
	if err != nil {
		return []ValidationIssue{
			GraphPluginConfigInvalid("pluginConfig", err.Error()),
		}
	}
	if err := sch.Validate(config); err != nil {
		var issues []ValidationIssue
		collectPluginSchemaErrors(&issues, "pluginConfig", err)
		if len(issues) == 0 {
			issues = append(issues, GraphPluginConfigInvalid("pluginConfig", err.Error()))
		}
		return issues
	}
	return nil
}

func (v *SchemaValidator) loadPluginSchema(filename string) (*jsonschema.Schema, error) {
	v.mu.Lock()
	defer v.mu.Unlock()
	if sch, ok := v.pluginCache[filename]; ok {
		return sch, nil
	}
	path := filepath.Join(v.pluginDir, filename)
	compiler := jsonschema.NewCompiler()
	compiler.DefaultDraft(jsonschema.Draft2020)
	compiler.UseLoader(jsonschema.FileLoader{})
	url := fileURL(path)
	sch, err := compiler.Compile(url)
	if err != nil {
		return nil, err
	}
	v.pluginCache[filename] = sch
	return sch, nil
}

func fileURL(path string) string {
	abs, err := filepath.Abs(path)
	if err != nil {
		abs = path
	}
	return "file://" + filepath.ToSlash(abs)
}

func pluginSchemaFile(pluginID, version string) (string, bool) {
	switch pluginID {
	case "core.base-game":
		if version == "1.0.0" {
			return "base-game-1.0.0.schema.json", true
		}
	case "core.free-spins":
		if version == "1.0.0" {
			return "free-spins-1.0.0.schema.json", true
		}
	case "core.hold-and-win":
		if version == "1.0.0" {
			return "hold-and-win-1.0.0.schema.json", true
		}
	case "core.multiplier":
		if version == "1.0.0" {
			return "multiplier-1.0.0.schema.json", true
		}
	}
	return "", false
}

func mapSchemaError(report *ValidationReport, err error) {
	ve, ok := err.(*jsonschema.ValidationError)
	if !ok {
		report.AddError(schemaGeneric("$", err.Error()))
		return
	}
	walkSchemaErrors(report, ve)
}

func walkSchemaErrors(report *ValidationReport, ve *jsonschema.ValidationError) {
	if ve == nil {
		return
	}
	path := jsonPointerPath(ve.InstanceLocation)
	msg := ve.Error()
	issue := schemaGeneric(path, msg)
	lower := strings.ToLower(msg)
	switch {
	case strings.Contains(lower, "required"):
		issue = schemaRequired(path, msg)
	case strings.Contains(lower, "expected"):
		issue = schemaType(path, msg)
	case strings.Contains(lower, "enum"):
		issue = schemaEnum(path, msg)
	case strings.Contains(lower, "pattern"):
		issue = schemaPattern(path)
	case strings.Contains(lower, "minimum") || strings.Contains(lower, "maximum") ||
		strings.Contains(lower, "minlength") || strings.Contains(lower, "maxlength"):
		issue = schemaRange(path, msg)
	case strings.Contains(lower, "additional properties"):
		issue = schemaAdditionalProperty(path, msg)
	}
	report.AddError(issue)
	for _, cause := range ve.Causes {
		walkSchemaErrors(report, cause)
	}
}

func collectPluginSchemaErrors(issues *[]ValidationIssue, basePath string, err error) {
	ve, ok := err.(*jsonschema.ValidationError)
	if !ok {
		*issues = append(*issues, GraphPluginConfigInvalid(basePath, err.Error()))
		return
	}
	path := basePath
	if len(ve.InstanceLocation) > 0 {
		path = basePath + "." + strings.Join(ve.InstanceLocation, ".")
	}
	*issues = append(*issues, GraphPluginConfigInvalid(path, ve.Error()))
	for _, cause := range ve.Causes {
		collectPluginSchemaErrors(issues, basePath, cause)
	}
}

func jsonPointerPath(instanceLocation []string) string {
	if len(instanceLocation) == 0 {
		return "$"
	}
	return "$." + strings.Join(instanceLocation, ".")
}

func contentHash(raw []byte) string {
	sum := sha256.Sum256(raw)
	return hex.EncodeToString(sum[:])
}

// DefaultSchemaPaths resolves schema locations relative to the runtime-core module.
func DefaultSchemaPaths() (SchemaPaths, error) {
	root, err := findRepoSchemaRoot()
	if err != nil {
		return SchemaPaths{}, err
	}
	return SchemaPaths{
		GameSchema:      filepath.Join(root, "schemas", "game-version-1.0.0.schema.json"),
		PluginSchemaDir: filepath.Join(root, "schemas", "plugins"),
	}, nil
}

func findRepoSchemaRoot() (string, error) {
	if env := os.Getenv("MATH_ASSISTANT_SCHEMA_ROOT"); env != "" {
		if _, err := os.Stat(filepath.Join(env, "schemas", "game-version-1.0.0.schema.json")); err == nil {
			return env, nil
		}
	}
	wd, err := os.Getwd()
	if err != nil {
		return "", err
	}
	dir := wd
	for {
		candidate := filepath.Join(dir, "packages", "game-schema")
		if _, err := os.Stat(filepath.Join(candidate, "schemas", "game-version-1.0.0.schema.json")); err == nil {
			return candidate, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
	return "", fmt.Errorf("game-schema root not found (cwd=%s)", wd)
}

// LoadFixture reads a JSON fixture from an fs.FS (for golden tests).
func LoadFixture(fsys fs.FS, name string) ([]byte, error) {
	return fs.ReadFile(fsys, name)
}
