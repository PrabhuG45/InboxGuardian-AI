import asyncio
from sqlalchemy import select
from app.db.session import init_db, AsyncSessionLocal
from app.db.models import EncryptedTokenVaultModel, ThreatLogModel, AuditLogModel


async def test_persistence_pipeline():
    print("=" * 65)
    print("🧪 RUNNING EASYMAIL DATABASE PERSISTENCE SUITE")
    print("=" * 65)

    # 1. Initialize Tables
    await init_db()
    print("\n🗄️ 1. Database Schema Initialized (SQLite Async / PostgreSQL Ready)")

    async with AsyncSessionLocal() as session:
        # 2. Insert Encrypted Token Record
        token_entry = EncryptedTokenVaultModel(
            user_email="prabhu@example.com",
            encrypted_token="dGVzdF9jaXBoZXJ0ZXh0X2RhdGE=",
            nonce="OTYtYml0LW5vbmNl",
        )
        session.add(token_entry)

        # 3. Insert Threat Log Record
        threat_entry = ThreatLogModel(
            message_id="msg_phish_999",
            sender="suspicious@login-bank.com",
            overall_threat_level="CRITICAL",
            primary_category="PHISHING",
            confidence_score=0.985,
            phishing_probability=0.985,
            spam_probability=0.012,
            flagged_indicators=["Domain mismatch", "High urgency phrasing"],
            extracted_urls=["http://login-verify-bank.com"],
            recommended_action="QUARANTINE_IMMEDIATELY",
        )
        session.add(threat_entry)

        # 4. Insert Audit Log
        audit_entry = AuditLogModel(
            user_email="prabhu@example.com",
            action="API_MSG_READ",
            scopes_used=["email:read"],
            client_ip="127.0.0.1",
        )
        session.add(audit_entry)

        await session.commit()
        print("✅ 2. Sample Vault Token, Threat Log, and Audit Log Persisted")

    # 5. Query and Assert Records
    async with AsyncSessionLocal() as session:
        stmt_vault = select(EncryptedTokenVaultModel).where(
            EncryptedTokenVaultModel.user_email == "prabhu@example.com"
        )
        res_vault = (await session.execute(stmt_vault)).scalar_one_or_none()
        assert res_vault is not None
        assert res_vault.encrypted_token == "dGVzdF9jaXBoZXJ0ZXh0X2RhdGE="

        stmt_threat = select(ThreatLogModel).where(
            ThreatLogModel.message_id == "msg_phish_999"
        )
        res_threat = (await session.execute(stmt_threat)).scalar_one_or_none()
        assert res_threat is not None
        assert res_threat.overall_threat_level == "CRITICAL"

        print("\n🔍 3. Record Query & Integrity Verifications:")
        print(f"   • Stored Vault User  : {res_vault.user_email}")
        print(f"   • Query Threat Level : {res_threat.overall_threat_level}")
        print(f"   • Extracted URL      : {res_threat.extracted_urls[0]}")

    print("\n" + "=" * 65)
    print("🎉 DATABASE PERSISTENCE VERIFICATION PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_persistence_pipeline())