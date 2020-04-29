import functools
import inspect
import time

from selenium.common.exceptions import WebDriverException


def wait(func=None, max_wait=10, step_wait=0.5):

    def decorator(decored_func):
        @functools.wraps(decored_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            time.sleep(step_wait)

            while True:
                try:
                    return decored_func(*args, **kwargs)
                except (AssertionError, WebDriverException) as ex:
                    if time.time() - start_time > max_wait:
                        raise ex
                    time.sleep(step_wait)
        return wrapper

    if inspect.isfunction(func):
        return decorator(func)

    return decorator


class ExplicitWaitMixin:  # pylint: disable=too-few-public-methods
    @staticmethod
    def wait_for(func, *args, max_wait=10, step_wait=0.5, **kwargs):
        @wait(max_wait=max_wait, step_wait=step_wait)
        @functools.wraps(func)
        def proxy_dummy(*args_, **kwargs_):
            return func(*args_, **kwargs_)

        return proxy_dummy(*args, **kwargs)
