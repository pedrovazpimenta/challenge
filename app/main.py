import os
import json
import uvicorn
from fastapi import HTTPException, status, Request
from utils import get_hash, logger
import classes
import constants as const

app = classes.App(title="System backend")


@app.get("/health")
def health():
    logger.info(
        const.HEALTH_CHECK_SUCCESS,
        run_hash=get_hash(),
        execution_hash=app.execution_hash,
        service_name=const.SERVICE_NAME,
    )
    return {"status": "ok"}


if __name__ == "__main__":
    import yaml

    with open("log_conf.yaml", "r") as f:
        log_config = yaml.safe_load(f)
    uvicorn.run(
        app, host=os.getenv("LOCAL_HOST"), port=8000, log_config=log_config
    )
