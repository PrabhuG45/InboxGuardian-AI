import asyncio
import time
from fastapi import HTTPException, status


class TokenBucketRateLimiter:
    """Thread-safe Token Bucket Rate Limiter for outbound API requests."""

    def __init__(self, capacity: int = 10, refill_rate: float = 2.0):
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.refill_rate = refill_rate  # tokens added per second
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens_needed: float = 1.0) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.last_refill = now

            # Refill tokens based on time elapsed
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
            else:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Outbound API rate limit exceeded. Please retry later.",
                )


# Global rate limiter instance (10 tokens max, refills 2 tokens/sec)
api_rate_limiter = TokenBucketRateLimiter(capacity=10, refill_rate=2.0)