import os
import logging
import json
import time
import hashlib
from logging import DEBUG, WARNING, CRITICAL, ERROR, INFO
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import uvicorn
import constants as const

LOG_LEVEL = const.LOG_TYPE[os.environ.get("LOG_LEVEL", "INFO")]

rotatingHandler = RotatingFileHandler(
    filename=const.LOG_FILE_PATH, maxBytes=20000, backupCount=1
)


logging_params = {
    "level": LOG_LEVEL,
    "handlers": [rotatingHandler],
}


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class Logger(metaclass=Singleton):
    def __init__(self) -> None:
        logging.basicConfig(**logging_params)
        self.logger = logging.getLogger(__name__)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        formatter = uvicorn.logging.DefaultFormatter(
            const.FORMAT, datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_standard_log(
        self,
        message: str,
        level: str,
        run_hash: str,
        service_name: str,
        execution_hash: str,
    ) -> dict:
        """
        The method returns a dict containing a standard log message.

        Parameters:
            message: message to be logged
            level: log-message level
            run_hash: hash id for the process
            service_name: name of the service which generated the log
        Returns:
            msg_dict: dictionary holding the message, timestamp, run_hash,
                    level and service values
        """
        if run_hash:
            display_run_hash = run_hash[:8]
        else:
            display_run_hash = run_hash

        if execution_hash:
            display_execution_hash = execution_hash[:8]
        else:
            display_execution_hash = execution_hash

        msg_dict = {
            "message": message,
            "run_hash": display_run_hash,
            "execution_hash": display_execution_hash,
            "level": level,
            "service": service_name,
        }
        return msg_dict

    def log(
        self,
        message: str,
        run_hash: str,
        execution_hash: str,
        msg_loglevel: str,
        service_name: str,
        loglevel: str,
    ) -> None:
        """
        A method for handling the logging process of messages

        Parameters:
            message: string message to be logged
            run_hash: hash id for the process
            msg_loglevel: which level the logging must occur
            service_name: name of the service calling the log
            loglevel: the level of the log
        """
        message = self.get_standard_log(
            message, msg_loglevel, run_hash, service_name, execution_hash
        )
        message_text = json.dumps(message)
        self.logger.log(loglevel, f"{message_text}")

    def debug(
        self,
        message: str,
        run_hash: str = None,
        service_name: str = None,
        execution_hash: str = None,
    ) -> None:
        """
        A method for handling the logging for debug messages

        Parameters:
            message: string message to be logged
            run_hash: hash id for the process
            service_name: name of the service calling the log
        """
        self.log(
            message,
            run_hash,
            execution_hash,
            str(DEBUG),
            service_name,
            DEBUG,
        )

    def warning(
        self,
        message: str,
        run_hash: str = None,
        service_name: str = None,
        execution_hash: str = None,
    ) -> None:
        """
        A method for handling the logging for debug messages

        Parameters:
            message: string message to be logged
            run_hash: hash id for the process
            service_name: name of the service calling the log
        """
        self.log(
            message,
            run_hash,
            execution_hash,
            str(WARNING),
            service_name,
            WARNING,
        )

    def critical(
        self,
        message: str,
        run_hash: str = None,
        service_name: str = None,
        execution_hash: str = None,
    ) -> None:
        """
        A method for handling the logging for debug messages

        Parameters:
            message: string message to be logged
            run_hash: hash id for the process
            service_name: name of the service calling the log
        """
        self.log(
            message,
            run_hash,
            execution_hash,
            str(CRITICAL),
            service_name,
            CRITICAL,
        )

    def error(
        self,
        message: str,
        run_hash: str = None,
        service_name: str = None,
        execution_hash: str = None,
    ) -> None:
        """
        A method for handling the logging for debug messages

        Parameters:
            message: string message to be logged
            run_hash: hash id for the process
            service_name: name of the service calling the log
        """
        self.log(
            message,
            run_hash,
            execution_hash,
            str(ERROR),
            service_name,
            ERROR,
        )

    def info(
        self,
        message: str,
        run_hash: str = None,
        service_name: str = None,
        execution_hash: str = None,
    ) -> None:
        """
        A method for handling the logging for debug messages

        Parameters:
            message: string message to be logged
            run_hash: hash id for the process
            service_name: name of the service calling the log
        """
        self.log(
            message,
            run_hash,
            execution_hash,
            str(INFO),
            service_name,
            INFO,
        )


def get_hash(*args) -> str:
    """
    The method gets a secure hash using MD5 algorithm

    Returns:
        a string object of double length, containing only hexadecimal
        digits
    """
    try:
        extra_inputs = [str(entry) for entry in args]
        hash_base = str(time.perf_counter()).encode("utf-8") + "-".join(
            extra_inputs
        ).encode("utf-8")
    except Exception as e:
        hash_base = str(time.perf_counter()).encode("utf-8") + str(e).encode(
            "utf-8"
        )

    run_hash = hashlib.md5(usedforsecurity=False)
    run_hash.update(hash_base)
    return run_hash.hexdigest()


logger = Logger()
