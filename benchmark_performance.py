import time
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

sample_phishing_payload = {
    "id": "bench_msg_001",
    "thread_id": "thread_bench_001",
    "sender": "security-alert@tempmail-verify.com",
    "subject": "URGENT SECURITY ACTION REQUIRED: VERIFY YOUR ACCOUNT",
    "body_text": "CRITICAL NOTICE: Unauthorized activity detected. Verify credentials at http://bank-verify-login.com"
}

sample_summary_payload = {
    "thread_id": "thread_bench_101",
    "message_bodies": [
        "Hi Prabhu, please review the attached milestone checklist for tomorrow's project evaluation drive. Ensure that the updated FastAPI backend documentation and React dashboard live demo are completely prepared before 10:00 AM. Best regards, Prof. Sharma"
    ]
}

def benchmark_endpoint(name, url, method="POST", payload=None, runs=5):
    latencies = []
    print(f"\n--- Benchmarking {name} ({runs} runs) ---")
    
    for i in range(1, runs + 1):
        start_time = time.perf_counter()
        if method == "POST":
            response = requests.post(url, json=payload)
        else:
            response = requests.get(url)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(elapsed_ms)
        print(f"  Run {i}: Status {response.status_code} | Latency: {elapsed_ms:.2f} ms")
    
    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    print(f"Result for {name} -> Avg: {avg_latency:.2f} ms | Min: {min_latency:.2f} ms | Max: {max_latency:.2f} ms")
    return avg_latency

if __name__ == "__main__":
    print("==========================================================")
    print("     EasyMail AI Microservice Performance Benchmark     ")
    print("==========================================================")
    
    try:
        # 1. Health Check Benchmark
        benchmark_endpoint("Health Check (GET /)", "http://127.0.0.1:8000/", method="GET", runs=3)
        
        # 2. DistilBERT Threat Classification Benchmark
        threat_avg = benchmark_endpoint(
            "DistilBERT Threat Classification",
            f"{API_BASE_URL}/threats/analyze",
            payload=sample_phishing_payload,
            runs=5
        )
        
        # 3. T5 Summarization Benchmark
        summary_avg = benchmark_endpoint(
            "T5 Thread Summarizer",
            f"{API_BASE_URL}/ai/summarize",
            payload=sample_summary_payload,
            runs=5
        )
        
        print("\n==========================================================")
        print("                    BENCHMARK VERDICT                     ")
        print("==========================================================")
        print(f"DistilBERT Inference Target: < 300 ms  | Measured Avg: {threat_avg:.2f} ms [{'PASS' if threat_avg < 300 else 'FAIL'}]")
        print(f"T5 Summarizer Target:        < 1500 ms | Measured Avg: {summary_avg:.2f} ms [{'PASS' if summary_avg < 1500 else 'FAIL'}]")
        print("==========================================================")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to FastAPI server at http://127.0.0.1:8000.")
        print("Ensure Uvicorn is running: uvicorn app.main:app --reload --port 8000")