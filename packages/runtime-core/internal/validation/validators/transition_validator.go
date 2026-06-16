package validators

import "math-assistant/runtime-core/internal/domain"

// ValidateTransitions checks transition targets, pop rules, and priority metadata.
func ValidateTransitions(game *domain.GameVersion, tiers *PriorityTierRegistry) []Finding {
	var findings []Finding
	if game == nil {
		return findings
	}
	for machineID, machine := range game.StateMachines {
		for stateID, state := range machine.States {
			seenTransitionIDs := make(map[string]bool)
			for _, tr := range state.Transitions {
				if seenTransitionIDs[tr.ID] {
					findings = append(findings, errFinding("GV-013",
						"stateMachines."+machineID+".states."+stateID+".transitions",
						"duplicate transition id '"+tr.ID+"' within state",
						"Assign unique transition ids per state"))
				}
				seenTransitionIDs[tr.ID] = true
				path := transitionPath(machineID, stateID, tr.ID)
				switch tr.Effect {
				case "goto", "stay":
					if tr.TargetStateID == "" {
						continue
					}
					if _, ok := machine.States[tr.TargetStateID]; !ok {
						findings = append(findings, errFinding("GV-003", path,
							"transition target state '"+tr.TargetStateID+"' does not exist in machine '"+machineID+"'",
							"Point targetStateId to an existing state or remove the transition"))
					}
				case "spawn":
					if tr.TargetMachineID == "" {
						continue
					}
					if _, ok := game.StateMachines[tr.TargetMachineID]; !ok {
						findings = append(findings, errFinding("GV-004", path,
							"spawn target machine '"+tr.TargetMachineID+"' does not exist",
							"Define the nested machine or fix targetMachineId"))
					}
				case "pop":
					if tr.TargetStateID != "" || tr.TargetMachineID != "" {
						findings = append(findings, errFinding("GV-010", path,
							"pop effect must not specify targetStateId or targetMachineId",
							"Remove target fields from pop transitions"))
					}
				}
				if tiers != nil {
					findings = append(findings, validatePriorityTier(tiers, path, tr)...)
				}
			}
			findings = append(findings, validateTransitionConflicts(game, machineID, stateID, state)...)
		}
	}
	return findings
}

func transitionPath(machineID, stateID, transitionID string) string {
	return "stateMachines." + machineID + ".states." + stateID + ".transitions." + transitionID
}

func validatePriorityTier(tiers *PriorityTierRegistry, path string, tr domain.Transition) []Finding {
	if tr.PriorityTier == "" {
		return []Finding{warnFinding("GV-028", path,
			"transition is missing priorityTier",
			"Set priorityTier to a registered tier for deterministic ordering")}
	}
	tier, ok := tiers.Resolve(tr.PriorityTier)
	if !ok {
		return []Finding{errFinding("GV-027", path,
			"unknown priorityTier '"+tr.PriorityTier+"'",
			"Use a tier from priority-tiers-v1.json")}
	}
	if tr.Priority != tier.DefaultPriority {
		if tr.Priority < tier.RangeMin || tr.Priority > tier.RangeMax {
			return []Finding{errFinding("GV-027", path,
				"priority is outside allowed range for tier '"+tier.ID+"'",
				"Set priority within the tier numericRange or use defaultPriority")}
		}
	}
	return nil
}

func validateTransitionConflicts(
	game *domain.GameVersion,
	machineID, stateID string,
	state domain.State,
) []Finding {
	var findings []Finding
	type key struct {
		trigger  string
		priority int
		tier     string
	}
	groups := make(map[key][]domain.Transition)
	for _, tr := range state.Transitions {
		k := key{trigger: tr.Trigger, priority: tr.Priority, tier: tr.PriorityTier}
		groups[k] = append(groups[k], tr)
	}
	for k, group := range groups {
		if len(group) > 1 {
			findings = append(findings, warnFinding("GV-016",
				"stateMachines."+machineID+".states."+stateID+".transitions",
				"multiple transitions share trigger '"+k.trigger+"' with identical priority and tier",
				"Differentiate priority or priorityTier to resolve ambiguity"))
			if !resolvableByPrecedence(game, group) {
				findings = append(findings, errFinding("GV-017",
					"stateMachines."+machineID+".states."+stateID+".transitions",
					"ambiguous transition set for trigger '"+k.trigger+"' cannot be resolved by precedence",
					"Adjust priorities or precedence.triggerOrder"))
			}
		}
	}
	return findings
}

func resolvableByPrecedence(game *domain.GameVersion, transitions []domain.Transition) bool {
	if len(transitions) <= 1 {
		return true
	}
	order := game.Precedence.TriggerOrder
	if len(order) == 0 {
		return false
	}
	rank := make(map[string]int, len(order))
	for i, t := range order {
		rank[t] = i
	}
	bestRank := len(order) + 1
	for _, tr := range transitions {
		r, ok := rank[tr.Trigger]
		if !ok {
			return false
		}
		if r < bestRank {
			bestRank = r
		}
	}
	countBest := 0
	for _, tr := range transitions {
		if rank[tr.Trigger] == bestRank {
			countBest++
		}
	}
	return countBest == 1
}
