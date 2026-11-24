import asyncio
import random
import logging
from typing import Callable, Any, TypeVar

T = TypeVar("T")
logger = logging.getLogger("orchestrator")


class ResilientOrchestrator:
    """Executes external API calls with Exponential Backoff and Full Jitter."""

    @staticmethod
    async def execute_with_retry(
        func: Callable[..., Any],
        *args: Any,
        max_retries: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 8.0,
        **kwargs: Any,
    ) -> Any:
        attempt = 0
        while True:
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                attempt += 1
                if attempt > max_retries:
                    logger.error(
                        f"Execution failed after {max_retries} retries: {exc}"
                    )
                    raise exc

                # Calculate Exponential Backoff with Full Jitter: Sleep ~ Uniform(0, min(max_delay, base * 2^attempt))
                calculated_delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                jittered_delay = random.uniform(0, calculated_delay)

                logger.warning(
                    f"Attempt {attempt}/{max_retries} failed ({exc}). Retrying in {jittered_delay:.2f}s..."
                )
                await asyncio.sleep(jittered_delay)


orchestrator = ResilientOrchestrator()