import os
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://assessment-recommender-nzl3.onrender.com"
).rstrip("/")
REQUEST_TIMEOUT_SECONDS = 30


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = []
    if "api_status" not in st.session_state:
        st.session_state.api_status = "unknown"
    if "latest_reply" not in st.session_state:
        st.session_state.latest_reply = ""
    if "end_of_conversation" not in st.session_state:
        st.session_state.end_of_conversation = False


def check_health() -> str:
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "ok":
            return "online"
        return "degraded"
    except requests.RequestException:
        return "offline"


def post_chat(messages: list[dict[str, str]]) -> dict[str, Any]:
    payload = {"messages": messages}
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def render_health_badge(status: str) -> None:
    if status == "online":
        st.success(f"Backend status: {status}")
    elif status == "degraded":
        st.warning(f"Backend status: {status}")
    else:
        st.error(f"Backend status: {status}")


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.recommendations = []
    st.session_state.latest_reply = ""
    st.session_state.end_of_conversation = False


def render_chat() -> None:
    st.subheader("Conversation")
    if not st.session_state.messages:
        st.info("Start by describing the role, skills, and seniority you are hiring for.")
        return

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def render_recommendations() -> None:
    st.subheader("Recommended Assessments")
    recs = st.session_state.recommendations
    if not recs:
        st.caption("Recommendations will appear after the assistant has enough information.")
        return

    for rec in recs:
        with st.container(border=True):
            st.markdown(f"**{rec.get('name', 'Unknown assessment')}**")
            st.write(f"Test type: {rec.get('test_type', 'N/A')}")
            description = rec.get("description")
            if description:
                st.write(description)
            duration = rec.get("duration")
            category = rec.get("category")
            skills = rec.get("skills_measured") or []
            if duration:
                st.caption(f"Duration: {duration}")
            if category:
                st.caption(f"Category: {category}")
            if skills:
                st.caption(f"Skills measured: {', '.join(skills)}")
            url = rec.get("url")
            if url:
                st.link_button("View in catalog", url)


def main() -> None:
    st.set_page_config(page_title="SHL Assessment Recommender", page_icon=":mag:", layout="wide")
    init_session_state()

    st.title("SHL Assessment Recommender")
    st.caption(
        "Describe your hiring need. The assistant will clarify requirements and suggest the best-fit SHL assessments."
    )

    st.session_state.api_status = check_health()

    col_chat, col_recs = st.columns([2, 1], gap="large")

    with col_chat:
        render_health_badge(st.session_state.api_status)
        if st.button("Reset conversation", use_container_width=False):
            reset_conversation()
            st.rerun()

        render_chat()

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Your message", placeholder="Need assessments for a mid-level Java developer...")
            submitted = st.form_submit_button("Send")

        if submitted and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input.strip()})

            if st.session_state.api_status == "offline":
                st.error("Backend is offline. Start FastAPI and try again.")
                st.rerun()

            try:
                data = post_chat(st.session_state.messages)
                reply = data.get("reply", "I could not generate a response.")
                recommendations = data.get("recommendations", [])
                end_flag = bool(data.get("end_of_conversation", False))

                st.session_state.latest_reply = reply
                st.session_state.recommendations = recommendations
                st.session_state.end_of_conversation = end_flag
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except requests.HTTPError as exc:
                st.error(f"Chat request failed: {exc}")
            except requests.RequestException as exc:
                st.error(f"Could not connect to backend: {exc}")

        if st.session_state.end_of_conversation:
            st.info("Conversation marked complete. You can refine further or reset to start a new one.")

    with col_recs:
        render_recommendations()


if __name__ == "__main__":
    main()
