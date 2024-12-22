from logging import DEBUG, WARNING, CRITICAL, ERROR, INFO

LOG_FILE_PATH: str = "logs/executions.log"
APP_STARTED: str = "Application started"
APP_SHUTDOWN: str = "Application shutdown"
HEALTH_CHECK_SUCCESS: str = "Health check success"
LOG_TYPE: dict = {
    "DEBUG": DEBUG,
    "WARNING": WARNING,
    "CRITICAL": CRITICAL,
    "ERROR": ERROR,
    "INFO": INFO,
}
FORMAT: str = "%(levelprefix)s [%(threadName)s] [%(name)s] %(message)s"
SERVICE_NAME: str = "Model API"
TRAINING_STARTED: str = "Training started"
TRAINING_SUCCESS: str = "Training success"
TRAINING_ERROR: str = "Training error"
INFERENCE_STARTED: str = "Inference started"
INFERENCE_SUCCESS: str = "Inference success"
INFERENCE_ERROR: str = "Inference error"
