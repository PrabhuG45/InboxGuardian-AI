# InboxGuardian AI (EasyMail)

**Smarter Inbox. Safer Communication. Powered by AI.**

InboxGuardian AI is an intelligent email management and cybersecurity assistant that wraps Gmail in a Zero-Trust security layer and pairs real-time NLP threat detection with generative writing assistance.

## Phase 1 Features
- **Zero-Trust OAuth 2.0 & AES-256-GCM Vault:** Passwordless Google Sign-In with CSRF `state` nonces, scoped JWT verification, and encrypted refresh-token storage.
- **Concurrent Gmail Sync:** Async REST integration across `Inbox`, `Starred`, `Sent`, `Drafts`, and `Trash` with MIME/HTML body extraction and attachment parsing.
- **Intelligent Threat Detection:** Semantic phishing and anomaly scoring powered by `DistilBERT` with confidence badges and one-click quarantine.
- **Abstractive Thread Summarization:** Condenses long email threads into concise digests using `T5`.
- **AI Writing Co-Writer:** Subject-triggered draft synthesis and inline ghost-text autocomplete inside the React compose modal.

## Tech Stack
- **Frontend:** React 19, Vite, Tailwind CSS, Axios, Lucide React
- **Backend & Security:** Python, FastAPI, Uvicorn, Pydantic v2, Async HTTPX, Google OAuth 2.0, JWT (`python-jose`), AES-256-GCM
- **AI / ML:** PyTorch, Hugging Face Transformers (`distilbert-base-uncased`, `t5-small`)

## Local Setup
1. Copy `.env.example` to `.env` and fill in your Google OAuth credentials, `SECRET_KEY`, and `AES_ENCRYPTION_KEY`.
2. **Backend:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
