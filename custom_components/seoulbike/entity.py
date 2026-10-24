from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    CONF_RADIUS_KM,
    CONF_STATION_ID,
    CONF_TOP_N,
    CONF_ZONE_ID,
    DEFAULT_RADIUS_KM,
    DEFAULT_TOP_N,
    SUBENTRY_TYPE_STATION,
    SUBENTRY_TYPE_ZONE,
    ZONE_HOME,
)


def station_attributes(station, distance_km):
    """대여소 엔티티들이 함께 쓰는 속성."""

    return {
        "station_id": station.station_id,
        "station_name": station.station_name,
        "distance_km": distance_km,
        "parking_bike_total_count": station.parking_bike_total_count,
        "rack_total_count": station.rack_total_count,
        "shared": station.shared,
        "availability_ratio": station.availability_ratio,
        "marker_color": station.marker_color,
    }


def find_zone_nearby(coordinator, subentry):
    """지역 하위 항목 설정대로 주변 대여소 목록. [(대여소, 거리km)]"""

    return coordinator.find_nearby(
        subentry.data[CONF_ZONE_ID],
        float(subentry.data.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)),
        int(subentry.data.get(CONF_TOP_N, DEFAULT_TOP_N)),
    )


def async_setup_station_entities(coordinator, entry, async_add_entities, entity_cls):
    """device_tracker·geo_location 공통 등록.

    대여소 하위 항목은 그 대여소 하나, 지역 하위 항목은 주변 대여소가
    새로 잡힐 때마다 엔티티를 추가한다.
    """

    for subentry in entry.subentries.values():

        if subentry.subentry_type == SUBENTRY_TYPE_STATION:
            async_add_entities(
                [entity_cls(coordinator, subentry, subentry.data[CONF_STATION_ID])],
                config_subentry_id=subentry.subentry_id,
            )

        elif subentry.subentry_type == SUBENTRY_TYPE_ZONE:
            _async_track_zone_stations(
                coordinator, entry, subentry, async_add_entities, entity_cls
            )


def _async_track_zone_stations(coordinator, entry, subentry, async_add_entities, entity_cls):

    known = set()

    def add_new_stations():

        new_entities = []

        for station, _ in find_zone_nearby(coordinator, subentry):

            if station.station_id in known:
                continue

            known.add(station.station_id)
            new_entities.append(entity_cls(coordinator, subentry, station.station_id))

        if new_entities:
            async_add_entities(new_entities, config_subentry_id=subentry.subentry_id)

    add_new_stations()
    entry.async_on_unload(coordinator.async_add_listener(add_new_stations))


class SeoulBikeEntity(CoordinatorEntity):
    """하위 항목(대여소/지역) 하나에 속한 엔티티의 공통 부분.

    하위 항목마다 기기 하나를 만든다.
    station_id가 있으면 그 대여소를 보여주는 엔티티다.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, subentry, station_id=None):

        super().__init__(coordinator)

        self._subentry = subentry
        self._station_id = station_id

        # 거리 기준: 지역 하위 항목은 그 지역, 대여소 하위 항목은 집
        self._zone_id = subentry.data.get(CONF_ZONE_ID, ZONE_HOME)

        # 엔티티 ID 앞부분: seoulbike_<대여소 번호> 또는 seoulbike_<지역>
        if subentry.subentry_type == SUBENTRY_TYPE_STATION:
            device_name = subentry.title
            model = "대여소"
            self._entity_id_base = f"{DOMAIN}_{self._station_key(subentry.data[CONF_STATION_ID])}"
        else:
            device_name = f"따릉이 {subentry.title}"
            model = "지역"
            self._entity_id_base = f"{DOMAIN}_{self._zone_id.split('.', 1)[1]}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=device_name,
            manufacturer="서울특별시",
            model=model,
            entry_type=DeviceEntryType.SERVICE,
        )

    def _station_key(self, station_id):
        """엔티티 ID에 쓸 대여소 번호. 번호를 못 찾으면 API ID (ST-3273 → st_3273)"""

        station = self.coordinator.get_station(station_id)
        number = station.station_number if station else None

        return number or slugify(station_id)

    def _suggest_entity_id(self, platform, *suffixes):
        """한글 이름 대신 영어 엔티티 ID로 고정.

        처음 등록할 때만 쓰이고, 이후에는 사용자가 바꾼 ID가 유지된다.
        """

        self.entity_id = f"{platform}.{'_'.join([self._entity_id_base, *suffixes])}"

    @property
    def station(self):
        return self.coordinator.get_station(self._station_id)

    @property
    def distance_km(self):
        return self.coordinator.distance_km(self._zone_id, self.station)

    @property
    def available(self):
        # 대여소가 API 목록에서 사라지면 사용 불가로 표시
        if self._station_id is None:
            return super().available

        return super().available and self.station is not None
