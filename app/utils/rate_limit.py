"""Small in-memory fixed-window rate limiter."""

from collections import defaultdict, deque
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from time import monotonic


@dataclass
class SimpleRateLimiter:
    """Track request timestamps per key in memory."""

    max_requests: int
    window_seconds: int
    hits: MutableMapping[str, deque[float]] = field(default_factory=lambda: defaultdict(deque))

    def allow(self, key: str, now: float | None = None) -> bool:
        """Return True when the key has remaining requests in the active window."""

        current = monotonic() if now is None else now
        window_start = current - self.window_seconds
        key_hits = self.hits[key]

        while key_hits and key_hits[0] <= window_start:
            key_hits.popleft()

        if len(key_hits) >= self.max_requests:
            return False

        key_hits.append(current)
        return True
