from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

def async_retryable(
        attempts: int = 3,
        multiplier: float = 1,
        min_wait: float = 1,
        max_wait: float = 10,
        exceptions=(Exception,)
):
    """
    Async retry decorator with exponential backoff and jitter.
    - attempts: max retry attempts
    - multiplier: base for exponential
    - min_wait/max_wait: jittered interval bounds in seconds
    - exceptions: tuple of exceptions to trigger retry
    """
    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_random_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(exceptions),
        reraise=True
    )
