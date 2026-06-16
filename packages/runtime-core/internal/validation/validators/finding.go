package validators

// Finding is a validation result produced by graph sub-validators.
type Finding struct {
	Code       string
	Severity   string // "error" or "warning"
	Path       string
	Message    string
	Suggestion string
}

func errFinding(code, path, message, suggestion string) Finding {
	return Finding{Code: code, Severity: "error", Path: path, Message: message, Suggestion: suggestion}
}

func warnFinding(code, path, message, suggestion string) Finding {
	return Finding{Code: code, Severity: "warning", Path: path, Message: message, Suggestion: suggestion}
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
