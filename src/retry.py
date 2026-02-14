import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar, Optional, Tuple

T = TypeVar("T")

@dataclass
class RetryPolicy:
    attempts: int = 5
    base_delay_s: float = 1.0
    max_delay_s: float = 30.0
    jitter: float = 0.25  # +-25% jitter


def sleep_backoff(attempt: int, policy: RetryPolicy) -> None:
    # exponential backoff: base * 2^(attempt-1)
    delay = min(policy.max_delay_s, policy.base_delay_s * (2 ** (attempt - 1)))
    # add jitter so you don't “sync” with server throttling
    jitter = delay * policy.jitter * (random.random() * 2 - 1)
    time.sleep(max(0.0, delay + jitter))


def with_retries(
    fn: Callable[[], T],
    policy: RetryPolicy,
    on_error: Optional[Callable[[Exception, int], None]] = None,
    retry_on: Tuple[type, ...] = (Exception,),
) -> T:
    last_err: Exception | None = None
    for attempt in range(1, policy.attempts + 1):
        try:
            return fn()
        except retry_on as e:
            last_err = e
            if on_error:
                on_error(e, attempt)
            if attempt == policy.attempts:
                raise
            sleep_backoff(attempt, policy)
    raise last_err  # for type checkers
