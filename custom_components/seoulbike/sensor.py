import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength

from .const import DOMAIN, CONF_STATION_ID, SUBENTRY_TYPE_STATION, SUBENTRY_TYPE_ZONE
from .entity import SeoulBikeEntity, find_zone_nearby, station_attributes

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    for subentry in entry.subentries.values():

        if subentry.subentry_type == SUBENTRY_TYPE_STATION:
            station_id = subentry.data[CONF_STATION_ID]
            entities = [
                SeoulBikeBikesSensor(coordinator, subentry, station_id),
                SeoulBikeRacksSensor(coordinator, subentry, station_id),
                SeoulBikeDistanceSensor(coordinator, subentry, station_id),
            ]

        elif subentry.subentry_type == SUBENTRY_TYPE_ZONE:
            entities = [
                SeoulBikeNearestStation(coordinator, subentry),
                SeoulBikeNearbyStations(coordinator, subentry),
            ]

        else:
            continue

        async_add_entities(entities, config_subentry_id=subentry.subentry_id)


class SeoulBikeBikesSensor(SeoulBikeEntity, SensorEntity):

    _attr_name = "대여 가능 자전거"
    _attr_icon = "mdi:bicycle"
    _attr_native_unit_of_measurement = "대"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, subentry, station_id):

        super().__init__(coordinator, subentry, station_id)

        self._attr_unique_id = f"{subentry.subentry_id}_parking_bike_total_count"
        self._suggest_entity_id("sensor", "bikes")

    @property
    def native_value(self):
        station = self.station
        return station.parking_bike_total_count if station else None

    @property
    def extra_state_attributes(self):
        station = self.station
        return station_attributes(station, self.distance_km) if station else {}


class SeoulBikeRacksSensor(SeoulBikeEntity, SensorEntity):

    _attr_name = "거치대"
    _attr_icon = "mdi:parking"
    _attr_native_unit_of_measurement = "개"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, subentry, station_id):

        super().__init__(coordinator, subentry, station_id)

        self._attr_unique_id = f"{subentry.subentry_id}_rack_total_count"
        self._suggest_entity_id("sensor", "racks")

    @property
    def native_value(self):
        station = self.station
        return station.rack_total_count if station else None


class SeoulBikeDistanceSensor(SeoulBikeEntity, SensorEntity):

    _attr_name = "거리"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, subentry, station_id):

        super().__init__(coordinator, subentry, station_id)

        self._attr_unique_id = f"{subentry.subentry_id}_distance"
        self._suggest_entity_id("sensor", "distance")

    @property
    def native_value(self):
        return self.distance_km


class SeoulBikeNearestStation(SeoulBikeEntity, SensorEntity):

    _attr_name = "가장 가까운 대여소"
    _attr_icon = "mdi:map-marker-radius"

    def __init__(self, coordinator, subentry):

        super().__init__(coordinator, subentry)

        self._attr_unique_id = f"{subentry.subentry_id}_nearest_station"
        self._suggest_entity_id("sensor", "nearest_station")

    def _nearest(self):
        nearby = find_zone_nearby(self.coordinator, self._subentry)
        return nearby[0] if nearby else None

    @property
    def native_value(self):
        nearest = self._nearest()
        return nearest[0].station_name if nearest else None

    @property
    def extra_state_attributes(self):
        nearest = self._nearest()
        return station_attributes(*nearest) if nearest else {}


class SeoulBikeNearbyStations(SeoulBikeEntity, SensorEntity):

    _attr_name = "주변 대여소"
    _attr_icon = "mdi:format-list-bulleted"
    _attr_native_unit_of_measurement = "곳"

    def __init__(self, coordinator, subentry):

        super().__init__(coordinator, subentry)

        self._attr_unique_id = f"{subentry.subentry_id}_nearby_stations"
        self._suggest_entity_id("sensor", "nearby_stations")

    @property
    def native_value(self):
        return len(find_zone_nearby(self.coordinator, self._subentry))

    @property
    def extra_state_attributes(self):
        return {
            "stations": [
                station_attributes(station, dist)
                for station, dist in find_zone_nearby(self.coordinator, self._subentry)
            ]
        }
