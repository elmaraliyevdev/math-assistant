package validators

import (
	"fmt"
	"math-assistant/runtime-core/internal/domain"
)

// ValidatePluginReferences checks symbol, reel set, and plugin cross-references in configs.
func ValidatePluginReferences(game *domain.GameVersion) []Finding {
	var findings []Finding
	if game == nil {
		return findings
	}
	for machineID, machine := range game.StateMachines {
		for stateID, state := range machine.States {
			basePath := "stateMachines." + machineID + ".states." + stateID + ".pluginConfig"
			findings = append(findings, validateSymbolRefs(game, basePath, state.PluginConfig)...)
			findings = append(findings, validateReelSet(game, basePath, state.PluginConfig)...)
		}
	}
	return findings
}

func validateSymbolRefs(game *domain.GameVersion, basePath string, config map[string]any) []Finding {
	var findings []Finding
	if config == nil {
		return findings
	}
	checkSymbol := func(field string, id string) {
		if id == "" {
			return
		}
		if _, ok := game.Symbols[id]; !ok {
			findings = append(findings, errFinding("GV-021", basePath+"."+field,
				"symbol '"+id+"' referenced in plugin config does not exist",
				"Define the symbol in symbols or fix the reference"))
		}
	}
	if v, ok := config["reelSetId"].(string); ok {
		if _, ok := game.ReelSets[v]; !ok {
			findings = append(findings, errFinding("GV-021", basePath+".reelSetId",
				"symbol '"+v+"' referenced in plugin config does not exist",
				"Define the symbol in symbols or fix the reference"))
		}
	}
	if v, ok := config["triggerSymbolId"].(string); ok {
		checkSymbol("triggerSymbolId", v)
	}
	if v, ok := config["multiplierRefId"].(string); ok {
		if _, ok := game.Plugins[v]; !ok {
			findings = append(findings, errFinding("GV-018", basePath+".multiplierRefId",
				"pluginRefId '"+v+"' does not exist in plugins registry",
				"Define the plugin reference or fix pluginRefId"))
		}
	}
	for _, field := range []string{"scatterTriggers", "bonusTriggers"} {
		triggers, ok := config[field].([]any)
		if !ok {
			continue
		}
		for i, item := range triggers {
			m, ok := item.(map[string]any)
			if !ok {
				continue
			}
			if sym, ok := m["symbolId"].(string); ok {
				checkSymbol(fmt.Sprintf("%s[%d].symbolId", field, i), sym)
			}
		}
	}
	return findings
}

func validateReelSet(game *domain.GameVersion, basePath string, config map[string]any) []Finding {
	reelSetID, ok := config["reelSetId"].(string)
	if !ok || reelSetID == "" {
		return nil
	}
	reelSet, ok := game.ReelSets[reelSetID]
	if !ok {
		return nil
	}
	expected := game.GameConfig.Grid.Reels
	if expected > 0 && len(reelSet.Reels) != expected {
		return []Finding{errFinding("GV-022", basePath+".reelSetId",
			"reel set reel count does not match game grid",
			"Ensure reel set has "+itoa(expected)+" reels (found "+itoa(len(reelSet.Reels))+")")}
	}
	return nil
}
