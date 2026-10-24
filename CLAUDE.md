# CLAUDE 지시사항

## 공통

### 기본 원칙

- 언제나 환각(hallucination)을 발생시키지 말 것
- 모든 수정은 요청한 범위만 하고, 불필요한 수정은 최대한 피할 것
  - 작업 중 발견한 다른 문제는 고치지 말고 보고만 할 것
  - 커밋·푸시는 요청받았을 때만 할 것
  - git 히스토리 재작성, 강제 푸시처럼 되돌리기 어려운 작업은 요청받았더라도 실행 전에 영향 범위를 알리고 다시 확인받을 것
- 모든 설계와 구현은 오캄의 면도날(Occam's razor)을 따라 가능한 간단하게 할 것
  - 단, 예외처리는 항상 고려하고 꼼꼼하게 할 것

### 설계

- 아래 설계 결정은 실행 전에 선택지와 각각의 근거·영향을 먼저 제시하고, 사용자의 확인을 받은 뒤 진행할 것 (근거 검토 없이 혼자 판단해 되돌려야 하는 작업을 만들지 않기 위함)
  - 파일·모듈·기능·설정 항목 삭제
  - 여러 대안 중 하나를 고르는 일 (라이브러리, 구조, 방식 등)
  - 사용자에게 보이는 동작 변경 (출력 값의 의미, 화면 흐름, 기본값)
  - 외부에서 참조하는 식별자 변경 (실행 명령의 경로, 설정 키 이름, ID 등 — 바꾸면 사용자 쪽 명령·설정이 깨짐. 이 저장소의 예시는 프로젝트 섹션 참고)
  - 선택지를 제시할 때는 추천안과 그 이유를 함께 적을 것 (사용자가 비교 없이도 바로 고를 수 있게)
  - 승인 범위는 좁게 해석할 것
    - "N번 진행해"는 그 항목 안의 명확한 버그 수정까지만 승인한 것이며, 설계 결정이 섞여 있으면 따로 물을 것
    - 개선안에 "둘 중 하나 삭제"라고 적었더라도 어느 쪽을 지울지는 승인받지 않은 것
- 지우기 전에 왜 있는지부터 확인할 것
  - 고장 난 코드라고 필요 없는 코드는 아니므로, 먼저 고치는 것이 맞는지 검토할 것
  - 비슷한 것이 두 개 있으면 각각의 원래 용도·제약·장단점을 비교한 뒤 판단할 것

### 구현

- 모든 구현은 가능한 가독성을 최대한으로 고려할 것
- 주석은 한글, 로그와 콘솔 출력 메시지는 모두 영어로 작성할 것
  - 하위 폴더의 CLAUDE.md나 프로젝트 섹션에 다른 규칙이 있으면 그것을 따름

### 검증

- 모든 결과는 사용자에게 보여주기전에 사전에 AI가 직접 확인 후 제공할 것
  - 무엇을 어떤 방법으로 확인했고, 무엇을 확인하지 못했는지 구분해서 보고할 것
  - 실행 환경이 없어 동작을 확인할 수 없으면, 가능한 검증(문법 검사 등)까지 하고 나머지는 "미확인"으로 적을 것


## Coding

- 언어별 표준 코딩 스타일 가이드를 준수할 것
  - Python: [PEP 8](https://peps.python.org/pep-0008/)
  - PowerShell: [PowerShell Practice and Style Guide](https://poshcode.gitbook.io/powershell-practice-and-style/), PSScriptAnalyzer 기본 규칙
  - Bash: [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html), ShellCheck 경고가 없게
  - 스타일 가이드와 이 파일·하위 폴더 CLAUDE.md의 규칙이 충돌하면 이 파일·하위 폴더 CLAUDE.md의 규칙을 따를 것

### Python

- 가능한 모든 string은 f-string을 사용할 것
- 제어문자도 불필요한 사용은 피할것
  - 예: `print("message1\nmessage2")` 대신 `print("message1"); print("message2")`


## 공개 저장소

- 이 저장소는 공개(public)이므로 비밀번호, 토큰, 키, 위치 좌표 같은 개인정보를 파일에 넣지 말 것
  - 이런 값은 `.env`(git 무시)에 두고, 값이 빈 `.env.example`과 사용법을 함께 둘 것
- 커밋 작성자는 `silent <20176737+s1len7@users.noreply.github.com>`을 쓰고, 실제 이메일이 커밋에 들어가지 않게 할 것
- 커밋 메시지와 PR에 `Co-Authored-By: Claude` 같은 AI 공동 작성자 줄을 넣지 말 것


## 프로젝트: 따릉이(Seoul Bike) Home Assistant 통합

서울시 공공자전거 실시간 대여정보 API로 집 주변 대여소의 자전거 수를 보여주는 HACS 커스텀 통합.
저장소: https://github.com/s1len7/ha_seoulbike (공개)

### 구조

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

설정 항목 하나가 API 키를 갖고, 대여소·지역은 그 아래 하위 항목(config subentry)으로 추가한다.

```text
SeoulBike (설정 항목: API 키)
 ├─ 대여소 하위 항목: 대여소 하나 고정 (거리 기준은 zone.home)
 └─ 지역 하위 항목: 지역(zone) 주변 반경 안의 대여소를 가까운 순으로 자동 탐색
```

### 외부에서 참조하는 식별자

`### 설계`의 "외부에서 참조하는 식별자 변경"에 해당하는 이 저장소의 항목이다. 바꾸기 전에 반드시 확인받을 것.

| 식별자 | 위치 | 바꾸면 깨지는 것 |
|---|---|---|
| 엔티티 `unique_id` (`<하위 항목 ID>_<키>`, 지도 엔티티는 `<하위 항목 ID>_<대여소 ID>`) | 각 플랫폼 파일 | 기존 엔티티가 새로 생기고, 대시보드·자동화가 옛 엔티티를 가리킴 |
| 엔티티 ID 형식 (대여소: `sensor.seoulbike_<대여소 번호>_bikes`·`_racks`·`_distance`, `device_tracker`/`geo_location.seoulbike_<대여소 번호>` / 지역: `sensor.seoulbike_<지역>_nearest_station`·`_nearby_stations`, `device_tracker`/`geo_location.seoulbike_<지역>_<대여소 번호>`) | `entity.py` `_suggest_entity_id` | 새로 추가하는 엔티티의 ID 형식이 기존과 달라짐. 한글 이름을 그대로 두면 HA가 로마자로 바꿔 `ddareungi_...` 같은 ID를 만든다 |
| 설정 키 (`seoul_api_key`, `station_id`, `zone_id`, `radius_km`, `top_n`) | `const.py` | 이미 등록된 설정 항목·하위 항목이 값을 못 읽음 |
| 하위 항목 종류 (`station`, `zone`) | `const.py` | 이미 추가한 하위 항목을 인식하지 못함 |
| 설정 항목 `VERSION` | `config_flow.py` | 올리면 `__init__.py`의 `async_migrate_entry`에 이전 코드를 함께 추가해야 함 |
| 도메인 `seoulbike` | `manifest.json` | 통합 자체가 다른 통합으로 인식됨 |
| geo_location 출처 `seoulbike` | `geo_location.py` | 지도 카드의 `geo_location_sources: [seoulbike]` 설정 |

### Home Assistant 통합 규칙

- API 호출은 설정 항목당 coordinator 하나가 할 것. 하위 항목(대여소·지역)마다 호출하지 않는다 (한 번 호출로 전체 대여소를 받음)
- 하위 항목 하나에 기기 하나를 둘 것 (`entity.py`의 `SeoulBikeEntity`)
- 엔티티 플랫폼은 원래 용도에 맞게 쓸 것. 플랫폼마다 HA가 고정해 둔 동작이 있다
  - `device_tracker`: 움직이는 대상(사람·기기) 추적용. 원래 state는 `home`/`not_home`
  - `geo_location`(`GeolocationEvent`): 집 주변의 고정 지점용. `state`는 HA가 distance로 고정(`@final`)해서 덮어쓸 수 없음
- API 실패는 `SeoulApiError`로 올리고, coordinator에서 `UpdateFailed`로 바꿀 것
  - 빈 값을 반환하면 HA가 "대여소 0개"를 정상 데이터로 보고, 재시도·`unavailable` 표시가 동작하지 않음
  - 키 오류는 `SeoulApiAuthError` → `ConfigEntryAuthFailed`로 바꿔 HA가 "재인증 필요" 알림을 띄우게 할 것
  - 서울 API는 키가 틀리면 json을 요청해도 XML(`INFO-100`)로 응답한다
- 다시 로드는 update listener가 맡는다 (API 키 변경, 하위 항목 추가·변경·삭제 모두 listener가 호출됨)
  - listener가 있는 설정 항목에 `async_update_reload_and_abort`를 쓰면 HA가 경고를 남기고 2026.12부터 동작하지 않음. listener가 있으면 `async_update_and_abort`를 쓸 것
- HTTP 요청은 `async_get_clientsession(hass)` 공용 세션을 쓸 것
- 설정 화면·에러 문구 같은 사용자에게 보이는 텍스트는 코드가 아니라 `translations/ko.json`에 둘 것
- 로그 레벨: 1분마다 반복되는 정상 동작은 `debug`, `warning`/`error`는 사용자가 조치해야 하는 문제에만 쓸 것
- 로그도 f-string을 쓸 것 (HA 권장 방식인 `%` 포맷보다 `### Python` 규칙이 우선)
- 로그와 예외 메시지에 API 키와 집 좌표를 넣지 말 것 (사용자가 로그를 GitHub 이슈에 그대로 붙여넣음)
- 버전은 `manifest.json`의 `version`만 올릴 것. `DOMAIN`도 manifest에서 읽으므로 하드코딩하지 않음

### 개발 환경

개발용 Home Assistant는 Docker 컨테이너 `ha-dev`로 돌아가고, 이 저장소의 통합 폴더가 컨테이너에 그대로 연결돼 있다 (복사 없이 바로 반영).
VS Code 작업(`.vscode/tasks.json`)은 저장소 옆의 `ha-dev` 폴더를 사용한다.

```text
~/
├── ha_seoulbike/   # 이 저장소
└── ha-dev/
    ├── docker-compose.yml
    └── config/     # HA 설정 폴더 (컨테이너 /config)
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
| 로그 | `ha-dev/config/home-assistant.log` (`logger`에서 `custom_components.seoulbike: debug` 설정됨) |
| 엔티티 등록 정보 | `ha-dev/config/.storage/core.entity_registry` |
| 엔티티 상태 기록 | `ha-dev/config/home-assistant_v2.db` (recorder) |
| HA 소스 (컨테이너 안) | `/usr/src/homeassistant/homeassistant/` |

```bash
cd ~/ha-dev
docker compose up -d                          # 시작 (VS Code 작업: HA Start)
docker compose restart homeassistant          # 코드 수정 후 반영 (HA Restart)
docker compose logs --since 5m homeassistant 2>&1 | grep -i seoulbike   # (HA Logs)
```

Docker는 Windows의 Docker Desktop이고, WSL에서 `docker` 명령을 쓰려면 Docker Desktop 설정에서 WSL 통합이 켜져 있어야 한다.

- 코드를 고친 뒤에는 이 개발용 HA에서 직접 확인할 것
- `docker` 명령이 응답하지 않으면 Docker Desktop이 꺼진 것이므로 사용자에게 켜달라고 요청할 것
- HA 내부 동작(기본 클래스의 `@final`, state 계산 방식 등)은 추측하지 말고 컨테이너 안의 HA 소스에서 확인할 것
- 엔티티의 현재 상태·속성은 recorder DB의 `states` 테이블에서 확인할 것
  - HA가 쓰고 있는 파일이므로 읽기 전용(`mode=ro`)으로 열어 복사본을 만든 뒤 조회할 것
  - `.storage/core.restore_state`에는 상태 복원 기능이 있는 엔티티만 저장되므로 seoulbike 엔티티는 없다
- 웹 UI로 확인할 것이 있으면 사용자 브라우저에 띄울 것. 로그인이 필요할 수 있으면 탭은 하나만 띄울 것

### 검증

코드를 고치면 아래 순서로 확인할 것.

1. 문법 검사
   ```bash
   for f in custom_components/seoulbike/*.py custom_components/seoulbike/src/*.py; do
     python3 -c "import ast; ast.parse(open('${f}').read())" || echo "FAIL ${f}"
   done
   ```
2. JSON 파일(`manifest.json`, `translations/*.json`)을 고쳤으면 `python3 -c "import json; json.load(open('<파일>'))"`
3. `ha-dev` 재시작 후 로그에서 seoulbike 관련 `ERROR`/`Traceback`이 없는지, `Finished fetching seoulbike data ... (success: True)`가 나오는지 확인
4. 엔티티 상태·속성을 바꿨으면 recorder DB에서 실제 값을 확인
5. 웹 UI에서만 볼 수 있는 동작(설정 화면 입력, 지도 화면)은 직접 확인한 범위와 사용자가 확인할 항목을 나눠 보고할 것

### 디버깅

- 코드에 `debugpy`를 import하지 말 것. 다른 사용자 환경에는 debugpy가 없어 통합 로드가 실패하고, 있으면 원격 코드 실행 포트가 열린다
- 디버깅은 HA 내장 디버거 통합으로 한다. 개발용 HA의 `configuration.yaml`에 아래를 넣고 재시작한 뒤, VS Code의 **Attach HA Debug**(`.vscode/launch.json`)로 접속한다
  ```yaml
  debugpy:
    host: 0.0.0.0
    port: 2015
  ```


<!--
## 참고
- https://daleseo.com/claude-code-claude-md/
-->
