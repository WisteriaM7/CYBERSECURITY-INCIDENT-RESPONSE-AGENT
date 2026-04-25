import streamlit as st
from agents import run_agent
from storage import (
    load_progress, save_progress, add_chat_message,
    load_chat_history, clear_topic_data, get_all_topics,
)
from quiz import parse_quiz, evaluate_answer

st.set_page_config(page_title="Learning Coach", page_icon="🎓", layout="wide")


# ── Helper ────────────────────────────────────────────────────────────────────

def build_context(subject: str, topic: str, progress: dict) -> str:
    sessions = progress.get("sessions", 0)
    quizzes  = progress.get("quizzes_taken", 0)
    correct  = progress.get("correct", 0)
    pct      = int((correct / quizzes) * 100) if quizzes > 0 else 0
    return (
        f"Subject: {subject}. Topic: {topic}. "
        f"Student stats — Sessions: {sessions}, "
        f"Quizzes taken: {quizzes}, Quiz score: {pct}%."
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🎓 Learning Coach")
    st.divider()

    model   = st.text_input("Ollama Model", value="llama3")
    subject = st.text_input("Subject", value="Python Programming")
    topic   = st.text_input("Topic",   value="Functions and Recursion")

    st.divider()
    st.subheader("📊 Your Progress")
    progress    = load_progress(subject, topic)
    total_q     = progress.get("quizzes_taken", 0)
    correct_all = progress.get("correct", 0)
    score_pct   = int((correct_all / total_q) * 100) if total_q > 0 else 0

    st.metric("Study Sessions",   progress.get("sessions", 0))
    st.metric("Quizzes Taken",    total_q)
    st.metric("Correct Answers",  correct_all)
    st.progress(score_pct / 100, text=f"Overall Quiz Score: {score_pct}%")

    st.divider()
    st.subheader("📂 Topics Studied")
    all_topics = get_all_topics()
    if all_topics:
        for t in all_topics:
            st.caption(f"• {t}")
    else:
        st.caption("None yet.")

    st.divider()
    if st.button("🗑️ Reset This Topic", use_container_width=True):
        clear_topic_data(subject, topic)
        st.success("Topic data cleared.")
        st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────

st.title(f"📖 {subject} — {topic}")

tab_explain, tab_quiz, tab_motivate, tab_history = st.tabs([
    "🧠 Explainer", "❓ Quiz", "💪 Motivation", "📜 History",
])


# ── TAB 1: Explainer ──────────────────────────────────────────────────────────

with tab_explain:
    st.subheader("🧠 Explainer Agent")
    st.caption("Ask anything. The agent simplifies concepts for your level.")

    question = st.text_area(
        "What would you like explained?",
        placeholder=f"e.g. Explain {topic} with a real-world example",
        height=100,
        key="explain_q",
    )
    level = st.selectbox("Your level", ["Beginner", "Intermediate", "Advanced"], key="explain_level")

    if st.button("💡 Explain It", use_container_width=True, key="btn_explain"):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Thinking..."):
                ctx    = build_context(subject, topic, progress)
                output = run_agent("Explainer", question, subject, topic, level, ctx, model)
            st.markdown(output)
            add_chat_message(subject, topic, "Explainer", question, output)
            progress["sessions"] = progress.get("sessions", 0) + 1
            save_progress(subject, topic, progress)
            st.rerun()


# ── TAB 2: Quiz ───────────────────────────────────────────────────────────────

with tab_quiz:
    st.subheader("❓ Quiz Agent")
    st.caption("Test your knowledge with AI-generated questions.")

    col1, col2, col3 = st.columns(3)
    num_q  = col1.slider("Questions", 1, 5, 3, key="num_q")
    q_type = col2.selectbox("Type", ["Multiple Choice", "True/False", "Short Answer"], key="q_type")
    q_diff = col3.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="q_diff")

    if st.button("📝 Generate Quiz", use_container_width=True, key="btn_quiz"):
        with st.spinner("Building quiz..."):
            ctx          = build_context(subject, topic, progress)
            prompt_extra = f"{num_q} {q_type} questions at {q_diff} difficulty"
            output       = run_agent("Quiz", prompt_extra, subject, topic, q_diff, ctx, model)
        st.session_state["quiz_raw"]       = output
        st.session_state["quiz_parsed"]    = parse_quiz(output)
        st.session_state["quiz_answers"]   = {}
        st.session_state["quiz_submitted"] = False
        add_chat_message(subject, topic, "Quiz", prompt_extra, output)
        st.rerun()

    # Active quiz
    if st.session_state.get("quiz_parsed") and not st.session_state.get("quiz_submitted"):
        questions = st.session_state["quiz_parsed"]
        st.divider()

        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            if q["type"] == "mcq" and q.get("options"):
                ans = st.radio("", q["options"], key=f"qa_{i}", index=None, label_visibility="collapsed")
            else:
                ans = st.text_input("Your answer:", key=f"qa_{i}")
            st.session_state["quiz_answers"][i] = ans

        if st.button("✅ Submit Answers", use_container_width=True, key="btn_submit"):
            st.session_state["quiz_submitted"] = True
            st.rerun()

    # Results
    if st.session_state.get("quiz_submitted"):
        questions     = st.session_state.get("quiz_parsed", [])
        answers       = st.session_state.get("quiz_answers", {})
        correct_count = 0

        st.divider()
        st.subheader("📊 Results")

        for i, q in enumerate(questions):
            user_ans   = answers.get(i, "")
            is_correct = evaluate_answer(q, user_ans)
            if is_correct:
                correct_count += 1
                st.success(f"✅ Q{i+1}. {q['question']}")
            else:
                st.error(f"❌ Q{i+1}. {q['question']}")
                if q.get("answer"):
                    st.caption(f"Correct answer: {q['answer']}")

        if questions:
            progress["quizzes_taken"] = progress.get("quizzes_taken", 0) + len(questions)
            progress["correct"]       = progress.get("correct", 0) + correct_count
            save_progress(subject, topic, progress)

            pct = int((correct_count / len(questions)) * 100)
            st.metric("Your Score", f"{correct_count}/{len(questions)}  ({pct}%)")

            if pct >= 80:
                st.balloons()
                st.success("🎉 Excellent! You're really getting the hang of this.")
            elif pct >= 50:
                st.info("👍 Good effort! A bit more practice and you'll nail it.")
            else:
                st.warning("📖 Keep going! Head to the Explainer tab to review the concepts.")

        if st.button("🔄 Try Another Quiz", use_container_width=True, key="btn_newquiz"):
            for key in ["quiz_raw", "quiz_parsed", "quiz_answers", "quiz_submitted"]:
                st.session_state.pop(key, None)
            st.rerun()


