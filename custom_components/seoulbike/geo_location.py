from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.const import UnitOfLength

from .const import DOMAIN, SUBENTRY_TYPE_STATION
from .entity import SeoulBikeEntity, async_setup_station_entities, station_attributes


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_setup_station_entities(
        coordinator, entry, async_add_entities, SeoulBikeGeoLocation
    )


class SeoulBikeGeoLocation(SeoulBikeEntity, GeolocationEvent):
    # state는 GeolocationEvent가 distance로 고정 (@final)
    # 지도 카드에서 geo_location_sources: [seoulbike] 로 전체 표시 가능
    _attr_source = DOMAIN
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:map-marker"

    def __init__(self, coordinator, subentry, station_id):

        super().__init__(coordinator, subentry, station_id)

        self._attr_unique_id = f"{subentry.subentry_id}_{station_id}"

        # 대여소 하위 항목은 기기 이름(대여소 이름)을 그대로 씀
        if subentry.subentry_type == SUBENTRY_TYPE_STATION:
            self._attr_name = None
            self._suggest_entity_id("geo_location")
        else:
            station = self.station
            self._attr_name = station.station_name if station else station_id
            self._suggest_entity_id("geo_location", self._station_key(station_id))

    @property
    def distance(self):
        return self.distance_km

    @property
    def latitude(self):
        station = self.station
        return station.lat if station else None

    @property
    def longitude(self):
        station = self.station
        return station.lon if station else None

    @property
    def extra_state_attributes(self):
        station = self.station

        if not station:
            return {}

        # source/latitude/longitude는 GeolocationEvent가 자동으로 추가
        return station_attributes(station, self.distance_km)

    @property
    def entity_picture(self):
        station = self.station
        return station.marker_svg if station else None
