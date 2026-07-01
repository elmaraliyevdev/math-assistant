"""Built-in constraint presets."""

from __future__ import annotations

from typing import Any

BUILTIN_PRESETS: list[dict[str, Any]] = [
    {
        "id": "generic",
        "name": "Generic",
        "description": "Balanced scatter spacing and wild separation.",
        "builtIn": True,
        "document": {
            "version": 1,
            "edgeWrapping": True,
            "groups": [],
            "inventory": {},
            "constraints": [
                {
                    "id": "generic-scatter-min",
                    "type": "min_count",
                    "enabled": True,
                    "description": "Scatter minimum across reels",
                    "targetType": "group",
                    "targetId": "scatter",
                    "value": 3,
                    "scope": "global",
                    "severity": "error",
                }
            ],
        },
    },
    {
        "id": "high_volatility",
        "name": "High Volatility",
        "description": "Tighter feature spacing.",
        "builtIn": True,
        "document": {
            "version": 1,
            "edgeWrapping": True,
            "groups": [],
            "inventory": {},
            "constraints": [
                {
                    "id": "hv-scatter-max-consecutive",
                    "type": "max_consecutive",
                    "enabled": True,
                    "description": "Scatter max consecutive",
                    "targetType": "group",
                    "targetId": "scatter",
                    "value": 1,
                    "scope": "global",
                    "severity": "error",
                }
            ],
        },
    },
]
