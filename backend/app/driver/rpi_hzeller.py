import numpy as np
from PIL import Image

from .. import config
from .base import MatrixDriver


class RpiHzellerDriver(MatrixDriver):
    """라즈베리파이 + hzeller rpi-rgb-led-matrix 드라이버.

    rgbmatrix 파이썬 바인딩은 pip에 없고 라이브러리 빌드 시 함께 설치된다:
      git clone https://github.com/hzeller/rpi-rgb-led-matrix
      cd rpi-rgb-led-matrix && make build-python && sudo make install-python
    """

    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self._matrix = None
        self._canvas = None

    def open(self) -> None:
        try:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions
        except ImportError as e:
            raise RuntimeError(
                "rgbmatrix 모듈이 없습니다. hzeller/rpi-rgb-led-matrix를 빌드해 "
                "파이썬 바인딩을 설치하거나(docs/hardware.md §3 참고), "
                "하드웨어 없이 개발하려면 MATRIX_DRIVER=sim 으로 실행하세요."
            ) from e

        cols, rows = config.MATRIX_PANEL_COLS, config.MATRIX_PANEL_ROWS
        if self.width % cols or self.height % rows:
            raise RuntimeError(
                f"전체 해상도 {self.width}x{self.height}가 패널 크기 {cols}x{rows}의 "
                "배수가 아닙니다. MATRIX_PANEL_COLS/ROWS를 확인하세요."
            )
        parallel = self.height // rows
        if parallel > 3:
            raise RuntimeError(
                f"parallel={parallel}: rpi-rgb-led-matrix는 병렬 3체인까지 지원합니다. "
                "MATRIX_HEIGHT 또는 패널 배치를 조정하세요."
            )

        opts = RGBMatrixOptions()
        opts.cols = cols
        opts.rows = rows
        opts.chain_length = self.width // cols
        opts.parallel = parallel
        opts.hardware_mapping = config.RPI_HARDWARE_MAPPING
        opts.gpio_slowdown = config.RPI_GPIO_SLOWDOWN
        opts.pwm_bits = config.RPI_PWM_BITS
        opts.brightness = config.MATRIX_BRIGHTNESS

        self._matrix = RGBMatrix(options=opts)
        self._canvas = self._matrix.CreateFrameCanvas()

    def push(self, frame: np.ndarray) -> None:
        if self._matrix is None:
            return
        self._canvas.SetImage(Image.fromarray(frame))
        # 더블 버퍼 스왑 — 티어링 없이 다음 리프레시에 반영
        self._canvas = self._matrix.SwapOnVSync(self._canvas)

    def close(self) -> None:
        if self._matrix is not None:
            self._matrix.Clear()
            self._matrix = None
            self._canvas = None
