package validators

import "math-assistant/runtime-core/internal/domain"

// ValidateStackDepth ensures worst-case spawn nesting fits session.maxStackDepth.
func ValidateStackDepth(game *domain.GameVersion) []Finding {
	var findings []Finding
	if game == nil {
		return findings
	}
	root := game.Session.RootMachineID
	if root == "" {
		return findings
	}
	worst := worstCaseStackDepth(game, root, make(map[string]int))
	limit := game.Session.MaxStackDepth
	if limit <= 0 {
		limit = 8
	}
	if worst > limit {
		findings = append(findings, errFinding("GV-012", "session.maxStackDepth",
			"worst-case spawn stack depth exceeds maxStackDepth",
			"Increase maxStackDepth or reduce nested spawn depth (worst case: "+itoa(worst)+", limit: "+itoa(limit)+")"))
	}
	return findings
}

func worstCaseStackDepth(game *domain.GameVersion, machineID string, memo map[string]int) int {
	if d, ok := memo[machineID]; ok {
		return d
	}
	machine, ok := game.StateMachines[machineID]
	if !ok {
		memo[machineID] = 1
		return 1
	}
	maxChildDepth := 0
	for _, state := range machine.States {
		for _, tr := range state.Transitions {
			if tr.Effect != "spawn" || tr.TargetMachineID == "" {
				continue
			}
			childDepth := worstCaseStackDepth(game, tr.TargetMachineID, memo)
			if childDepth > maxChildDepth {
				maxChildDepth = childDepth
			}
		}
	}
	depth := 1
	if maxChildDepth > 0 {
		depth = 1 + maxChildDepth
	}
	memo[machineID] = depth
	return depth
}
