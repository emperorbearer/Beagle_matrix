import os
from pathlib import Path

MATRIX_WIDTH = int(os.environ.get("MATRIX_WIDTH", "128"))
MATRIX_HEIGHT = int(os.environ.get("MATRIX_HEIGHT", "64"))
MATRIX_DRIVER = os.environ.get("MATRIX_DRIVER", "sim")
MATRIX_FPS = int(os.environ.get("MATRIX_FPS", "30"))

# 한글 출력 시 예: /usr/share/fonts/truetype/nanum/NanumGothic.ttf
FONT_PATH = os.environ.get("FONT_PATH", "")

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 프론트엔드 빌드 결과물 (frontend/ 에서 npm run build)
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
