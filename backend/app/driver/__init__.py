from .. import config
from .base import MatrixDriver
from .simulator import SimulatorDriver


def create_driver() -> MatrixDriver:
    if config.MATRIX_DRIVER == "hub75":
        from .hub75_pru import Hub75PruDriver

        return Hub75PruDriver(config.MATRIX_WIDTH, config.MATRIX_HEIGHT)
    return SimulatorDriver(config.MATRIX_WIDTH, config.MATRIX_HEIGHT)
