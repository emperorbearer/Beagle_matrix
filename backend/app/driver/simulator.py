import numpy as np

from .base import MatrixDriver


class SimulatorDriver(MatrixDriver):
    """하드웨어 없이 개발할 때 쓰는 드라이버.

    실제 출력은 하지 않는다 — 웹 UI의 미리보기(WebSocket)가 곧 시뮬레이터
    화면 역할을 하므로 여기서는 프레임을 버린다.
    """

    def push(self, frame: np.ndarray) -> None:
        pass
