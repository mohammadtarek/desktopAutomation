import time
from typing import Callable, Optional, Type, TypeVar, Tuple

from utils.logger import get_logger

T = TypeVar("T")
logger = get_logger("retry")


def retry(
    attempts: int = 3,
    delay_seconds: float = 1.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
):
    """
    Simple retry decorator with fixed delay.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            last_exc: Optional[BaseException] = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # type: ignore[misc]
                    last_exc = exc
                    logger.warning(
                        "Attempt %s/%s failed: %s", attempt, attempts, exc
                    )
                    if attempt < attempts:
                        time.sleep(delay_seconds)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
