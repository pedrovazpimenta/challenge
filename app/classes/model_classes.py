import os
from pydantic import BaseModel


class FPTrainingInput(BaseModel):

    training_data_path: str
    test_data_path: str
    s3_bucket: str = os.getenv("MLFLOW_S3_BUCKET_NAME")
    learning_rate: float = 0.01
    n_estimators: int = 300
    max_depth: int = 5
    loss: str = "absolute_error"


class FPInferenceInput(BaseModel):
    fp_model_path: str
    data_path: str
    s3_bucket: str = os.getenv("MLFLOW_S3_BUCKET_NAME")
