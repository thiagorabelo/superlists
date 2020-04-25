import functools
import inspect
import time

from selenium.common.exceptions import WebDriverException


def wait(func=None, max_wait=10, step_wait=0.5):

    def decorator(decored_func):
        @functools.wraps(decored_func)
        def wrapper(*args, **kwargs):
            print(f"max_wait={max_wait}")
            start_time = time.time()

            try:
                while True:
                    try:
                        return decored_func(*args, **kwargs)
                    except (AssertionError, WebDriverException) as ex:
                        if time.time() - start_time > max_wait:
                            raise ex
                        print(f"step_wait={step_wait}")
                        time.sleep(step_wait)
            finally:
                print("----------------------")
        return wrapper

    if inspect.isfunction(func):
        return decorator(func)

    return decorator
