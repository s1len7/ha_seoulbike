# 🚲 따릉이(Seoul Bike) for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![Release](https://img.shields.io/github/v/release/s1len7/ha_seoulbike)](https://github.com/s1len7/ha_seoulbike/releases)

서울시 공공자전거 따릉이의 실시간 대여 정보를 Home Assistant에서 보여주는 커스텀 통합입니다.
자주 쓰는 대여소의 자전거 수를 센서로 보고, 집이나 회사 주변 대여소를 지도에 표시할 수 있습니다.

![Seoul Bike](https://play-lh.googleusercontent.com/fDnBp9mmuZ4Fk0g6Rlg1Nd-ZRGkWX3_-kGDrBnKZtHwaPVtGUlwvvAFHtQn9RkNa3vR4bSa_FdjkM5xtbZ-EPA)

## 기능

- **대여소 고정**: 대여소를 골라 대여 가능 자전거 수, 거치대 수, 집에서의 거리를 센서로 받습니다
- **지역 주변 자동 탐색**: 지역(zone)을 고르면 반경 안의 대여소를 가까운 순으로 찾아 줍니다
- **지도 표시**: 대여소마다 자전거 수가 적힌 마커를 지도에 표시합니다 (초록: 여유 / 주황: 30% 이하 / 빨강: 0대)
- **API 키 관리**: API 키가 무효해지면 HA가 재인증 알림을 띄우고, 통합 화면에서 키만 바꿀 수도 있습니다
- 1분마다 갱신되고, 대여소·지역을 여러 개 추가해도 API 호출 수는 늘지 않습니다 (한 번에 전체 대여소를 받아 함께 씀)

## 요구 사항

- Home Assistant 2026.6.0 이상
- [서울 열린데이터광장](https://data.seoul.go.kr) 인증키 (무료)

## 설치

### 1. HACS로 설치

[![HACS 저장소 열기](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=s1len7&repository=ha_seoulbike&category=integration)

버튼이 동작하지 않으면 직접 추가합니다.

1. HACS → 오른쪽 위 ⋮ → **사용자 지정 저장소**
2. 저장소 `https://github.com/s1len7/ha_seoulbike`, 유형 **Integration**으로 추가
3. 목록에서 **따릉이(Seoul Bike)** 를 설치하고 Home Assistant를 재시작

### 2. API 인증키 발급

1. [서울 열린데이터광장](https://data.seoul.go.kr)에 회원가입·로그인
2. [인증키 신청 페이지](https://data.seoul.go.kr/together/mypage/actkeyMain.do)에서 일반 인증키를 발급
3. 사용하는 데이터: [서울시 공공자전거 실시간 대여정보](https://data.seoul.go.kr/dataList/OA-15493/A/1/datasetView.do)

### 3. 통합 추가

[![통합 추가](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=seoulbike)

1. **설정 → 기기 및 서비스 → 통합 추가 → 따릉이(Seoul Bike)**
2. API 인증키를 입력합니다 (입력 즉시 실제 API로 확인합니다)
3. 통합 화면에서 **대여소 추가** 또는 **지역 추가**를 누릅니다

| 추가 항목 | 입력 | 용도 |
|---|---|---|
| 대여소 | 대여소 (집에서 가까운 순 목록) | 매일 쓰는 대여소를 고정해서 볼 때 |
| 지역 | 지역(zone), 검색 반경(0.1~5km), 최대 대여소 수(1~9) | 집·회사 주변에서 자전거 있는 곳을 찾을 때 |

대여소와 지역은 여러 개 추가할 수 있고, 하나마다 기기가 하나씩 생깁니다.

## 엔티티

### 대여소

`5778. 북위례3` 대여소를 추가한 경우입니다. 엔티티 ID에는 대여소 번호가 들어갑니다.

| 엔티티 | 상태 | 설명 |
|---|---|---|
| `sensor.seoulbike_5778_bikes` | `12` 대 | 대여 가능 자전거 |
| `sensor.seoulbike_5778_racks` | `15` 개 | 거치대 |
| `sensor.seoulbike_5778_distance` | `0.40` km | 집(`zone.home`)에서의 거리 |
| `device_tracker.seoulbike_5778` | `12` | 지도 표시 (상태 = 대여 가능 자전거) |
| `geo_location.seoulbike_5778` | `0.4` km | 지도 표시 (상태 = 거리) |

### 지역

`zone.home`을 추가한 경우입니다. 엔티티 ID에는 지역 이름(`home`)이 들어갑니다.

| 엔티티 | 상태 | 설명 |
|---|---|---|
| `sensor.seoulbike_home_nearest_station` | `5778. 북위례3` | 가장 가까운 대여소 |
| `sensor.seoulbike_home_nearby_stations` | `1` 곳 | 반경 안의 대여소 수 (속성 `stations`에 목록) |
| `device_tracker.seoulbike_home_<대여소 번호>` | 자전거 수 | 반경 안의 대여소마다 하나 |
| `geo_location.seoulbike_home_<대여소 번호>` | 거리 km | 반경 안의 대여소마다 하나 |

### 대여소 속성

대여 가능 자전거 센서, 가장 가까운 대여소 센서, 지도 엔티티에 들어 있습니다.

| 속성 | 설명 |
|---|---|
| `station_id` | API 대여소 ID (`ST-3273`) |
| `station_name` | 대여소 이름 |
| `distance_km` | 기준 지역에서의 거리 (km) |
| `parking_bike_total_count` | 대여 가능 자전거 |
| `rack_total_count` | 거치대 |
| `shared` | 거치율 (%) |
| `availability_ratio` | 대여 가능 자전거 ÷ 거치대 |
| `marker_color` | 지도 마커 색 |

## 사용 예시

### 대시보드

```yaml
type: tile
entity: sensor.seoulbike_5778_bikes
```

추가한 대여소와 지역 주변 대여소를 모두 지도에 표시합니다.

```yaml
type: map
geo_location_sources:
  - seoulbike
entities:
  - zone.home
```

### 자동화

출근 전에 집 앞 대여소의 자전거가 2대 미만이면 알림을 보냅니다.

```yaml
alias: 출근 전 따릉이 확인
triggers:
  - trigger: time
    at: "08:00:00"
conditions:
  - condition: numeric_state
    entity_id: sensor.seoulbike_5778_bikes
    below: 2
actions:
  - action: notify.notify
    data:
      message: "집 앞 따릉이가 {{ states('sensor.seoulbike_5778_bikes') }}대 남았습니다."
```

## API 키 변경

- **키가 무효해진 경우**: HA가 **재인증 필요** 알림을 띄웁니다. 알림을 눌러 새 키를 입력합니다
- **직접 바꾸는 경우**: 통합 화면 ⋮ → **재구성**에서 새 키를 입력합니다

어느 쪽이든 추가한 대여소·지역과 엔티티는 그대로 유지됩니다.

## 문제 해결

디버그 로그를 켜려면 `configuration.yaml`에 추가하고 재시작합니다.

```yaml
logger:
  logs:
    custom_components.seoulbike: debug
```

문제가 있으면 [GitHub 이슈](https://github.com/s1len7/ha_seoulbike/issues)에 로그와 함께 남겨 주세요.
로그를 올리기 전에 API 키가 들어 있지 않은지 확인해 주세요.
