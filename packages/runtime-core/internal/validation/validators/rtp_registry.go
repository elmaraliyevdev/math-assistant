package validators

import (
	"encoding/json"
	"fmt"
	"math-assistant/runtime-core/internal/domain"
	"os"
	"path/filepath"
)

// RtpCategoryRegistry resolves rtpCategory ids for states.
type RtpCategoryRegistry struct {
	categories map[string]struct{}
}

// LoadRtpCategoryRegistry loads rtp-categories-v1.json from the schema root registries folder.
func LoadRtpCategoryRegistry(schemaRoot string) (*RtpCategoryRegistry, error) {
	path := filepath.Join(schemaRoot, "registries", "rtp-categories-v1.json")
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read rtp categories: %w", err)
	}
	var doc struct {
		Categories []struct {
			ID string `json:"id"`
		} `json:"categories"`
		Aliases []struct {
			ID     string `json:"id"`
			MapsTo string `json:"mapsTo"`
		} `json:"aliases"`
	}
	if err := json.Unmarshal(data, &doc); err != nil {
		return nil, fmt.Errorf("parse rtp categories: %w", err)
	}
	reg := &RtpCategoryRegistry{categories: make(map[string]struct{})}
	for _, c := range doc.Categories {
		reg.categories[c.ID] = struct{}{}
	}
	for _, a := range doc.Aliases {
		reg.categories[a.ID] = struct{}{}
	}
	return reg, nil
}

func (r *RtpCategoryRegistry) IsKnown(category string) bool {
	if r == nil {
		return false
	}
	_, ok := r.categories[category]
	return ok
}

func (r *RtpCategoryRegistry) MergeDocument(game *domain.GameVersion) {
	if r == nil || game == nil || game.RtpCategoryRegistry == nil {
		return
	}
	for id := range game.RtpCategoryRegistry.Categories {
		r.categories[id] = struct{}{}
	}
}

func (r *RtpCategoryRegistry) Clone() *RtpCategoryRegistry {
	if r == nil {
		return nil
	}
	copyReg := &RtpCategoryRegistry{categories: make(map[string]struct{}, len(r.categories))}
	for id := range r.categories {
		copyReg.categories[id] = struct{}{}
	}
	return copyReg
}
