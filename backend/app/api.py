import re

from fastapi import APIRouter, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from . import config

router = APIRouter(prefix="/api")

ALLOWED_VIDEO_EXT = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".gif"}


def _manager(request: Request):
    return request.app.state.display


@router.get("/config")
def get_config():
    return {
        "width": config.MATRIX_WIDTH,
        "height": config.MATRIX_HEIGHT,
        "fps": config.MATRIX_FPS,
        "driver": config.MATRIX_DRIVER,
    }


@router.get("/status")
def get_status(request: Request):
    m = _manager(request)
    return {"mode": m.mode, "detail": m.detail}


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    color: str = "#ffffff"
    bg: str = "#000000"
    speed: float = Field(default=40.0, ge=0, le=500)
    font_size: int = Field(default=0, ge=0, le=256)


@router.post("/display/text")
def display_text(req: TextRequest, request: Request):
    _manager(request).show_text(req.text, req.color, req.bg, req.speed, req.font_size)
    return {"ok": True}


@router.post("/display/stop")
def display_stop(request: Request):
    _manager(request).stop()
    return {"ok": True}


def _safe_name(name: str) -> str:
    return re.sub(r"[^\w.\-가-힣]", "_", name)


@router.get("/videos")
def list_videos():
    files = sorted(
        p.name for p in config.UPLOAD_DIR.iterdir()
        if p.suffix.lower() in ALLOWED_VIDEO_EXT
    )
    return {"videos": files}


@router.post("/videos")
async def upload_video(file: UploadFile):
    name = _safe_name(file.filename or "video")
    if not any(name.lower().endswith(ext) for ext in ALLOWED_VIDEO_EXT):
        raise HTTPException(400, f"지원하지 않는 형식입니다: {name}")
    dest = config.UPLOAD_DIR / name
    with dest.open("wb") as f:
        while chunk := await file.read(1 << 20):
            f.write(chunk)
    return {"ok": True, "name": name}


class PlayRequest(BaseModel):
    name: str
    loop: bool = True


@router.post("/display/video")
def play_video(req: PlayRequest, request: Request):
    path = config.UPLOAD_DIR / _safe_name(req.name)
    if not path.is_file():
        raise HTTPException(404, "영상을 찾을 수 없습니다")
    _manager(request).play_video(path, loop=req.loop)
    return {"ok": True}


@router.websocket("/ws/preview")
async def ws_preview(ws: WebSocket):
    await ws.accept()
    manager = ws.app.state.display
    q = manager.subscribe()
    try:
        while True:
            frame: bytes = await q.get()
            await ws.send_bytes(frame)
    except WebSocketDisconnect:
        pass
    finally:
        manager.unsubscribe(q)
