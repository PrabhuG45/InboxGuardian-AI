import asyncio
import time
from app.core.rate_limiter import TokenBucketRateLimiter
from app.services.orchestrator import orchestrator


async def test_resilience_suite():
    print("=" * 65)
    print("🧪 RUNNING EASYMAIL RESILIENT ORCHESTRATOR SUITE")
    print("=" * 65)

    # 1. Test Token Bucket Rate Limiter
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1.0)
    print("\n💧 1. Testing Token Bucket Exhaustion:")

    # Acquire 3 available tokens
    for i in range(3):
        await limiter.acquire(1.0)
        print(f"   • Token {i+1} acquired successfully.")

    # 4th acquisition should fail immediately
    try:
        await limiter.acquire(1.0)
        assert False, "Should have thrown 429 Too Many Requests"
    except Exception as exc:
        print(f"   • Success: Rate limit triggered as expected ({exc.detail})")

    # 2. Test Exponential Backoff with Jitter
    print("\n🔄 2. Testing Exponential Backoff & Retry Jitter:")
    call_counter = 0

    async def flaky_api_call():
        nonlocal call_counter
        call_counter += 1
        if call_counter < 3:
            raise ConnectionError("Simulated 503 Gateway Timeout")
        return {"status": "SUCCESS", "attempts": call_counter}

    start_time = time.perf_counter()
    result = await orchestrator.execute_with_retry(
        flaky_api_call, max_retries=3, base_delay=0.2
    )
    duration = time.perf_counter() - start_time

    print(f"   • Execution Result : {result}")
    print(f"   • Total Attempts   : {result['attempts']}")
    print(f"   • Total Recovery Time: {duration:.3f} seconds")

    assert result["status"] == "SUCCESS"
    assert result["attempts"] == 3

    print("\n" + "=" * 65)
    print("🎉 RESILIENT ORCHESTRATOR VERIFICATION PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_resilience_suite())