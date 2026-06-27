class SeoulBikeNearestStationTracker(TrackerEntity, CoordinatorEntity):

    def __init__(self, coordinator):
        CoordinatorEntity.__init__(self, coordinator)

        self._attr_unique_id = f"{DOMAIN}.device_tracker.nearest_station"
        self._attr_name = self._attr_unique_id
        self._attr_icon = "mdi:bicycle"

    # 📍 위치
    @property
    def latitude(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})
        return nearest.get("lat")

    @property
    def longitude(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})
        return nearest.get("lon")

    # 📌 상태 = 잔여 자전거 수 (마커 숫자)
    @property
    def state(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})

        try:
            bikes = int(nearest.get("bikes") or 0)
            return max(bikes, 0)
        except (TypeError, ValueError):
            return 0

    # 📌 popup 정보
    @property
    def extra_state_attributes(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})

        return {
            "station_id": nearest.get("station_id"),
            "name": nearest.get("name"),
            "distance_km": nearest.get("distance_km"),
            "bikes": nearest.get("bikes"),
            "racks": nearest.get("racks"),
            "availability_ratio": nearest.get("availability_ratio"),
            "latitude": nearest.get("lat"),
            "longitude": nearest.get("lon"),
        }

    @property
    def source_type(self):
        return "gps"

    # 🚲 핵심: 마커 아이콘 + 상태별 색상
    @property
    def entity_picture(self):
        nearest = (self.coordinator.data or {}).get("nearest", {})

        try:
            bikes = int(nearest.get("bikes") or 0)
        except (TypeError, ValueError):
            bikes = 0

        # 🎯 기본: 심플한 라인 자전거 (고정)
        base_icon = "https://cdn.jsdelivr.net/npm/lucide-static/icons/bike.svg"
        return base_icon
        # # 🔴 없음 → 빨간 느낌 (SVG 자체가 아니라 테두리 느낌용 교체)
        # if bikes == 0:
        #     return base_icon

        # # 🟠 부족
        # elif bikes <= 3:
        #     return base_icon

        # # 🟢 충분
        # else:
        #     return base_icon