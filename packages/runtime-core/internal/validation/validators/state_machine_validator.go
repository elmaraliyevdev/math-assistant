package validators

import "math-assistant/runtime-core/internal/domain"

// ValidateStateMachines checks machine identity, initial states, and duplicate ids.
func ValidateStateMachines(game *domain.GameVersion) []Finding {
	var findings []Finding
	if game == nil {
		return findings
	}
	seenMachines := make(map[string]string)
	for key, machine := range game.StateMachines {
		if existingKey, ok := seenMachines[machine.ID]; ok && existingKey != key {
			findings = append(findings, errFinding("GV-015", "stateMachines",
				"duplicate state machine id '"+machine.ID+"'",
				"Ensure machine map keys match unique machine ids"))
		}
		seenMachines[machine.ID] = key
		if machine.ID != key {
			findings = append(findings, errFinding("GV-015", "stateMachines",
				"duplicate state machine id '"+key+"'",
				"Ensure machine map keys match unique machine ids"))
		}
		if machine.InitialStateID == "" {
			findings = append(findings, errFinding("GV-001", "stateMachines."+machine.ID,
				"state machine must have exactly one initial state",
				"Set initialStateId to a single defined state"))
			continue
		}
		if _, ok := machine.States[machine.InitialStateID]; !ok {
			findings = append(findings, errFinding("GV-001",
				"stateMachines."+machine.ID+".initialStateId",
				"initial state '"+machine.InitialStateID+"' is not defined in states map",
				"Define the initial state or update initialStateId"))
		}
		seenStates := make(map[string]bool)
		for stateKey, state := range machine.States {
			if state.ID != stateKey {
				findings = append(findings, errFinding("GV-014",
					"stateMachines."+machine.ID+".states",
					"duplicate state id '"+stateKey+"'",
					"Ensure state map keys match unique state ids"))
			}
			if seenStates[state.ID] {
				findings = append(findings, errFinding("GV-014",
					"stateMachines."+machine.ID+".states",
					"duplicate state id '"+state.ID+"'",
					"Ensure state map keys match unique state ids"))
			}
			seenStates[state.ID] = true
		}
	}
	root := game.Session.RootMachineID
	if root != "" {
		if _, ok := game.StateMachines[root]; !ok {
			findings = append(findings, errFinding("GV-002", "session.rootMachineId",
				"root machine '"+root+"' does not exist in stateMachines",
				"Set rootMachineId to an existing state machine id"))
		}
	}
	return findings
}
