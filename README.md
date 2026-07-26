# Beagle Matrix

PocketBeagle 2로 HUB75 LED 매트릭스 패널을 제어해 브라우저에서 문자와 영상을 출력하는 웹앱.

Web app for driving a HUB75 LED matrix panel from a PocketBeagle 2 — display text and video from your browser.

## 구성

```
┌──────────────┐   HTTP/WS    ┌─────────────────────────┐   framebuffer   ┌──────────────┐
│   브라우저    │ ───────────► │  PocketBeagle 2          │ ──────────────► │ HUB75 패널   │
│  (Svelte UI) │ ◄─────────── │  FastAPI + 렌더러 + 드라이버 │    (PRU/GPIO)   │  128 × 64    │
└──────────────┘   미리보기    └─────────────────────────┘                 └──────────────┘
```

- **frontend/** — Svelte + Vite 웹 UI. 문자 입력(색상·속도·크기), 영상 업로드/재생, 실시간 미리보기(WebSocket).
- **backend/** — Python FastAPI 서버. 텍스트 → 픽셀 렌더링(Pillow), 영상 → 프레임 디코딩(ffmpeg), 디스플레이 루프.
- **backend/app/driver/** — 매트릭스 드라이버 계층. 개발 PC에서는 시뮬레이터, 실기에서는 HUB75(PRU) 드라이버.
- **pru/** — PRU 펌웨어 (HUB75 비트뱅잉, 개발 예정).
- **docs/hardware.md** — 하드웨어 설계: 부품 목록, 배선, 전원, 최대 해상도 분석.

기본 목표 해상도는 **128×64** (64×64 패널 2장 체인)이며, 근거는 [docs/hardware.md](docs/hardware.md) 참고.

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

## PocketBeagle 2에서 실행

```bash
# 프론트엔드 빌드 결과물을 백엔드가 정적 파일로 서빙
cd frontend && npm run build        # frontend/dist 생성
cd ../backend
pip install -r requirements.txt
MATRIX_DRIVER=hub75 uvicorn app.main:app --host 0.0.0.0 --port 80
```

> HUB75 드라이버는 PRU 펌웨어가 필요하다. 현재는 인터페이스/공유 프레임버퍼까지 구현된 상태이며
> 펌웨어 개발 계획은 [pru/README.md](pru/README.md) 참고. 하드웨어가 준비되기 전에는
> `MATRIX_DRIVER=sim`(기본값)으로 전체 파이프라인을 검증할 수 있다.

## 설정 (환경변수)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `MATRIX_WIDTH` | `128` | 전체 가로 픽셀 수 |
| `MATRIX_HEIGHT` | `64` | 전체 세로 픽셀 수 |
| `MATRIX_DRIVER` | `sim` | `sim` 또는 `hub75` |
| `MATRIX_FPS` | `30` | 콘텐츠 프레임레이트 |
| `FONT_PATH` | (자동) | TTF 폰트 경로. 한글은 예: `/usr/share/fonts/truetype/nanum/NanumGothic.ttf` |
| `UPLOAD_DIR` | `uploads` | 업로드 영상 저장 위치 |

## 라이선스

Apache-2.0
