package validation

import (
	"math"
	"math-assistant/runtime-core/internal/domain"
)

var validCapScopes = map[string]struct{}{
	"session_spin_chain": {},
	"single_spin":        {},
	"feature":            {},
}

// ExposureValidator validates exposure caps in strict mode (MVP).
type ExposureValidator struct{}

// NewExposureValidator constructs an exposure validator.
func NewExposureValidator() *ExposureValidator {
	return &ExposureValidator{}
}

// Validate checks exposure configuration and theoretical max win vs caps.
func (v *ExposureValidator) Validate(game *domain.GameVersion) *ValidationReport {
	report := NewReport("")
	if game == nil {
		return report
	}
	exp := game.Exposure
	if exp.ValidationMode != "strict" {
		return report
	}
	if exp.EnforceCap && exp.MaxWinMinorUnits <= 0 {
		report.AddError(GraphExposureCapInvalid())
	}
	if exp.MaxWinMultiplier <= 0 && exp.EnforceCap {
		report.AddError(GraphExposureMultiplierInvalid())
	}
	if _, ok := validCapScopes[exp.CapScope]; !ok {
		report.AddError(GraphExposureScopeInvalid(exp.CapScope))
	}
	if !exp.EnforceCap {
		return report
	}
	theoretical := theoreticalMaxWinMinor(game)
	effectiveCap := effectiveExposureCap(game)
	if effectiveCap > 0 && theoretical > effectiveCap {
		report.AddError(GraphExposureCapExceeded(theoretical, effectiveCap))
	}
	return report
}

func effectiveExposureCap(game *domain.GameVersion) int64 {
	exp := game.Exposure
	cap := int64(exp.MaxWinMinorUnits)
	totalBet := totalBetMinor(game)
	if exp.MaxWinMultiplier > 0 && totalBet > 0 {
		multCap := int64(exp.MaxWinMultiplier) * totalBet
		if cap == 0 || multCap < cap {
			cap = multCap
		}
	}
	return cap
}

func totalBetMinor(game *domain.GameVersion) int64 {
	bet := game.BetModel
	if bet.TotalBetMinorUnits > 0 {
		return int64(bet.TotalBetMinorUnits)
	}
	lines := bet.LineCount
	if lines <= 0 {
		lines = 1
	}
	scale := bet.CoinValueScale
	if scale <= 0 {
		scale = 1
	}
	coin := bet.DefaultCoinValue
	if coin <= 0 {
		coin = 1
	}
	return int64(lines * coin * scale)
}

func theoreticalMaxWinMinor(game *domain.GameVersion) int64 {
	var maxPaytable int64
	for _, pay := range game.Paytable.Pays {
		mult := payMultiplier(pay.Multiplier)
		win := mult * totalBetMinor(game)
		if win > maxPaytable {
			maxPaytable = win
		}
	}
	jackpotMax := maxJackpotMinor(game)
	if jackpotMax > maxPaytable {
		return jackpotMax
	}
	return maxPaytable
}

func payMultiplier(v any) int64 {
	switch n := v.(type) {
	case float64:
		return int64(math.Round(n))
	case int:
		return int64(n)
	case int64:
		return n
	default:
		return 0
	}
}

func maxJackpotMinor(game *domain.GameVersion) int64 {
	var max int64
	for _, machine := range game.StateMachines {
		for _, state := range machine.States {
			cfg := state.PluginConfig
			if cfg == nil {
				continue
			}
			tiers, ok := cfg["jackpotTiers"].(map[string]any)
			if !ok {
				continue
			}
			for _, val := range tiers {
				mult := payMultiplier(val)
				win := mult * totalBetMinor(game)
				if win > max {
					max = win
				}
			}
		}
	}
	return max
}
