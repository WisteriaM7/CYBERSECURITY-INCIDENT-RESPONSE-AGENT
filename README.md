# 🎓 Agent-Guided Learning Coach

A Streamlit app with three AI agents that act as your personal tutor, quiz master, and motivational coach — all powered by a local LLM via Ollama.

## Agents

| Agent | Role |
|---|---|
| 🧠 **Explainer** | Simplifies concepts at your level with examples & analogies |
| ❓ **Quiz** | Generates MCQ, True/False, or Short Answer questions and grades them |
| 💪 **Motivation** | Gives encouragement, study plans, and personalised feedback |

---

## Project Structure

```
learning_coach/
├── app.py              # Streamlit UI (4 tabs)
├── agents.py           # Agent prompts + runner
├── quiz.py             # Quiz parser and answer evaluator
├── storage.py          # Progress tracking + chat history per topic
├── ollama_client.py    # Ollama HTTP client
├── requirements.txt
└── learner_data/       # Auto-created JSON files per topic
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and run Ollama

```bash
# Download from https://ollama.com
ollama pull llama3      # or mistral, phi3, gemma2, etc.
ollama serve
```

### 3. Run the app

```bash
streamlit run app.py
```

---

## How to Use

1. **Set Subject & Topic** in the sidebar (e.g. Subject: Biology, Topic: Cell Division)
2. Pick your **Ollama model** in the sidebar

### 🧠 Explainer Tab
- Type any question about the topic
- Choose your level (Beginner / Intermediate / Advanced)
- Get a structured explanation with examples and a key takeaway

### ❓ Quiz Tab
- Choose number of questions, type, and difficulty
- Answer each question in the UI
- Submit to see instant results with scoring
- Progress is saved automatically

### 💪 Motivation Tab
- Choose what kind of support you need
- Get personalised encouragement, a study plan, or strategic advice

### 📜 History Tab
- Review all past interactions for the current topic

---

## Progress Tracking

For each subject + topic combination the app saves:
- Number of study sessions
- Total quiz questions attempted
- Total correct answers
- Full chat history

Data is stored in `learner_data/` as JSON files. Use "Reset This Topic" in the sidebar to clear it.

---

## Notes

- No internet or API keys needed — fully local via Ollama
- Works with any Ollama model; `llama3` recommended for best quality
- Switch topics freely in the sidebar — each topic has its own memory
