import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("learner_data")
DATA_DIR.mkdir(exist_ok=True)


def _safe_key(subject: str, topic: str) -> str:
    combined = f"{subject}_{topic}"
    return "".join(c if c.isalnum() or c in "_- " else "_" for c in combined).replace(" ", "_")


def _progress_path(subject: str, topic: str) -> Path:
    return DATA_DIR / f"{_safe_key(subject, topic)}_progress.json"


def _history_path(subject: str, topic: str) -> Path:
    return DATA_DIR / f"{_safe_key(subject, topic)}_history.json"


# ── Progress ──────────────────────────────────────────────────────────────────

def load_progress(subject: str, topic: str) -> dict:
    path = _progress_path(subject, topic)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"sessions": 0, "quizzes_taken": 0, "correct": 0}


def save_progress(subject: str, topic: str, data: dict):
    path = _progress_path(subject, topic)
    data["subject"] = subject
    data["topic"]   = topic
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ── Chat History ──────────────────────────────────────────────────────────────

def load_chat_history(subject: str, topic: str) -> list:
    path = _history_path(subject, topic)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def add_chat_message(subject: str, topic: str, agent: str, user_input: str, agent_output: str):
    history = load_chat_history(subject, topic)
    history.append({
        "agent":        agent,
        "user_input":   user_input,
        "agent_output": agent_output,
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    path = _history_path(subject, topic)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


# ── Manage topics ─────────────────────────────────────────────────────────────

def get_all_topics() -> list:
    topics = set()
    for path in DATA_DIR.glob("*_progress.json"):
        try:
            with open(path) as f:
                data = json.load(f)
            subj  = data.get("subject", "")
            topic = data.get("topic", "")
            if subj and topic:
                topics.add(f"{subj} → {topic}")
        except Exception:
            pass
    return sorted(topics)


def clear_topic_data(subject: str, topic: str):
    for path in [_progress_path(subject, topic), _history_path(subject, topic)]:
        if path.exists():
            path.unlink()
