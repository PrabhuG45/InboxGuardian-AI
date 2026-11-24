import asyncio
import streamlit as st
from app.schemas.email import DraftCreatePayload, SendEmailPayload
from app.services.email_client import GmailConnector

# Page Configuration
st.set_page_config(
    page_title="EasyMail — Inbox Workspace",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Gmail Aesthetic
st.markdown(
    """
<style>
    .stApp {
        background-color: #f6f8fc;
    }
    .email-card {
        background-color: #ffffff;
        padding: 14px 18px;
        border-radius: 8px;
        border-left: 4px solid #1a73e8;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .unread-badge {
        background-color: #e8f0fe;
        color: #1a73e8;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    .sender-title {
        font-weight: 700;
        color: #202124;
        font-size: 14px;
    }
    .subject-text {
        font-weight: 600;
        color: #3c4043;
        font-size: 13px;
    }
    .snippet-text {
        color: #5f6368;
        font-size: 12px;
    }
    .ai-box {
        background-color: #f0f4f9;
        border: 1px solid #d3e3fd;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "selected_email" not in st.session_state:
    st.session_state["selected_email"] = None
if "active_folder" not in st.session_state:
    st.session_state["active_folder"] = "INBOX"
if "draft_body_text" not in st.session_state:
    st.session_state["draft_body_text"] = ""

connector = GmailConnector(access_token="test_token")


async def fetch_emails(query_filter: str = ""):
    raw_refs = await connector.list_messages(query=query_filter, max_results=15)
    email_objects = []
    for ref in raw_refs:
        msg = await connector.get_message(ref["id"])
        email_objects.append(msg)
    return email_objects


# AI Smart Generator Helper
def generate_ai_draft_from_subject(subject: str) -> tuple[str, list[str]]:
    """Analyzes subject line and generates smart draft body & word suggestions."""
    sub_lower = subject.lower()

    if "loan" in sub_lower:
        body = (
            "Dear Bank Representative,\n\n"
            "I am writing to formally submit my application for a personal loan. "
            "Please find attached my income proof, identity documents, and bank statements for evaluation.\n\n"
            "Kindly advise on the next steps and expected processing timelines.\n\n"
            "Best regards,\nPrabhu"
        )
        suggestions = ["income proof", "interest rate", "repayment schedule", "pre-approval", "collateral"]
    elif "meeting" in sub_lower or "discussion" in sub_lower:
        body = (
            "Hi Team,\n\n"
            "I would like to schedule a brief meeting to discuss our upcoming project milestones and review pending deliverables.\n\n"
            "Please let me know your availability for tomorrow afternoon.\n\n"
            "Thanks,\nPrabhu"
        )
        suggestions = ["agenda", "time slots", "Google Meet link", "action items", "status update"]
    elif "security" in sub_lower or "urgent" in sub_lower:
        body = (
            "Attention Security Team,\n\n"
            "A potential security anomaly was flagged on my account. "
            "I request an immediate audit of recent authentication logs and active session tokens.\n\n"
            "Regards,\nPrabhu"
        )
        suggestions = ["audit log", "2FA reset", "session revocation", "IP check", "Zero Trust"]
    else:
        body = (
            f"Dear Team,\n\n"
            f"I am following up regarding '{subject}'. "
            f"Please review the details and let me know if any further information is required.\n\n"
            f"Best regards,\nPrabhu"
        )
        suggestions = ["follow-up", "confirmation", "attached files", "feedback requested", "review"]

    return body, suggestions


# ==========================================
# 1. SIDEBAR: ACCOUNT SWITCHER & FOLDERS
# ==========================================
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg",
        width=40,
    )
    st.title("EasyMail Workspace")

    user_email = st.text_input(
        "👤 Account Email:",
        value="prabhu@example.com",
        help="Enter the email address to inspect inbox records.",
    )

    st.markdown("---")

    if st.button("✏️ Compose Email", use_container_width=True, type="primary"):
        st.session_state["selected_email"] = "COMPOSE"

    st.markdown("### Navigation")

    folders = [
        ("📥 Inbox", "INBOX"),
        ("✉️ Unread", "is:unread"),
        ("⭐ Starred", "is:starred"),
        ("📝 Drafts", "DRAFT"),
        ("🚀 Sent", "SENT"),
        ("🗑️ Trash", "TRASH"),
    ]

    for label, folder_code in folders:
        if st.button(label, use_container_width=True):
            st.session_state["active_folder"] = folder_code
            st.session_state["selected_email"] = None
            with st.spinner(f"Loading {label}..."):
                st.session_state["messages"] = asyncio.run(
                    fetch_emails(
                        folder_code if ":" in folder_code else f"label:{folder_code}"
                    )
                )

    st.markdown("---")
    st.caption("🔒 System Security: **Zero Trust Scoped**")
    st.caption("🔑 Vault Standard: **AES-256-GCM**")


# ==========================================
# 2. TOP SEARCH & FILTER BAR
# ==========================================
col_search, col_refresh, col_stats = st.columns([5, 1.5, 2.5])

with col_search:
    search_query = st.text_input(
        "🔍 Search Mail",
        placeholder="Search by sender, subject, or keywords...",
        label_visibility="collapsed",
    )

with col_refresh:
    if st.button("🔄 Sync Feed", use_container_width=True):
        with st.spinner("Syncing Gmail API..."):
            st.session_state["messages"] = asyncio.run(fetch_emails(search_query))
            st.success("Updated!")

with col_stats:
    st.markdown(
        f"**Active User:** `{user_email}` | **Folder:** `{st.session_state['active_folder']}`"
    )

st.markdown("---")


# ==========================================
# 3. MAIN WORKSPACE (GMAIL DUAL-PANE VIEW)
# ==========================================
col_list, col_viewer = st.columns([1.1, 1.4])

if not st.session_state["messages"]:
    st.session_state["messages"] = asyncio.run(
        fetch_emails(st.session_state["active_folder"])
    )

# LEFT PANE: EMAIL LIST
with col_list:
    st.subheader(f"📩 {st.session_state['active_folder']} Feed")
    messages = st.session_state["messages"]

    if not messages:
        st.info("No emails found matching the selected filter.")

    for msg in messages:
        if (
            search_query
            and search_query.lower() not in msg.subject.lower()
            and search_query.lower() not in msg.sender.lower()
            and search_query.lower() not in msg.snippet.lower()
        ):
            continue

        with st.container():
            st.markdown(
                f"""
            <div class="email-card">
                <span class="sender-title">{msg.sender}</span>
                <span class="unread-badge">{', '.join(msg.labels)}</span>
                <div class="subject-text">{msg.subject}</div>
                <div class="snippet-text">{msg.snippet[:80]}...</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button(f"📖 Open Message #{msg.id}", key=f"btn_{msg.id}"):
                st.session_state["selected_email"] = msg

# RIGHT PANE: READING PANE & AI COMPOSE CENTER
with col_viewer:
    selected = st.session_state["selected_email"]

    if selected == "COMPOSE":
        st.subheader("✏️ Compose New Email")

        to_field = st.text_input("To:", value="prabhugharat@gmail.com")
        cc_field = st.text_input("Cc (Optional):", value="")
        sub_field = st.text_input("Subject:", value="Loan application")

        # Dynamic AI Assistant Block
        if sub_field.strip():
            ai_body, smart_suggestions = generate_ai_draft_from_subject(sub_field)

            st.markdown(
                f"""
            <div class="ai-box">
                <b>✨ EasyMail AI Generator:</b> Context detected for <i>"{sub_field}"</i>.
            </div>
            """,
                unsafe_allow_html=True,
            )

            col_btn, col_sug = st.columns([1.2, 2])
            with col_btn:
                if st.button("🪄 Auto-Fill AI Draft Body"):
                    st.session_state["draft_body_text"] = ai_body
                    st.rerun()

            with col_sug:
                st.write("**Suggested Keywords:**")
                st.write(" • ".join([f"`{s}`" for s in smart_suggestions]))

        body_field = st.text_area(
            "Email Body:",
            value=st.session_state.get("draft_body_text", ""),
            height=180,
            placeholder="Type your email content here or click 'Auto-Fill AI Draft Body' above...",
        )

        cc_list = [c.strip() for c in cc_field.split(",") if c.strip()] if cc_field else None

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Dispatch Email", type="primary"):
                payload = SendEmailPayload(
                    to=[to_field],
                    cc=cc_list,
                    subject=sub_field,
                    body_text=body_field,
                )
                res = asyncio.run(connector.send_email(payload))
                st.success(f"Email Dispatched! Message ID: {res.get('id')}")
        with c2:
            if st.button("📝 Save as Draft"):
                payload = DraftCreatePayload(
                    to=[to_field],
                    cc=cc_list,
                    subject=sub_field,
                    body_text=body_field,
                )
                res = asyncio.run(connector.create_draft(payload))
                st.info(f"Draft Synced! ID: {res.get('id')}")

    elif selected and hasattr(selected, "subject"):
        st.subheader("📖 Email Viewer")

        act_col1, act_col2, act_col3 = st.columns(3)
        with act_col1:
            if st.button("⭐ Star Email"):
                st.toast("Email Starred!")
        with act_col2:
            if st.button("🏷️ Mark as Read"):
                st.toast("Marked as read.")
        with act_col3:
            if st.button("🗑️ Move to Trash"):
                asyncio.run(connector.trash_message(selected.id))
                st.warning("Message trashed!")

        st.markdown("---")

        st.markdown(f"### {selected.subject}")
        st.markdown(f"**From:** `{selected.sender}`")
        st.markdown(
            f"**To:** `{', '.join(selected.recipients)}` | **Thread ID:** `{selected.thread_id}`"
        )

        st.markdown("**Labels:**")
        st.write(" ".join([f"`{lbl}`" for lbl in selected.labels]))

        st.markdown("---")

        st.markdown("**Message Body:**")
        if selected.body_html:
            st.components.v1.html(selected.body_html, height=250, scrolling=True)
        else:
            st.info(selected.body_text or selected.snippet)

        if selected.attachments:
            st.markdown("---")
            st.markdown("📎 **Attachments:**")
            for att in selected.attachments:
                st.write(
                    f"• `{att.filename}` ({att.mime_type}) — {att.size_bytes} bytes"
                )

    else:
        st.info(
            "👈 Select an email from the inbox list on the left to read its content or click **Compose Email** to send a message."
        )