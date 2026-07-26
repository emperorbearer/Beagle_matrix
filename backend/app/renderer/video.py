import logging
import subprocess
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)


class VideoPlayer:
    """ffmpeg 서브프로세스로 영상을 디코딩해 매트릭스 해상도의 RGB 프레임을
    순서대로 내놓는다. PocketBeagle 2에서도 OpenCV 없이 apt의 ffmpeg만으로 동작."""

    def __init__(self, path: Path, width: int, height: int, fps: int, loop: bool = True):
        self.path = path
        self.width = width
        self.height = height
        self.fps = fps
        self.loop = loop
        self._frame_bytes = width * height * 3
        self._proc: subprocess.Popen | None = None
        self.finished = False
        self._start()

    def _start(self) -> None:
        # 화면비 유지: 축소 후 검은 여백으로 패딩
        vf = (
            f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,"
            f"pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2:black,"
            f"fps={self.fps}"
        )
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-stream_loop", "-1" if self.loop else "0",
            "-i", str(self.path),
            "-vf", vf,
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "pipe:1",
        ]
        self._proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)

    def read_frame(self) -> np.ndarray | None:
        """블로킹 호출 — 디스플레이 루프에서 executor로 실행할 것."""
        if self._proc is None or self._proc.stdout is None:
            return None
        data = self._proc.stdout.read(self._frame_bytes)
        if data is None or len(data) < self._frame_bytes:
            self.finished = True
            return None
        return np.frombuffer(data, dtype=np.uint8).reshape(self.height, self.width, 3)

    def stop(self) -> None:
        if self._proc is not None:
            self._proc.kill()
            self._proc.wait()
            self._proc = None
