import pandas as pd
import pickle
from sklearn.pipeline import Pipeline
from utils import logger, load_data, download_model_binary
import classes
import constants as const

MODEL_NAME = ""
MODEL = None


def pf_basic_model_batch_inference(
    input: classes.FPBatchInferenceInput, hashes: tuple
) -> list:
    """
    Load a model from S3 and make predictions on a dataset.

    Args:
        input (FPInferenceInput): the input parameters for the inference.
        hashes (tuple): the hashes of the run and execution

    Returns:
        list: the predictions
    """
    try:
        logger.info(
            "Starting model inference",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        global MODEL_NAME
        global MODEL

        if MODEL_NAME != input.fp_model_path:
            MODEL_NAME = input.fp_model_path
            model_binary = download_model_binary(
                input.s3_bucket, input.fp_model_path
            )
            MODEL = pickle.loads(model_binary)
            logger.info(
                "Model binary stored successfully",
                run_hash=hashes[0],
                execution_hash=hashes[1],
                service_name=const.SERVICE_NAME,
            )
        else:
            logger.info(
                "Model binary already stored",
                run_hash=hashes[0],
                execution_hash=hashes[1],
                service_name=const.SERVICE_NAME,
            )

        model: Pipeline = MODEL
        message = {
            "message": "Model loaded successfully",
            "model name": input.fp_model_path,
        }
        logger.info(
            message,
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        data = load_data(input.s3_bucket, input.data_path)

        for col in ["type", "sector"]:
            if col not in data.columns:
                raise ValueError(f"Column '{col}' not found in data.")
        logger.info(
            "Inference data loaded successfully",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        relevant_cols = [
            col for col in data.columns if col not in ["id", "target"]
        ]

        assert isinstance(model, Pipeline), "Loaded object is not a Pipeline."
        predictions = model.predict(data[relevant_cols])

        logger.info(
            "Inference completed successfully",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        return predictions.tolist()

    except Exception as e:
        logger.error(
            f"An error occurred while doing the prediction: {e}",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )
        raise e


def pf_basic_model_inference(
    input: classes.FPSingleInferenceInput, hashes: tuple
) -> list:
    """
    Load a model from S3 and make predictions on a dataset.

    Args:
        input (FPInferenceInput): the input parameters for the inference.
        hashes (tuple): the hashes of the run and execution

    Returns:
        list: the predictions
    """
    try:
        logger.info(
            "Starting model inference",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        global MODEL_NAME
        global MODEL

        if MODEL_NAME != input.fp_model_path:
            MODEL_NAME = input.fp_model_path
            model_binary = download_model_binary(
                input.s3_bucket, input.fp_model_path
            )
            MODEL = pickle.loads(model_binary)
            logger.info(
                "Model binary stored successfully",
                run_hash=hashes[0],
                execution_hash=hashes[1],
                service_name=const.SERVICE_NAME,
            )
        else:
            logger.info(
                "Model binary already stored",
                run_hash=hashes[0],
                execution_hash=hashes[1],
                service_name=const.SERVICE_NAME,
            )

        model: Pipeline = MODEL
        message = {
            "message": "Model loaded successfully",
            "model name": input.fp_model_path,
        }
        logger.info(
            message,
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        data = pd.DataFrame([input.input.model_dump()])

        for col in ["type", "sector"]:
            if col not in data.columns:
                raise ValueError(f"Column '{col}' not found in data.")
        logger.info(
            "Inference data loaded successfully",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        relevant_cols = [
            col for col in data.columns if col not in ["id", "target"]
        ]

        assert isinstance(model, Pipeline), "Loaded object is not a Pipeline."
        predictions = model.predict(data[relevant_cols])

        logger.info(
            "Inference completed successfully",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        return predictions.tolist()

    except Exception as e:
        logger.error(
            f"An error occurred while doing the prediction: {e}",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )
        raise e
