from __future__ import annotations

import json
from pathlib import Path

_manifest = json.loads(
    (Path(__file__).parent / "manifest.json").read_text(encoding="utf-8")
)

DOMAIN: str = _manifest["domain"]

CONF_API_KEY = "seoul_api_key"
CONF_RADIUS_KM = "radius_km"
CONF_TOP_N = "top_n"

DEFAULT_RADIUS_KM = 0.5
DEFAULT_TOP_N = 3

TOP_N_MIN = 1
TOP_N_MAX = 9

