# 개발

따릉이(Seoul Bike) 통합을 개발할 때 필요한 내용입니다. 설치·사용 방법은 [README](../README.md)를 참고하세요.

## 구조

```text
custom_components/seoulbike/
├── manifest.json        # 도메인·버전의 단일 출처 (const.py가 읽어감)
├── const.py             # 설정 키, 하위 항목 종류, 기본값
├── __init__.py          # 설정 항목 로드/언로드, 플랫폼 등록, 버전 마이그레이션
├── config_flow.py       # API 키 입력·재인증·재구성, 하위 항목(대여소/지역) 추가
├── coordinator.py       # 60초마다 전체 대여소 조회 (모든 하위 항목이 공유), 거리·주변 탐색
├── entity.py            # 하위 항목 공통 엔티티(기기 하나), 대여소 속성, 지도 엔티티 등록
├── sensor.py            # 대여소: 대여 가능·거치대·거리 / 지역: 가장 가까운·주변 대여소
├── device_tracker.py    # 대여소 지도 표시 (state = 자전거 수)
├── geo_location.py      # 대여소 지도 표시 (state = 거리 km, 고정)
├── src/
│   ├── seoul_api.py         # 서울 열린데이터광장 공통 클라이언트, SeoulApiError·SeoulApiAuthError
│   ├── seoul_bike_api.py    # bikeList 서비스 (따릉이)
│   ├── seoulbike_station.py # 대여소 데이터 클래스
│   └── marker.py            # 지도 마커 SVG
└── translations/ko.json # 설정 화면·에러 문구
```

설정 항목 하나가 API 키를 갖고, 대여소·지역은 그 아래 하위 항목(config subentry)으로 추가합니다.

```text
SeoulBike (설정 항목: API 키)
 ├─ 대여소 하위 항목: 대여소 하나 고정 (거리 기준은 zone.home)
 └─ 지역 하위 항목: 지역(zone) 주변 반경 안의 대여소를 가까운 순으로 자동 탐색
```

## 개발 환경

개발용 Home Assistant를 Docker로 띄우고, 이 저장소의 통합 폴더를 컨테이너에 그대로 연결합니다.
VS Code 작업(`.vscode/tasks.json`)은 저장소 옆의 `ha-dev` 폴더를 사용합니다.

```text
~/
├── ha_seoulbike/   # 이 저장소
└── ha-dev/
    ├── docker-compose.yml
    └── config/     # HA 설정 폴더
```

`ha-dev/docker-compose.yml`:

```yaml
services:
  homeassistant:
    container_name: ha-dev
    image: ghcr.io/home-assistant/home-assistant:stable
    ports:
      - "8123:8123"
      - "2015:2015"   # 디버거
    privileged: true
    restart: unless-stopped
    environment:
      TZ: Asia/Seoul
    volumes:
      - ./config:/config
      - ../ha_seoulbike/custom_components/seoulbike:/config/custom_components/seoulbike
```

| 항목 | 값 |
|---|---|
| 웹 UI | http://localhost:8123 |
| 로그 | `ha-dev/config/home-assistant.log` |
| 엔티티 등록 정보 | `ha-dev/config/.storage/core.entity_registry` |
| 엔티티 상태 기록 | `ha-dev/config/home-assistant_v2.db` (recorder) |
| HA 소스 (컨테이너 안) | `/usr/src/homeassistant/homeassistant/` |

```bash
cd ~/ha-dev
docker compose up -d                          # 시작
docker compose restart homeassistant          # 코드 수정 후 반영
docker compose logs --since 5m homeassistant 2>&1 | grep -i seoulbike
```

VS Code에서는 **작업 실행**의 `HA Start`, `HA Restart`, `HA Stop`, `HA Logs`로 같은 일을 할 수 있습니다.
Windows의 Docker Desktop을 WSL에서 쓰려면 Docker Desktop 설정에서 WSL 통합을 켜야 합니다.

## 디버깅

HA 내장 디버거 통합을 개발용 HA의 `configuration.yaml`에서 켭니다.

```yaml
debugpy:
  host: 0.0.0.0
  port: 2015
```

HA를 재시작한 뒤 VS Code의 **Attach HA Debug** (`.vscode/launch.json`)로 접속합니다.
