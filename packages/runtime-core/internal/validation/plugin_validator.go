package validation

import (
	"math-assistant/runtime-core/internal/domain"
	"math-assistant/runtime-core/internal/validation/validators"
)

var supportedPluginVersions = map[string]map[string]struct{}{
	"core.base-game":    {"1.0.0": {}},
	"core.free-spins":   {"1.0.0": {}},
	"core.hold-and-win": {"1.0.0": {}},
	"core.multiplier":   {"1.0.0": {}},
}

var requiredCapabilities = map[string][]string{
	"atomic_spin": {"spin.grid"},
	"multi_step":  {"spin.grid", "state.multistep"},
}

// PluginValidator validates plugin references, versions, configs, and capabilities.
type PluginValidator struct {
	schema  *SchemaValidator
	rtpReg  *validators.RtpCategoryRegistry
}

// NewPluginValidator constructs a plugin validator.
func NewPluginValidator(schema *SchemaValidator, rtpReg *validators.RtpCategoryRegistry) *PluginValidator {
	return &PluginValidator{
		schema: schema,
		rtpReg: rtpReg,
	}
}

// Validate runs plugin-level checks (GV-xxx).
func (v *PluginValidator) Validate(game *domain.GameVersion) *ValidationReport {
	report := NewReport("")
	if game == nil {
		return report
	}
	rtp := v.rtpReg.Clone()
	if rtp != nil {
		rtp.MergeDocument(game)
	}
	for machineID, machine := range game.StateMachines {
		for stateID, state := range machine.States {
			statePath := "stateMachines." + machineID + ".states." + stateID
			plugin, ok := game.Plugins[state.PluginRefID]
			if !ok {
				report.AddError(GraphPluginRefMissing(statePath+".pluginRefId", state.PluginRefID))
				continue
			}
			if !isSupportedPluginVersion(plugin.PluginID, plugin.PluginVersion) {
				report.AddError(GraphPluginVersionUnsupported(plugin.RefID, plugin.PluginID, plugin.PluginVersion))
			}
			for _, cap := range requiredCapabilitiesForState(state.StateType) {
				if !hasCapability(plugin.Capabilities, cap) {
					report.AddError(GraphPluginCapabilityMissing(plugin.RefID, cap))
				}
			}
			if rtp != nil && state.RtpCategory != "" && !rtp.IsKnown(state.RtpCategory) {
				report.AddError(GraphRtpCategoryUnknown(statePath+".rtpCategory", state.RtpCategory))
			}
			basePath := statePath + ".pluginConfig"
			for _, issue := range v.schema.ValidatePluginConfig(plugin.PluginID, plugin.PluginVersion, state.PluginConfig) {
				issue.Path = basePath
				report.AddError(issue)
			}
		}
	}
	addFindings(report, validators.ValidatePluginReferences(game))
	return report
}

func isSupportedPluginVersion(pluginID, version string) bool {
	versions, ok := supportedPluginVersions[pluginID]
	if !ok {
		return false
	}
	_, ok = versions[version]
	return ok
}

func requiredCapabilitiesForState(stateType string) []string {
	return requiredCapabilities[stateType]
}

func hasCapability(caps []string, required string) bool {
	for _, c := range caps {
		if c == required {
			return true
		}
	}
	return false
}
