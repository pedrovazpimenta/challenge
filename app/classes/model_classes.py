import os
from typing import Optional
from pydantic import BaseModel


class FPTrainingInput(BaseModel):

    training_data_path: str
    test_data_path: str
    s3_bucket: str = os.getenv("MLFLOW_S3_BUCKET_NAME")
    learning_rate: float = 0.01
    n_estimators: int = 300
    max_depth: int = 5
    loss: str = "absolute_error"


class FPBatchInferenceInput(BaseModel):
    fp_model_path: str
    data_path: str
    s3_bucket: str = os.getenv("MLFLOW_S3_BUCKET_NAME")


class InputColumns(BaseModel):
    type: str
    sector: str
    net_usable_area: float
    net_area: float
    n_rooms: float
    n_bathroom: float
    latitude: float
    longitude: float
    price: Optional[float] = 0.0


class FPSingleInferenceInput(BaseModel):
    fp_model_path: str
    input: InputColumns
    s3_bucket: str = os.getenv("MLFLOW_S3_BUCKET_NAME")
