import numpy as np
import pickle
from sklearn.pipeline import Pipeline
from utils import logger, load_data, download_model_binary
import classes
import constants as const


def pf_basic_model_inference(
    input: classes.FPInferenceInput, hashes: tuple
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

        # Load the model binary from S3
        model_binary = download_model_binary(
            input.s3_bucket, input.fp_model_path
        )
        model: Pipeline = pickle.loads(model_binary)
        logger.info(
            "Model loaded successfully",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        # Load the data for inference
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

        # Select relevant columns for inference
        relevant_cols = [
            col for col in data.columns if col not in ["id", "target"]
        ]

        logger.info(f"Loaded model steps: {model.named_steps}")
        assert isinstance(model, Pipeline), "Loaded object is not a Pipeline."
        # Perform predictions
        predictions = model.predict(data[relevant_cols].head())

        logger.info(
            "Inference completed successfully",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )

        logger.info(f"model list: {predictions.tolist()}")
        logger.info(f"checked")

        return predictions.tolist()

    except Exception as e:
        logger.error(
            f"An error occurred while doing the prediction: {e}",
            run_hash=hashes[0],
            execution_hash=hashes[1],
            service_name=const.SERVICE_NAME,
        )
        raise e
