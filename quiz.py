import re


def parse_quiz(raw_text: str) -> list:
    """
    Parse quiz output from the Quiz Agent into a list of question dicts.
    Handles: Multiple Choice, True/False, Short Answer
    """
    questions = []
    lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]

    current_q = None

    for line in lines:
        # New question line: Q1. or 1. or Q1)
        if re.match(r"^Q?\d+[\.\)]\s+", line, re.IGNORECASE):
            if current_q:
                questions.append(current_q)
            question_text = re.sub(r"^Q?\d+[\.\)]\s+", "", line, flags=re.IGNORECASE)
            current_q = {
                "question": question_text,
                "type": "short",
                "options": [],
                "answer": "",
            }

        # MCQ option line: A) or A. or a)
        elif re.match(r"^[A-Da-d][\.\)]\s+", line) and current_q:
            current_q["type"] = "mcq"
            current_q["options"].append(line)

        # Answer line
        elif re.match(r"^Answer\s*[:]\s*", line, re.IGNORECASE) and current_q:
            answer_val = re.sub(r"^Answer\s*[:]\s*", "", line, flags=re.IGNORECASE).strip()
            current_q["answer"] = answer_val

            # Detect True/False
            if answer_val.lower() in ("true", "false"):
                current_q["type"] = "truefalse"
                current_q["options"] = ["True", "False"]

    if current_q:
        questions.append(current_q)

    return questions


def evaluate_answer(question: dict, user_answer: str) -> bool:
    """
    Compare user answer to the correct answer.
    Returns True if correct.
    """
    if not user_answer or not question.get("answer"):
        return False

    correct = question["answer"].strip().lower()
    user    = user_answer.strip().lower()

    q_type = question.get("type", "short")

    if q_type == "mcq":
        # Match by letter: "A" matches "A) some text"
        correct_letter = correct[0] if correct else ""
        user_letter    = user[0] if user else ""
        return correct_letter == user_letter

    elif q_type == "truefalse":
        return correct == user

    else:
        # Short answer: fuzzy match — correct answer contained in user answer or vice versa
        return correct in user or user in correct