# ── TAB 3: Motivation ─────────────────────────────────────────────────────────

with tab_motivate:
    st.subheader("💪 Motivation Agent")
    st.caption("Get encouragement, study strategies, and a personalised learning plan.")

    motivation_type = st.selectbox("What do you need?", [
        "General encouragement",
        "I'm stuck and frustrated",
        "Study strategy advice",
        "Personalised learning plan",
        "Review my progress and give feedback",
    ], key="motiv_type")

    extra_note = st.text_input(
        "Anything to add? (optional)",
        placeholder="e.g. I have an exam in 3 days",
        key="motiv_extra",
    )

    if st.button("🌟 Get Support", use_container_width=True, key="btn_motivate"):
        with st.spinner("Personalising your message..."):
            ctx    = build_context(subject, topic, progress)
            prompt = f"{motivation_type}. {extra_note}".strip(" .")
            output = run_agent("Motivation", prompt, subject, topic, "", ctx, model)
        st.markdown(output)
        add_chat_message(subject, topic, "Motivation", prompt, output)


# ── TAB 4: History ────────────────────────────────────────────────────────────

with tab_history:
    st.subheader("📜 Session History")
    history = load_chat_history(subject, topic)

    if not history:
        st.info("No history yet for this topic. Start studying!")
    else:
        icons = {"Explainer": "🧠", "Quiz": "❓", "Motivation": "💪"}
        for entry in reversed(history):
            agent = entry.get("agent", "")
            ts    = entry.get("timestamp", "")
            q     = entry.get("user_input", "")
            a     = entry.get("agent_output", "")
            icon  = icons.get(agent, "🤖")
            with st.expander(f"{icon} {agent} — {ts}", expanded=False):
                st.markdown(f"**You:** {q}")
                st.divider()
                st.markdown(a)
