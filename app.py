"""
Streamlit frontend for the Startup Copilot.

Talks to the FastAPI backend over HTTP only (see src/api/main.py) — this
file has no direct imports from src.pipeline or src.mentorship. That
separation is the point of Phase 4: the UI can be swapped for anything
else without touching the AI logic at all.

Run the backend first:  uvicorn src.api.main:app --reload
Then run this:           streamlit run app.py
"""

import time

import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8123"

st.set_page_config(page_title="Startup Copilot", page_icon="🧭", layout="wide")

if "profile_id" not in st.session_state:
    st.session_state.profile_id = None
if "profile" not in st.session_state:
    st.session_state.profile = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def poll_until_done(profile_id: str, placeholder) -> dict | None:
    while True:
        resp = requests.get(f"{API_BASE}/profile/{profile_id}")
        data = resp.json()
        if data["status"] == "done":
            return data["profile"]
        if data["status"] == "failed":
            placeholder.error(f"Build failed: {data.get('error')}")
            return None
        placeholder.info(f"Status: {data['status'].replace('_', ' ')}...")
        time.sleep(2)


st.title("🧭 Startup Copilot")
st.caption("Submit your startup's links, get a grounded profile, then ask for mentorship.")

if st.session_state.profile is None:
    with st.form("intake_form"):
        st.subheader("Submit your links")
        github_url = st.text_input("GitHub repo")
        website_url = st.text_input("Website")
        pitch_deck_url = st.text_input("Pitch deck (direct PDF link)")
        social_url = st.text_input("Social media profile")
        submitted = st.form_submit_button("Build my profile")

    if st.button("Or load the demo profile"):
        resp = requests.get(f"{API_BASE}/profile/demo")
        if resp.status_code == 200 and resp.json()["status"] == "done":
            st.session_state.profile_id = "demo"
            st.session_state.profile = resp.json()["profile"]
            st.rerun()
        else:
            st.error("Demo profile not found — run `python -m src.mock_data` first.")

    if submitted:
        urls = {
            "github_url": github_url or None,
            "website_url": website_url or None,
            "pitch_deck_url": pitch_deck_url or None,
            "social_url": social_url or None,
        }
        if not any(urls.values()):
            st.error("Provide at least one link.")
        else:
            resp = requests.post(f"{API_BASE}/profile", json=urls)
            if resp.status_code != 200:
                st.error(f"Could not start build: {resp.text}")
            else:
                profile_id = resp.json()["profile_id"]
                st.session_state.profile_id = profile_id
                placeholder = st.empty()
                profile = poll_until_done(profile_id, placeholder)
                if profile:
                    st.session_state.profile = profile
                    st.rerun()

else:
    profile = st.session_state.profile

    with st.sidebar:
        st.header(profile.get("company_name") or "Unnamed startup")
        st.write(profile.get("one_line_summary") or "")
        if st.button("Start over"):
            st.session_state.profile_id = None
            st.session_state.profile = None
            st.session_state.chat_history = []
            st.rerun()

        with st.expander("Technical"):
            st.json(profile["technical"])
        with st.expander("Product"):
            st.json(profile["product"])
        with st.expander("Pitch"):
            st.json(profile["pitch"])
        with st.expander("Social"):
            st.json(profile["social"])
        with st.expander(f"Evidence log ({len(profile['evidence_log'])})"):
            for e in profile["evidence_log"]:
                st.caption(f"[{e['source']}] {e['claim']}")

    st.subheader("Chat with your mentor")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("specialists"):
                st.caption(f"Answered by: {', '.join(msg['specialists'])}")

    question = st.chat_input("Ask for feedback or advice...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
            resp = requests.post(
                f"{API_BASE}/chat",
                json={"profile_id": st.session_state.profile_id, "question": question},
            )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.chat_history.append(
                {"role": "assistant", "content": data["reply"], "specialists": data["specialists_used"]}
            )
        else:
            st.session_state.chat_history.append(
                {"role": "assistant", "content": f"Error: {resp.json().get('detail')}"}
            )
        st.rerun()
