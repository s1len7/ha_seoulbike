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
CONF_STATION_ID = "station_id"
CONF_ZONE_ID = "zone_id"

# 하위 항목 종류: 고정 대여소 / 지역 주변 대여소 자동 탐색
SUBENTRY_TYPE_STATION = "station"
SUBENTRY_TYPE_ZONE = "zone"

ZONE_HOME = "zone.home"

DEFAULT_RADIUS_KM = 0.5
DEFAULT_TOP_N = 3

RADIUS_KM_MIN = 0.1
RADIUS_KM_MAX = 5.0

TOP_N_MIN = 1
TOP_N_MAX = 9
