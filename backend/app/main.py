import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import config
from .api import router
from .display import DisplayManager
from .driver import create_driver

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    driver = create_driver()
    driver.open()
    display = DisplayManager(driver)
    app.state.display = display
    display.start()
    log.info(
        "beagle-matrix 시작: %dx%d, driver=%s",
        config.MATRIX_WIDTH, config.MATRIX_HEIGHT, config.MATRIX_DRIVER,
    )
    yield
    await display.shutdown()


app = FastAPI(title="beagle-matrix", lifespan=lifespan)
app.include_router(router)

if config.FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=config.FRONTEND_DIST, html=True), name="frontend")
