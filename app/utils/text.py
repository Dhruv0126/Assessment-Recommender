import re


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def detect_missing_slots(last_user_message: str, full_context: str) -> list[str]:
    text = f"{full_context} {last_user_message}".lower()
    missing = []

    role_hints = ["developer", "engineer", "analyst", "manager", "tester", "scientist", "role", "hiring"]
    seniority_hints = ["junior", "mid", "senior", "years", "experience", "fresher"]
    focus_hints = ["coding", "aptitude", "personality", "communication", "behavioral", "technical"]

    if not any(h in text for h in role_hints):
        missing.append("role")
    if not any(h in text for h in seniority_hints):
        missing.append("seniority")
    if not any(h in text for h in focus_hints):
        missing.append("assessment_focus")

    return missing


def is_out_of_scope(message: str) -> bool:
    m = message.lower()
    blocked_topics = [
        "salary",
        "ctc",
        "legal advice",
        "visa",
        "immigration",
        "medical",
        "stock market",
        "sports",
        "movie",
    ]
    return any(topic in m for topic in blocked_topics)
