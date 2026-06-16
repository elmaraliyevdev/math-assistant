package validators

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// PriorityTier describes a registered transition priority tier.
type PriorityTier struct {
	ID              string
	DefaultPriority int
	RangeMin        int
	RangeMax        int
	Aliases         []string
}

// PriorityTierRegistry resolves priority tier ids and aliases.
type PriorityTierRegistry struct {
	byID map[string]PriorityTier
}

// LoadPriorityTierRegistry loads priority-tiers-v1.json from the schema root registries folder.
func LoadPriorityTierRegistry(schemaRoot string) (*PriorityTierRegistry, error) {
	path := filepath.Join(schemaRoot, "registries", "priority-tiers-v1.json")
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read priority tiers: %w", err)
	}
	var doc struct {
		Tiers []struct {
			ID              string   `json:"id"`
			DefaultPriority int      `json:"defaultPriority"`
			NumericRange    struct {
				Min int `json:"min"`
				Max int `json:"max"`
			} `json:"numericRange"`
			Aliases []string `json:"aliases"`
		} `json:"tiers"`
	}
	if err := json.Unmarshal(data, &doc); err != nil {
		return nil, fmt.Errorf("parse priority tiers: %w", err)
	}
	reg := &PriorityTierRegistry{byID: make(map[string]PriorityTier)}
	for _, t := range doc.Tiers {
		tier := PriorityTier{
			ID:              t.ID,
			DefaultPriority: t.DefaultPriority,
			RangeMin:        t.NumericRange.Min,
			RangeMax:        t.NumericRange.Max,
			Aliases:         t.Aliases,
		}
		reg.byID[t.ID] = tier
		for _, alias := range t.Aliases {
			reg.byID[alias] = tier
		}
	}
	return reg, nil
}

// Resolve returns the tier for an id or alias.
func (r *PriorityTierRegistry) Resolve(id string) (PriorityTier, bool) {
	if r == nil {
		return PriorityTier{}, false
	}
	t, ok := r.byID[id]
	return t, ok
}
