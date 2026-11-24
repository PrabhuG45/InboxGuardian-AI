import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)


def test_threat_detection_pipeline():
    print("=" * 65)
    print("🧪 RUNNING EASYMAIL PHASE 2 THREAT DETECTION SUITE")
    print("=" * 65)

    # 1. Generate Zero Trust Access Token with required scope
    valid_jwt = create_access_token(
        subject="prabhu@example.com",
        claims={
            "jti": str(uuid.uuid4()),
            "scopes": ["email:read", "email:send"],
        },
    )
    headers = {"Authorization": f"Bearer {valid_jwt}"}

    # 2. Test Benign Email Analysis
    benign_payload = {
        "id": "msg_benign_001",
        "thread_id": "thread_001",
        "sender": "prof.sharma@university.edu",
        "recipients": ["prabhu@example.com"],
        "subject": "Project Progress Review Schedule",
        "body_text": "Hi Prabhu, please send over the updated slides for the project evaluation tomorrow.",
        "snippet": "Hi Prabhu, please send over...",
        "labels": ["INBOX"],
    }

    res = client.post("/api/v1/threats/analyze", json=benign_payload, headers=headers)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()

    print("\n✅ 1. Benign Email Evaluation:")
    print(f"   • Primary Category : {data['primary_category']}")
    print(f"   • Overall Level    : {data['overall_threat_level']}")
    print(f"   • Action           : {data['recommended_action']}")
    assert data["overall_threat_level"] in ["SAFE", "SUSPICIOUS"]

    # 3. Test High-Risk Phishing Email Analysis
    phishing_payload = {
        "id": "msg_phish_002",
        "thread_id": "thread_002",
        "sender": "security-alert@tempmail.com",
        "recipients": ["prabhu@example.com"],
        "subject": "URGENT SECURITY ACTION REQUIRED: VERIFY YOUR ACCOUNT IMMEDIATELY",
        "body_text": "Unauthorized activity detected. Please click http://bank-verify-login.com to verify your account or wire transfer.",
        "snippet": "Unauthorized activity detected...",
        "labels": ["INBOX", "UNREAD"],
    }

    res = client.post("/api/v1/threats/analyze", json=phishing_payload, headers=headers)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()

    print("\n⚠️ 2. Phishing Email Evaluation:")
    print(f"   • Primary Category  : {data['primary_category']}")
    print(f"   • Threat Level      : {data['overall_threat_level']}")
    print(f"   • Extracted URLs    : {data['extracted_urls']}")
    print(f"   • Flagged Signals   : {data['flagged_indicators']}")
    print(f"   • Recommended Action: {data['recommended_action']}")

    assert data["overall_threat_level"] in ["SUSPICIOUS", "CRITICAL"]
    assert len(data["flagged_indicators"]) > 0

    # 4. Test Zero Trust Enforcement (Missing Scopes)
    no_scope_jwt = create_access_token(
        subject="attacker@example.com",
        claims={"jti": str(uuid.uuid4()), "scopes": ["email:draft"]},
    )
    forbidden_res = client.post(
        "/api/v1/threats/analyze",
        json=benign_payload,
        headers={"Authorization": f"Bearer {no_scope_jwt}"},
    )

    print("\n🛡️ 3. Zero Trust Security Guard Test:")
    print(f"   • Status Code: {forbidden_res.status_code} (Expected 403 Forbidden)")
    assert forbidden_res.status_code == 403

    print("\n" + "=" * 65)
    print("🎉 ALL PHASE 2 THREAT PIPELINE VERIFICATIONS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    test_threat_detection_pipeline()