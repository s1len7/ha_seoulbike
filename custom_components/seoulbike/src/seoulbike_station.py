from dataclasses import dataclass

from .marker import build_marker_svg, get_availability_marker


@dataclass(slots=True)
class SeoulBikeStation:
    station_id: str
    station_name: str
    lat: float
    lon: float
    rack_total_count: int
    parking_bike_total_count: int
    shared: int
    distance_km: float = 0.0  # runtime value

    @property
    def availability_ratio(self) -> float | None:
        if self.rack_total_count <= 0:
            return None

        return self.parking_bike_total_count / self.rack_total_count

    @property
    def marker_color(self) -> str:
        return get_availability_marker(self.availability_ratio)[0]

    @property
    def marker_svg(self) -> str:
        return build_marker_svg(
            self.availability_ratio,
            self.parking_bike_total_count,
        )