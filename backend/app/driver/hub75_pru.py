import logging
import mmap
import os

import numpy as np

from .base import MatrixDriver

log = logging.getLogger(__name__)

# PRU 펌웨어와 공유하는 프레임버퍼. 디바이스 트리에서 예약한 메모리를
# uio 또는 /dev/mem 으로 노출한 경로를 환경변수로 지정한다.
# 레이아웃(더블 버퍼 + 스왑 플래그)은 pru/README.md 참고.
FRAMEBUFFER_PATH = os.environ.get("HUB75_FB_PATH", "/dev/uio0")


class Hub75PruDriver(MatrixDriver):
    """HUB75 실기 드라이버: 공유 메모리에 RGB888 프레임을 쓰고
    PRU 펌웨어가 BCM 스캔을 담당한다. 펌웨어는 pru/ 에서 개발 중."""

    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self._mem: mmap.mmap | None = None
        self._frame_bytes = width * height * 3

    def open(self) -> None:
        try:
            fd = os.open(FRAMEBUFFER_PATH, os.O_RDWR | os.O_SYNC)
        except OSError as e:
            raise RuntimeError(
                f"HUB75 공유 프레임버퍼({FRAMEBUFFER_PATH})를 열 수 없습니다. "
                "PRU 펌웨어가 로드되어 있는지 확인하거나, 하드웨어 없이 개발하려면 "
                "MATRIX_DRIVER=sim 으로 실행하세요."
            ) from e
        # 더블 버퍼 + 제어 워드 공간
        self._mem = mmap.mmap(fd, self._frame_bytes * 2 + 64)
        os.close(fd)

    def push(self, frame: np.ndarray) -> None:
        if self._mem is None:
            return
        # TODO: 더블 버퍼 스왑 프로토콜 확정 후 back buffer 선택 로직 추가
        self._mem[: self._frame_bytes] = frame.tobytes()

    def close(self) -> None:
        if self._mem is not None:
            self._mem.close()
            self._mem = None
