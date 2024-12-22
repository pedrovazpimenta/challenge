from pydantic import BaseModel

class FPTrainingInput(BaseModel):
    s3_bucket: str
    training_data_path: str
    test_data_path: str
    learning_rate: float = 0.01
    n_estimators: int = 300
    max_depth: int = 5
    loss: str = "absolute_error"

class FPInferenceInput(BaseModel):
    model_path: str
    data_path: str