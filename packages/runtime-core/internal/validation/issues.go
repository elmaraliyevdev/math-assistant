package validation

// Issue constructors for canonical validation error codes.

func issue(code, path, message, suggestion string) ValidationIssue {
	return ValidationIssue{
		Code:       code,
		Path:       path,
		Message:    message,
		Suggestion: suggestion,
	}
}

func errIssue(code, path, message, suggestion string) ValidationIssue {
	i := issue(code, path, message, suggestion)
	i.Severity = SeverityError
	return i
}

func warnIssue(code, path, message, suggestion string) ValidationIssue {
	i := issue(code, path, message, suggestion)
	i.Severity = SeverityWarning
	return i
}

// Schema issue helpers (SV-xxx).
func schemaRequired(path, field string) ValidationIssue {
	return errIssue("SV-001", path,
		"required property missing: "+field,
		"Add the required field to satisfy the canonical schema")
}

func schemaType(path, expected string) ValidationIssue {
	return errIssue("SV-002", path,
		"value has incorrect type; expected "+expected,
		"Correct the value type to match the schema definition")
}

func schemaEnum(path, allowed string) ValidationIssue {
	return errIssue("SV-003", path,
		"value is not in allowed enum",
		"Use one of: "+allowed)
}

func schemaPattern(path string) ValidationIssue {
	return errIssue("SV-004", path,
		"value does not match required pattern",
		"Adjust the value to match the schema pattern constraint")
}

func schemaRange(path, detail string) ValidationIssue {
	return errIssue("SV-005", path,
		"numeric constraint violated: "+detail,
		"Adjust the numeric value to fall within schema bounds")
}

func schemaAdditionalProperty(path, prop string) ValidationIssue {
	return errIssue("SV-006", path,
		"additional property not allowed: "+prop,
		"Remove the unknown property or move it to extensions")
}

func schemaGeneric(path, message string) ValidationIssue {
	return errIssue("SV-001", path, message,
		"Fix the document to conform to game-version-1.0.0.schema.json")
}

// Graph issue helpers (GV-xxx).
func GraphInitialStateMissing(machineID, stateID string) ValidationIssue {
	return errIssue("GV-001",
		"stateMachines."+machineID+".initialStateId",
		"initial state '"+stateID+"' is not defined in states map",
		"Define the initial state or update initialStateId")
}

func GraphRootMachineMissing(id string) ValidationIssue {
	return errIssue("GV-002", "session.rootMachineId",
		"root machine '"+id+"' does not exist in stateMachines",
		"Set rootMachineId to an existing state machine id")
}

func GraphTransitionTargetMissing(machineID, stateID, transitionID, target string) ValidationIssue {
	return errIssue("GV-003",
		"stateMachines."+machineID+".states."+stateID+".transitions."+transitionID,
		"transition target state '"+target+"' does not exist in machine '"+machineID+"'",
		"Point targetStateId to an existing state or remove the transition")
}

func GraphSpawnTargetMissing(machineID, stateID, transitionID, target string) ValidationIssue {
	return errIssue("GV-004",
		"stateMachines."+machineID+".states."+stateID+".transitions."+transitionID,
		"spawn target machine '"+target+"' does not exist",
		"Define the nested machine or fix targetMachineId")
}

func GraphOrphanState(machineID, stateID string) ValidationIssue {
	return errIssue("GV-005",
		"stateMachines."+machineID+".states."+stateID,
		"state is unreachable from the session entry point",
		"Add transitions that reach this state or mark it deprecated")
}

func GraphDeadEnd(machineID, stateID string) ValidationIssue {
	return errIssue("GV-006",
		"stateMachines."+machineID+".states."+stateID,
		"non-terminal state has no outgoing transitions",
		"Add transitions or mark the state terminal")
}

func GraphSpawnNoPop(machineID string) ValidationIssue {
	return errIssue("GV-008",
		"stateMachines."+machineID,
		"spawned machine has no pop transition path to return to parent",
		"Add a FEATURE_COMPLETE transition with effect pop")
}

func GraphInfiniteLoop(machineID, stateID string) ValidationIssue {
	return errIssue("GV-011",
		"stateMachines."+machineID+".states."+stateID,
		"infinite progression loop detected without terminating progression metadata",
		"Add progression metadata or a terminating transition")
}

func GraphStackDepthExceeded(worstCase, limit int) ValidationIssue {
	return errIssue("GV-012", "session.maxStackDepth",
		"worst-case spawn stack depth exceeds maxStackDepth",
		"Increase maxStackDepth or reduce nested spawn depth (worst case: "+itoa(worstCase)+", limit: "+itoa(limit)+")")
}

func GraphDuplicateTransitionID(machineID, stateID, transitionID string) ValidationIssue {
	return errIssue("GV-013",
		"stateMachines."+machineID+".states."+stateID+".transitions",
		"duplicate transition id '"+transitionID+"' within state",
		"Assign unique transition ids per state")
}

func GraphDuplicateStateID(machineID, stateID string) ValidationIssue {
	return errIssue("GV-014",
		"stateMachines."+machineID+".states",
		"duplicate state id '"+stateID+"'",
		"Ensure state map keys match unique state ids")
}

func GraphDuplicateMachineID(machineID string) ValidationIssue {
	return errIssue("GV-015", "stateMachines",
		"duplicate state machine id '"+machineID+"'",
		"Ensure machine map keys match unique machine ids")
}

func GraphPriorityConflict(machineID, stateID, trigger string) ValidationIssue {
	return warnIssue("GV-016",
		"stateMachines."+machineID+".states."+stateID+".transitions",
		"multiple transitions share trigger '"+trigger+"' with identical priority and tier",
		"Differentiate priority or priorityTier to resolve ambiguity")
}

