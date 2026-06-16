package validators

import "math-assistant/runtime-core/internal/domain"

// ValidateProgression detects infinite loops in states without terminating progression.
func ValidateProgression(game *domain.GameVersion) []Finding {
	var findings []Finding
	if game == nil {
		return findings
	}
	for machineID, machine := range game.StateMachines {
		for stateID, state := range machine.States {
			if state.Terminal {
				continue
			}
			if state.StateType != "multi_step" {
				continue
			}
			if state.Progression != nil && state.Progression.TerminatesWhen != "" {
				continue
			}
			if hasSelfStayLoop(machine, stateID) {
				findings = append(findings, errFinding("GV-011",
					"stateMachines."+machineID+".states."+stateID,
					"infinite progression loop detected without terminating progression metadata",
					"Add progression metadata or a terminating transition"))
			}
		}
	}
	return findings
}

func hasSelfStayLoop(machine domain.StateMachine, stateID string) bool {
	state, ok := machine.States[stateID]
	if !ok {
		return false
	}
	for _, tr := range state.Transitions {
		if tr.Effect == "stay" && tr.TargetStateID == stateID {
			hasExit := false
			for _, other := range state.Transitions {
				if other.Effect != "stay" || other.TargetStateID != stateID {
					hasExit = true
					break
				}
			}
			if !hasExit {
				return true
			}
		}
	}
	return false
}
