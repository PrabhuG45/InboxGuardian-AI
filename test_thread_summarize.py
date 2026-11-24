import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)


def test_summarization_pipeline():
    print("=" * 65)
    print("🧪 RUNNING EASYMAIL T5 THREAD SUMMARIZATION SUITE")
    print("=" * 65)

    valid_jwt = create_access_token(
        subject="prabhu@example.com",
        claims={
            "jti": str(uuid.uuid4()),
            "scopes": ["email:read"],
        },
    )
    headers = {"Authorization": f"Bearer {valid_jwt}"}

    sample_thread = {
        "thread_id": "thread_demo_99",
        "message_bodies": [
            "Hi team, please review the attached slides for tomorrow's project evaluation.",
            "I checked the slides. Kindly update the performance benchmark numbers in slide 4.",
            "Updated the benchmark figures. Please confirm if everything looks ready for submission.",
        ],
    }

    res = client.post("/api/v1/ai/summarize", json=sample_thread, headers=headers)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"

    data = res.json()
    print("\n📝 1. Summarization Output:")
    print(f"   • Thread ID        : {data['thread_id']}")
    print(f"   • Concise Digest   : {data['concise_digest']}")
    print(f"   • Bullet Points    : {data['bullet_points']}")
    print(f"   • Action Items     : {data['action_items']}")
    print(f"   • Message Count    : {data['participant_count']}")

    assert data["participant_count"] == 3
    assert len(data["action_items"]) > 0

    print("\n" + "=" * 65)
    print("🎉 T5 SUMMARIZATION PIPELINE VERIFICATION PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    test_summarization_pipeline()