func GraphAmbiguousTransitions(machineID, stateID, trigger string) ValidationIssue {
	return errIssue("GV-017",
		"stateMachines."+machineID+".states."+stateID+".transitions",
		"ambiguous transition set for trigger '"+trigger+"' cannot be resolved by precedence",
		"Adjust priorities or precedence.triggerOrder")
}

func GraphPluginRefMissing(statePath, refID string) ValidationIssue {
	return errIssue("GV-018", statePath,
		"pluginRefId '"+refID+"' does not exist in plugins registry",
		"Define the plugin reference or fix pluginRefId")
}

func GraphPluginVersionUnsupported(refID, pluginID, version string) ValidationIssue {
	return errIssue("GV-019", "plugins."+refID,
		"plugin version '"+version+"' is not supported for "+pluginID,
		"Use a supported plugin version (MVP: 1.0.0)")
}

func GraphPluginCapabilityMissing(refID, capability string) ValidationIssue {
	return errIssue("GV-020", "plugins."+refID,
		"required capability '"+capability+"' is not declared",
		"Add the capability to the plugin reference")
}

func GraphPluginSymbolMissing(path, symbolID string) ValidationIssue {
	return errIssue("GV-021", path,
		"symbol '"+symbolID+"' referenced in plugin config does not exist",
		"Define the symbol in symbols or fix the reference")
}

func GraphPluginReelMismatch(path string, expected, actual int) ValidationIssue {
	return errIssue("GV-022", path,
		"reel set reel count does not match game grid",
		"Ensure reel set has "+itoa(expected)+" reels (found "+itoa(actual)+")")
}

func GraphExposureCapExceeded(theoretical, cap int64) ValidationIssue {
	return errIssue("GV-023", "exposure",
		"theoretical max win exceeds effective exposure cap",
		"Raise exposure caps or reduce paytable/jackpot potential (theoretical: "+itoa64(theoretical)+", cap: "+itoa64(cap)+")")
}

func GraphRtpCategoryUnknown(statePath, category string) ValidationIssue {
	return errIssue("GV-025", statePath,
		"rtpCategory '"+category+"' is not registered",
		"Use a platform or document registry category id")
}

func GraphPriorityTierUnknown(transitionPath, tier string) ValidationIssue {
	return errIssue("GV-027", transitionPath,
		"unknown priorityTier '"+tier+"'",
		"Use a tier from priority-tiers-v1.json")
}

func GraphPriorityTierMissing(transitionPath string) ValidationIssue {
	return warnIssue("GV-028", transitionPath,
		"transition is missing priorityTier",
		"Set priorityTier to a registered tier for deterministic ordering")
}

func GraphPriorityOutOfRange(transitionPath, tier string) ValidationIssue {
	return errIssue("GV-027", transitionPath,
		"priority is outside allowed range for tier '"+tier+"'",
		"Set priority within the tier numericRange or use defaultPriority")
}

func GraphInvalidPop(transitionPath string) ValidationIssue {
	return errIssue("GV-010", transitionPath,
		"pop effect must not specify targetStateId or targetMachineId",
		"Remove target fields from pop transitions")
}

func GraphMultipleInitialStates(machineID string) ValidationIssue {
	return errIssue("GV-001", "stateMachines."+machineID,
		"state machine must have exactly one initial state",
		"Set initialStateId to a single defined state")
}

func GraphPluginConfigInvalid(path, detail string) ValidationIssue {
	return errIssue("GV-021", path,
		"plugin configuration failed schema validation: "+detail,
		"Fix pluginConfig to match the plugin schema")
}

func GraphExposureMultiplierInvalid() ValidationIssue {
	return errIssue("GV-023", "exposure.maxWinMultiplier",
		"maxWinMultiplier must be greater than 0 in strict mode",
		"Set a positive maxWinMultiplier or remove enforceCap")
}

func GraphExposureCapInvalid() ValidationIssue {
	return errIssue("GV-023", "exposure.maxWinMinorUnits",
		"maxWinMinorUnits must be greater than 0 when enforceCap is true",
		"Set a positive exposure cap in minor units")
}

func GraphExposureScopeInvalid(scope string) ValidationIssue {
	return errIssue("GV-023", "exposure.capScope",
		"invalid capScope '"+scope+"'",
		"Use session_spin_chain, feature_instance, or spin_step")
}

func GraphLimitsFramesExceedStack(frames, stack int) ValidationIssue {
	return errIssue("GV-036", "session.runtimeLimits.maxFramesPerChain",
		"maxFramesPerChain exceeds maxStackDepth",
		"Set maxFramesPerChain <= maxStackDepth ("+itoa(stack)+")")
}

func GraphLimitsRespinsExceeded(path string, respins, limit int) ValidationIssue {
	return errIssue("GV-037", path,
		"initialRespins exceeds maxRespinsPerFeature",
		"Reduce initialRespins to "+itoa(limit)+" or raise runtime limit")
}

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	neg := n < 0
	if neg {
		n = -n
	}
	buf := make([]byte, 0, 12)
	for n > 0 {
		buf = append(buf, byte('0'+n%10))
		n /= 10
	}
	if neg {
		buf = append(buf, '-')
	}
	for i, j := 0, len(buf)-1; i < j; i, j = i+1, j-1 {
		buf[i], buf[j] = buf[j], buf[i]
	}
	return string(buf)
}

func itoa64(n int64) string {
	return itoa(int(n))
}
