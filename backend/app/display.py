import asyncio
import logging
import time
from pathlib import Path

import numpy as np

from . import config
from .driver.base import MatrixDriver
from .renderer.text import TextScroller
from .renderer.video import VideoPlayer

log = logging.getLogger(__name__)


class DisplayManager:
    """현재 콘텐츠(텍스트/영상/꺼짐)를 프레임레이트에 맞춰 렌더링해서
    드라이버로 보내고, 미리보기 WebSocket 구독자에게도 같은 프레임을 뿌린다."""

    def __init__(self, driver: MatrixDriver):
        self.driver = driver
        self.width = driver.width
        self.height = driver.height
        self.mode = "off"
        self.detail: dict = {}
        self._text: TextScroller | None = None
        self._video: VideoPlayer | None = None
        self._black = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self._subscribers: set[asyncio.Queue] = set()
        self._task: asyncio.Task | None = None

    # ── 콘텐츠 전환 ──────────────────────────────────────────────

    def show_text(self, text: str, color: str, bg: str, speed: float, font_size: int) -> None:
        self._stop_video()
        self._text = TextScroller(
            self.width, self.height, text,
            color=color, bg=bg, speed=speed, font_size=font_size,
        )
        self.mode = "text"
        self.detail = {"text": text, "color": color, "speed": speed}

    def play_video(self, path: Path, loop: bool) -> None:
        self._stop_video()
        self._text = None
        self._video = VideoPlayer(path, self.width, self.height, config.MATRIX_FPS, loop=loop)
        self.mode = "video"
        self.detail = {"file": path.name, "loop": loop}

    def stop(self) -> None:
        self._stop_video()
        self._text = None
        self.mode = "off"
        self.detail = {}

    def _stop_video(self) -> None:
        if self._video is not None:
            self._video.stop()
            self._video = None

    # ── 미리보기 구독 ────────────────────────────────────────────

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=2)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.discard(q)

    # ── 메인 루프 ────────────────────────────────────────────────

    def start(self) -> None:
        self._task = asyncio.get_event_loop().create_task(self._run())

    async def shutdown(self) -> None:
        if self._task is not None:
            self._task.cancel()
        self.stop()
        self.driver.close()

    async def _run(self) -> None:
        loop = asyncio.get_event_loop()
        interval = 1.0 / config.MATRIX_FPS
        last = time.monotonic()
        while True:
            now = time.monotonic()
            dt, last = now - last, now

            frame = self._black
            if self.mode == "text" and self._text is not None:
                frame = self._text.next_frame(dt)
            elif self.mode == "video" and self._video is not None:
                f = await loop.run_in_executor(None, self._video.read_frame)
                if f is not None:
                    frame = f
                elif self._video is not None and self._video.finished:
                    self.stop()

            self.driver.push(frame)
            payload = frame.tobytes()
            for q in list(self._subscribers):
                if q.full():
                    q.get_nowait()  # 느린 클라이언트는 오래된 프레임을 버림
                q.put_nowait(payload)

            elapsed = time.monotonic() - now
            await asyncio.sleep(max(interval - elapsed, 0))
