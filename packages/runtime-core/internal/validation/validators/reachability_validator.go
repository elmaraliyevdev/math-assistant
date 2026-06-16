package validators

import "math-assistant/runtime-core/internal/domain"

// ValidateReachability checks orphan states, dead ends, and spawn/pop paths.
func ValidateReachability(game *domain.GameVersion) []Finding {
	var findings []Finding
	if game == nil || len(game.StateMachines) == 0 {
		return findings
	}
	reachable := computeReachableStates(game)
	for machineID, machine := range game.StateMachines {
		for stateID, state := range machine.States {
			if state.Deprecated {
				continue
			}
			key := machineID + "." + stateID
			if !reachable[key] {
				findings = append(findings, errFinding("GV-005",
					"stateMachines."+machineID+".states."+stateID,
					"state is unreachable from the session entry point",
					"Add transitions that reach this state or mark it deprecated"))
			}
			if !state.Terminal && len(state.Transitions) == 0 {
				findings = append(findings, errFinding("GV-006",
					"stateMachines."+machineID+".states."+stateID,
					"non-terminal state has no outgoing transitions",
					"Add transitions or mark the state terminal"))
			}
		}
	}
	for machineID, machine := range game.StateMachines {
		if !isSpawnTarget(game, machineID) {
			continue
		}
		if !hasPopPath(machine) {
			findings = append(findings, errFinding("GV-008",
				"stateMachines."+machineID,
				"spawned machine has no pop transition path to return to parent",
				"Add a FEATURE_COMPLETE transition with effect pop"))
		}
	}
	return findings
}

func computeReachableStates(game *domain.GameVersion) map[string]bool {
	reachable := make(map[string]bool)
	rootMachine := game.Session.RootMachineID
	rootMachineDef, ok := game.StateMachines[rootMachine]
	if !ok {
		return reachable
	}
	type frame struct {
		machineID string
		stateID   string
	}
	queue := []frame{{machineID: rootMachine, stateID: rootMachineDef.InitialStateID}}
	for len(queue) > 0 {
		cur := queue[0]
		queue = queue[1:]
		key := cur.machineID + "." + cur.stateID
		if reachable[key] {
			continue
		}
		reachable[key] = true
		machine := game.StateMachines[cur.machineID]
		state, ok := machine.States[cur.stateID]
		if !ok {
		 continue
		}
		for _, tr := range state.Transitions {
			switch tr.Effect {
			case "goto", "stay":
				if tr.TargetStateID != "" {
					queue = append(queue, frame{machineID: cur.machineID, stateID: tr.TargetStateID})
				}
			case "spawn":
				if tr.TargetMachineID == "" {
					continue
				}
				child, ok := game.StateMachines[tr.TargetMachineID]
				if !ok {
					continue
				}
				queue = append(queue, frame{machineID: child.ID, stateID: child.InitialStateID})
			}
		}
	}
	return reachable
}

func isSpawnTarget(game *domain.GameVersion, machineID string) bool {
	for _, machine := range game.StateMachines {
		for _, state := range machine.States {
			for _, tr := range state.Transitions {
				if tr.Effect == "spawn" && tr.TargetMachineID == machineID {
					return true
				}
			}
		}
	}
	return false
}

func hasPopPath(machine domain.StateMachine) bool {
	for _, state := range machine.States {
		for _, tr := range state.Transitions {
			if tr.Effect == "pop" {
				return true
			}
		}
	}
	return false
}
