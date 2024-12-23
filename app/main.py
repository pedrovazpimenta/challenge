import os
import json
from time import perf_counter
from datetime import timedelta
from typing import Annotated
import uvicorn
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from utils import get_hash, logger, fake_users_db, verify_generated_token
import classes
import utils
import constants as const
import model_training
import model_inference

app = classes.App(title="Model API", version="0.1.0")


@app.get("/health")
async def health():
    logger.info(
        const.HEALTH_CHECK_SUCCESS,
        run_hash=get_hash(),
        execution_hash=app.execution_hash,
        service_name=const.SERVICE_NAME,
    )
    return {"status": "ok"}


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> classes.Token:
    try:
        user = utils.authenticate_user(
            fake_users_db, form_data.username, form_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(
            minutes=const.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = utils.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return classes.Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        logger.error(
            const.LOGIN_ERROR + f": {str(e)}.",
            run_hash=get_hash(),
            execution_hash=app.execution_hash,
            service_name=const.SERVICE_NAME,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=json.dumps({"error": str(e)}),
        )


@app.get("/users/me/", response_model=classes.User)
async def read_users_me(
    current_user: Annotated[
        classes.User, Depends(utils.get_current_active_user)
    ],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[
        classes.User, Depends(utils.get_current_active_user)
    ],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.post("/train_fp_basic_model")
async def train_fp_basic_model(
    input: classes.FPTrainingInput,
    authentication=Annotated[
        classes.Authentication, Depends(utils.verify_generated_token)
    ],
):
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


@app.post("/batch_inference_fp_basic_model")
async def inference_fp_basic_model(
    input: classes.FPBatchInferenceInput,
    authentication=Annotated[
        classes.Authentication, Depends(utils.verify_generated_token)
    ],
):
    """
    Load a model from S3 and make predictions on a dataset also from S3.

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
        predictions = model_inference.pf_basic_model_batch_inference(
            input, hashes
        )
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


@app.post("/single_inference_fp_basic_model")
async def inference_fp_basic_model(
    input: classes.FPSingleInferenceInput,
    authentication=Annotated[
        classes.Authentication, Depends(utils.verify_generated_token)
    ],
):
    """
    Load a model from S3 and make predictions on a single datapoint.

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

        message = {
            "model": input.fp_model_path,
            "input_data": input.input.model_dump(),
            "time": ending_time - starting_time,
            "prediction": predictions[0],
        }
        logger.info(
            message,
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        return JSONResponse(message)
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
