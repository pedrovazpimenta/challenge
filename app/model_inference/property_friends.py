import numpy as np
import pickle
from utils import logger, load_data, download_model_binary
import classes


def pf_basic_model_inference(
    input: classes.FPInferenceInput, hashes: tuple
) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
    """
    Load a model from S3 and make predictions on a dataset.

    Args:
        input (FPInferenceInput): the input parameters for the inference.
        hashes (tuple): the hashes of the run and execution

    Returns:
        np.ndarray | tuple[np.ndarray, np.ndarray]: the predictions
    """
    try:
        model_binary = download_model_binary(input.model_path)
        model = pickle.loads(model_binary)
        data = load_data(input.data_path)
        relevant_cols = [
            col for col in data.columns if col not in ["id", "target"]
        ]
        return model.predict(data[relevant_cols])
    except Exception as e:
        logger.error(
            f"An error occurred: {e}",
            run_hash=hashes[0],
            execution_hash=hashes[1],
        )
        raise e
