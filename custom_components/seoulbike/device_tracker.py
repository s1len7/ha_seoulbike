from homeassistant.components.device_tracker import SourceType, TrackerEntity

from .const import DOMAIN, SUBENTRY_TYPE_STATION
from .entity import SeoulBikeEntity, async_setup_station_entities, station_attributes


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_setup_station_entities(
        coordinator, entry, async_add_entities, SeoulBikeTracker
    )


class SeoulBikeTracker(SeoulBikeEntity, TrackerEntity):

    _attr_icon = "mdi:bicycle"
    _attr_source_type = SourceType.GPS

    def __init__(self, coordinator, subentry, station_id):

        super().__init__(coordinator, subentry, station_id)

        self._attr_unique_id = f"{subentry.subentry_id}_{station_id}"

        # 대여소 하위 항목은 기기 이름(대여소 이름)을 그대로 씀
        if subentry.subentry_type == SUBENTRY_TYPE_STATION:
            self._attr_name = None
            self._suggest_entity_id("device_tracker")
        else:
            station = self.station
            self._attr_name = station.station_name if station else station_id
            self._suggest_entity_id("device_tracker", self._station_key(station_id))

    @property
    def latitude(self):
        station = self.station
        return station.lat if station else None

    @property
    def longitude(self):
        station = self.station
        return station.lon if station else None

    @property
    def state(self):
        station = self.station
        return station.parking_bike_total_count if station else 0

    @property
    def extra_state_attributes(self):
        station = self.station
        return station_attributes(station, self.distance_km) if station else {}

    @property
    def entity_picture(self):
        station = self.station
        return station.marker_svg if station else None
