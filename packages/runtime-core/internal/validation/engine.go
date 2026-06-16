package validation

import (
	"context"
	"encoding/json"
	"fmt"
	"path/filepath"

	"math-assistant/runtime-core/internal/domain"
	"math-assistant/runtime-core/internal/validation/validators"
)

// Engine validates Canonical Game Schema v1.0.0 documents.
type Engine interface {
	Validate(ctx context.Context, game *domain.GameVersion) (*ValidationReport, error)
}

type engine struct {
	schema   *SchemaValidator
	graph    *GraphValidator
	plugin   *PluginValidator
	exposure *ExposureValidator
	limits   *LimitsValidator
}

// Config configures validation engine dependencies.
type Config struct {
	SchemaPaths SchemaPaths
	SchemaRoot  string
}

// NewEngine constructs a validation engine with default schema resolution.
func NewEngine(cfg Config) (Engine, error) {
	if cfg.SchemaPaths.GameSchema == "" {
		paths, err := DefaultSchemaPaths()
		if err != nil {
			return nil, err
		}
		cfg.SchemaPaths = paths
	}
	if cfg.SchemaRoot == "" {
		cfg.SchemaRoot = filepath.Dir(filepath.Dir(cfg.SchemaPaths.GameSchema))
	}
	schemaVal, err := NewSchemaValidator(cfg.SchemaPaths)
	if err != nil {
		return nil, fmt.Errorf("schema validator: %w", err)
	}
	tiers, err := validators.LoadPriorityTierRegistry(cfg.SchemaRoot)
	if err != nil {
		return nil, fmt.Errorf("priority tiers: %w", err)
	}
	rtpReg, err := validators.LoadRtpCategoryRegistry(cfg.SchemaRoot)
	if err != nil {
		return nil, fmt.Errorf("rtp categories: %w", err)
	}
	return &engine{
		schema:   schemaVal,
		graph:    NewGraphValidator(tiers),
		plugin:   NewPluginValidator(schemaVal, rtpReg),
		exposure: NewExposureValidator(),
		limits:   NewLimitsValidator(),
	}, nil
}

// Validate runs schema → graph → plugin → exposure → limits validation.
func (e *engine) Validate(ctx context.Context, game *domain.GameVersion) (*ValidationReport, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	if game == nil {
		return nil, fmt.Errorf("game is nil")
	}
	raw, err := json.Marshal(game)
	if err != nil {
		return nil, fmt.Errorf("marshal game: %w", err)
	}
	schemaReport, err := e.schema.ValidateGame(raw)
	if err != nil {
		return nil, err
	}
	if schemaReport.HasErrors() {
		return schemaReport, nil
	}
	report := NewReport(schemaReport.Metadata.GameContentHash)
	report.Merge(e.graph.Validate(game))
	report.Merge(e.plugin.Validate(game))
	report.Merge(e.exposure.Validate(game))
	report.Merge(e.limits.Validate(game))
	return report, nil
}
