import re
from dataclasses import dataclass

from .marker import build_marker_svg, get_availability_marker

# 대여소 이름 앞의 번호 ("5778. 북위례3" → "5778")
_STATION_NUMBER_RE = re.compile(r"^\s*(\d+)\s*\.")


@dataclass(slots=True)
class SeoulBikeStation:
    station_id: str
    station_name: str
    lat: float
    lon: float
    rack_total_count: int
    parking_bike_total_count: int
    shared: int

    @property
    def station_number(self) -> str | None:
        match = _STATION_NUMBER_RE.match(self.station_name or "")
        return match.group(1) if match else None

    @property
    def availability_ratio(self) -> float | None:
        if self.rack_total_count <= 0:
            return None

        return self.parking_bike_total_count / self.rack_total_count

    @property
    def marker_color(self) -> str:
        return get_availability_marker(self.availability_ratio)

    @property
    def marker_svg(self) -> str:
        return build_marker_svg(
            self.availability_ratio,
            self.parking_bike_total_count,
        )