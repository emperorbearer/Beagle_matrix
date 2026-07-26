import numpy as np


class MatrixDriver:
    """매트릭스 출력 드라이버 인터페이스.

    push()는 (H, W, 3) uint8 RGB 프레임을 받는다. 디스플레이 루프에서
    프레임레이트에 맞춰 호출되므로 블로킹 없이 빠르게 반환해야 한다.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def open(self) -> None:
        pass

    def push(self, frame: np.ndarray) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass
