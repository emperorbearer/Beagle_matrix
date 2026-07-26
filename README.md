# Beagle Matrix

HUB75 LED 매트릭스 패널을 제어해 브라우저에서 문자와 영상을 출력하는 웹앱.
구동 하드웨어는 **Raspberry Pi 4** 또는 **PocketBeagle 2** 중에서 선택할 수 있다.

Web app for driving HUB75 LED matrix panels — display text and video from your browser.
Runs on a Raspberry Pi 4 or a PocketBeagle 2 (selectable driver layer).

## 구성

```
┌──────────────┐   HTTP/WS    ┌─────────────────────────┐   framebuffer   ┌──────────────┐
│   브라우저    │ ───────────► │  Pi 4 / PocketBeagle 2   │ ──────────────► │ HUB75 패널   │
│  (Svelte UI) │ ◄─────────── │  FastAPI + 렌더러 + 드라이버 │                 │  128 × 64 ~  │
└──────────────┘   미리보기    └─────────────────────────┘                 └──────────────┘
```

- **frontend/** — Svelte + Vite 웹 UI. 문자 입력(색상·속도·크기), 영상 업로드/재생, 실시간 미리보기(WebSocket).
- **backend/** — Python FastAPI 서버. 텍스트 → 픽셀 렌더링(Pillow), 영상 → 프레임 디코딩(ffmpeg), 디스플레이 루프.
- **backend/app/driver/** — 매트릭스 드라이버 계층. `sim`(시뮬레이터) / `rpi`(Pi 4 + [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)) / `pb2`(PocketBeagle 2 + PRU).
- **pru/** — PB2 경로용 PRU 펌웨어 (개발 예정).
- **docs/hardware.md** — 하드웨어 설계: 플랫폼 선택 가이드, 부품 목록, 배선, 전원, 최대 해상도 분석.

플랫폼별 트레이드오프(최대 해상도, 개발 기간, 타이밍 품질)는 [docs/hardware.md](docs/hardware.md) §1 참고.
요약: 빨리 크게 만들려면 Pi 4 (병렬 3체인, 256×192급 실증), PRU 펌웨어 개발이 목적이면 PB2.

## 개발 환경에서 실행 (하드웨어 없이)

백엔드 (시뮬레이터 드라이버):

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

프론트엔드:

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173  (API는 8000 포트로 프록시됨)
```

브라우저에서 텍스트를 입력하면 미리보기 캔버스에 매트릭스 출력이 그대로 표시된다.
영상 재생에는 `ffmpeg`이 필요하다 (`sudo apt install ffmpeg`).

## 실기에서 실행

공통: 프론트엔드를 빌드해 두면 백엔드가 정적 파일로 함께 서빙한다.

```bash
cd frontend && npm run build        # frontend/dist 생성
cd ../backend && pip install -r requirements.txt
```

**Raspberry Pi 4** (rpi-rgb-led-matrix 설치는 [docs/hardware.md](docs/hardware.md) §3.3):

```bash
MATRIX_DRIVER=rpi MATRIX_WIDTH=128 MATRIX_HEIGHT=64 \
  sudo -E uvicorn app.main:app --host 0.0.0.0 --port 80
```

**PocketBeagle 2**:

```bash
MATRIX_DRIVER=pb2 uvicorn app.main:app --host 0.0.0.0 --port 80
```

> `pb2` 드라이버는 PRU 펌웨어가 필요하다. 현재는 인터페이스/공유 프레임버퍼까지 구현된
> 상태이며 펌웨어 개발 계획은 [pru/README.md](pru/README.md) 참고. 하드웨어가 준비되기
> 전에는 `MATRIX_DRIVER=sim`(기본값)으로 전체 파이프라인을 검증할 수 있다.

## 설정 (환경변수)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `MATRIX_WIDTH` | `128` | 전체 가로 픽셀 수 |
| `MATRIX_HEIGHT` | `64` | 전체 세로 픽셀 수 |
| `MATRIX_DRIVER` | `sim` | `sim` / `rpi` / `pb2` |
| `MATRIX_FPS` | `30` | 콘텐츠 프레임레이트 |
| `MATRIX_BRIGHTNESS` | `100` | 밝기 0~100 (`rpi` 드라이버) |
| `MATRIX_PANEL_COLS` | `64` | 패널 1장의 가로 픽셀 (`rpi`: 체인/병렬 수 자동 계산) |
| `MATRIX_PANEL_ROWS` | `64` | 패널 1장의 세로 픽셀 |
| `RPI_HARDWARE_MAPPING` | `regular` | `regular`(Active-3) / `adafruit-hat` / `adafruit-hat-pwm` |
| `RPI_GPIO_SLOWDOWN` | `4` | Pi 4 권장 4, 깜빡이면 5 |
| `RPI_PWM_BITS` | `11` | 큰 해상도에서 8~9로 낮추면 리프레시 상승 |
| `FONT_PATH` | (자동) | TTF 폰트 경로. 한글은 예: `/usr/share/fonts/truetype/nanum/NanumGothic.ttf` |
| `UPLOAD_DIR` | `uploads` | 업로드 영상 저장 위치 |

## 라이선스

Apache-2.0
