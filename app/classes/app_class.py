from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from utils import get_hash, logger
import constants as const


class App(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(lifespan=self.lifespan, *args, **kwargs)
        self.execution_hash = None
        self.mount("/static", StaticFiles(directory="static"), name="static")

    def lifespan(self, app: FastAPI):
        app.execution_hash = get_hash()
        logger.info(
            const.APP_STARTED,
            execution_hash=self.execution_hash,
            service_name=const.SERVICE_NAME,
        )
        yield
