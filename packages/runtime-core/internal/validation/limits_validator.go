package validation

import (
	"math-assistant/runtime-core/internal/domain"
)

// LimitsValidator validates runtime limit consistency (GV-036, GV-037).
type LimitsValidator struct{}

// NewLimitsValidator constructs a limits validator.
func NewLimitsValidator() *LimitsValidator {
	return &LimitsValidator{}
}

// Validate checks runtimeLimits against session and plugin configuration.
func (v *LimitsValidator) Validate(game *domain.GameVersion) *ValidationReport {
	report := NewReport("")
	if game == nil {
		return report
	}
	limits := game.Session.RuntimeLimits
	if limits == nil {
		return report
	}
	stack := game.Session.MaxStackDepth
	if stack <= 0 {
		stack = 8
	}
	if limits.MaxFramesPerChain > 0 && limits.MaxFramesPerChain > stack {
		report.AddError(GraphLimitsFramesExceedStack(limits.MaxFramesPerChain, stack))
	}
	if limits.MaxRespinsPerFeature <= 0 {
		return report
	}
	for machineID, machine := range game.StateMachines {
		for stateID, state := range machine.States {
			cfg := state.PluginConfig
			if cfg == nil {
				continue
			}
			respins, ok := cfg["initialRespins"].(float64)
			if !ok {
				if ri, ok := cfg["initialRespins"].(int); ok {
					respins = float64(ri)
				} else {
					continue
				}
			}
			if int(respins) > limits.MaxRespinsPerFeature {
				path := "stateMachines." + machineID + ".states." + stateID + ".pluginConfig.initialRespins"
				report.AddError(GraphLimitsRespinsExceeded(path, int(respins), limits.MaxRespinsPerFeature))
			}
		}
	}
	return report
}
