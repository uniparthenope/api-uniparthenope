import logging
from functools import wraps
import time

global_path = "app/log/"


def time_log(title="api.uniparthenope.it", filename="", funcName=""):

    logger = logging.getLogger(title)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(global_path + filename)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    def decorator(func):
        """This decorator prints the execution time for the decorated function."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            logger.info("{} {} Time {}s".format(funcName, func.__name__, round(end - start, 2)))
            return result

        return wrapper

    return decorator
