import os
import json
from time import perf_counter
import uvicorn
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from utils import get_hash, logger
import numpy as np
import classes
import constants as const
import model_training
import model_inference

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


@app.post("/train_fp_basic_model")
async def train_fp_basic_model(input: classes.FPTrainingInput):
    """
    Train a model to predict the price of a property given a set of
    features downloaded from the property_friends dataset in S3.

    Args:
        input (FPTrainingInput): the input parameters for the training.

    Returns:
        dict: the status of the training
    """
    run_hash = get_hash()
    hashes = (run_hash, app.execution_hash)
    try:
        logger.info(
            const.TRAINING_STARTED,
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )
        model_training.pf_basic_model_training(input, hashes)
        logger.info(
            const.TRAINING_SUCCESS,
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(
            const.TRAINING_ERROR + f": {str(e)}.",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=json.dumps({"error": str(e)}),
        )


@app.post("/inference_fp_basic_model")
async def inference_fp_basic_model(input: classes.FPInferenceInput):
    """
    Load a model from S3 and make predictions on a dataset.

    Args:
        input (FPInferenceInput): the input parameters for the inference.

    Returns:
        dict: the predictions
    """
    run_hash = get_hash()
    hashes = (run_hash, app.execution_hash)
    try:
        logger.info(
            const.INFERENCE_STARTED,
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )
        starting_time = perf_counter()
        predictions = model_inference.pf_basic_model_inference(input, hashes)
        ending_time = perf_counter()
        logger.info(
            const.INFERENCE_SUCCESS,
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        return JSONResponse(
            {
                "model": input.fp_model_path,
                "input_data": input.data_path,
                "time": ending_time - starting_time,
                "predictions": predictions,
            }
        )
    except Exception as e:
        logger.error(
            const.INFERENCE_ERROR + f": {str(e)}.",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=json.dumps({"error": str(e)}),
        )


if __name__ == "__main__":
    import yaml

    with open("log_conf.yaml", "r") as f:
        log_config = yaml.safe_load(f)
    uvicorn.run(
        app, host=os.getenv("LOCAL_HOST"), port=8000, log_config=log_config
    )
