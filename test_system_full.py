import sys
import requests

API_BASE_URL = "http://127.0.0.1:8000/api/v1"
ROOT_URL = "http://127.0.0.1:8000"

# Authorized headers matching backend dev token bypass
AUTH_HEADERS = {
    "Authorization": "Bearer mock_zero_trust_jwt_token_2026",
    "Content-Type": "application/json"
}

def log_test(name, passed, details=""):
    status = "\033[92m[PASS]\033[0m" if passed else "\033[91m[FAIL]\033[0m"
    print(f"  {status} {name}")
    if details and not passed:
        print(f"         Error Details: {details}")

def run_integration_tests():
    print("==========================================================")
    print("      EasyMail Full System Integration Test Suite         ")
    print("==========================================================\n")
    
    passed_count = 0
    total_tests = 0

    # 1. Root Health Check Endpoint
    total_tests += 1
    try:
        res = requests.get(f"{ROOT_URL}/")
        if res.status_code == 200 and res.json().get("status") == "online":
            log_test("Root Health Check Endpoint (GET /)", True)
            passed_count += 1
        else:
            log_test("Root Health Check Endpoint (GET /)", False, f"Unexpected response: {res.text}")
    except Exception as e:
        log_test("Root Health Check Endpoint (GET /)", False, str(e))

    # 2. DistilBERT Security Inference
    total_tests += 1
    phishing_payload = {
        "id": "test_phish_001",
        "thread_id": "thread_001",
        "sender": "security-alert@tempmail-verify.com",
        "subject": "URGENT ACTION: VERIFY ACCOUNT",
        "body_text": "Verify credentials immediately at http://bank-verify-login.com"
    }
    try:
        res = requests.post(f"{API_BASE_URL}/threats/analyze", json=phishing_payload, headers=AUTH_HEADERS)
        data = res.json()
        if res.status_code == 200 and data.get("overall_threat_level") == "CRITICAL":
            log_test("DistilBERT Phishing Threat Analysis (POST /threats/analyze)", True)
            passed_count += 1
        else:
            log_test("DistilBERT Phishing Threat Analysis (POST /threats/analyze)", False, f"Response: {data}")
    except Exception as e:
        log_test("DistilBERT Phishing Threat Analysis (POST /threats/analyze)", False, str(e))

    # 3. Threat Quarantine Action
    total_tests += 1
    try:
        res = requests.post(f"{API_BASE_URL}/threats/quarantine/test_phish_001", headers=AUTH_HEADERS)
        data = res.json()
        if res.status_code == 200 and data.get("action_taken") == "QUARANTINED":
            log_test("Threat Quarantine Isolation (POST /threats/quarantine/{id})", True)
            passed_count += 1
        else:
            log_test("Threat Quarantine Isolation (POST /threats/quarantine/{id})", False, f"Response: {data}")
    except Exception as e:
        log_test("Threat Quarantine Isolation (POST /threats/quarantine/{id})", False, str(e))

    # 4. False Positive Override Action
    total_tests += 1
    try:
        res = requests.post(f"{API_BASE_URL}/threats/mark-safe/test_phish_001", headers=AUTH_HEADERS)
        data = res.json()
        if res.status_code == 200 and data.get("action_taken") == "MARKED_SAFE":
            log_test("Threat Override / Mark Safe (POST /threats/mark-safe/{id})", True)
            passed_count += 1
        else:
            log_test("Threat Override / Mark Safe (POST /threats/mark-safe/{id})", False, f"Response: {data}")
    except Exception as e:
        log_test("Threat Override / Mark Safe (POST /threats/mark-safe/{id})", False, str(e))

    # 5. T5 Executive Thread Summarizer
    total_tests += 1
    summary_payload = {
        "thread_id": "thread_demo_100",
        "message_bodies": ["Hi team, please complete the final FastAPI and React project documentation."]
    }
    try:
        res = requests.post(f"{API_BASE_URL}/ai/summarize", json=summary_payload, headers=AUTH_HEADERS)
        data = res.json()
        if res.status_code in [200, 201] and ("concise_digest" in data or "summary" in data or "bullet_points" in data or "digest" in data):
            log_test("T5 Executive Thread Summarization (POST /ai/summarize)", True)
            passed_count += 1
        else:
            log_test("T5 Executive Thread Summarization (POST /ai/summarize)", False, f"Status: {res.status_code} | Response: {data}")
    except Exception as e:
        log_test("T5 Executive Thread Summarization (POST /ai/summarize)", False, str(e))

    # 6. Outbound Email Dispatch Service
    total_tests += 1
    email_payload = {
        "recipients": ["prof.sharma@university.edu"],
        "subject": "Final Project Evaluation Deliverables Ready",
        "body_text": "Dear Professor, all backend services and UI components are operational."
    }
    try:
        res = requests.post(f"{API_BASE_URL}/email/send", json=email_payload, headers=AUTH_HEADERS)
        if res.status_code in [200, 201]:
            log_test("Outbound Email Dispatch (POST /email/send)", True)
            passed_count += 1
        else:
            log_test("Outbound Email Dispatch (POST /email/send)", False, f"Status: {res.status_code} | Response: {res.text}")
    except Exception as e:
        log_test("Outbound Email Dispatch (POST /email/send)", False, str(e))

    print("\n==========================================================")
    print(f"  INTEGRATION TEST SUMMARY: {passed_count}/{total_tests} PASSED")
    print("==========================================================")
    
    if passed_count != total_tests:
        sys.exit(1)

if __name__ == "__main__":
    run_integration_tests()