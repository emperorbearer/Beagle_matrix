from .. import config
from .base import MatrixDriver
from .simulator import SimulatorDriver


def create_driver() -> MatrixDriver:
    name = config.MATRIX_DRIVER
    if name == "rpi":
        from .rpi_hzeller import RpiHzellerDriver

        return RpiHzellerDriver(config.MATRIX_WIDTH, config.MATRIX_HEIGHT)
    if name in ("pb2", "hub75"):  # hub75는 구버전 이름
        from .hub75_pru import Hub75PruDriver

        return Hub75PruDriver(config.MATRIX_WIDTH, config.MATRIX_HEIGHT)
    if name == "sim":
        return SimulatorDriver(config.MATRIX_WIDTH, config.MATRIX_HEIGHT)
    raise ValueError(f"알 수 없는 MATRIX_DRIVER: {name} (sim | rpi | pb2 중 선택)")
