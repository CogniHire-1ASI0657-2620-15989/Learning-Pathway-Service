import time


class CircuitBreaker:
    """Process-local circuit breaker with closed, open and half-open states."""

    def __init__(self, failure_threshold: int = 3, recovery_seconds: float = 30.0):
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._failures = 0
        self._opened_at: float | None = None
        self._half_open_trial_in_flight = False

    def allow_request(self) -> bool:
        if self._opened_at is None:
            return True
        if time.monotonic() - self._opened_at < self._recovery_seconds:
            return False
        if not self._half_open_trial_in_flight:
            self._half_open_trial_in_flight = True
            return True
        return False

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None
        self._half_open_trial_in_flight = False

    def record_failure(self) -> None:
        if self._opened_at is not None:
            self._opened_at = time.monotonic()
            self._half_open_trial_in_flight = False
            return
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._opened_at = time.monotonic()
            self._half_open_trial_in_flight = False
