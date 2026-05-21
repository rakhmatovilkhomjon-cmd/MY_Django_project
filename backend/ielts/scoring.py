import json


def _norm(s):
    return (s or "").strip().lower()


def _word_count(s):
    return len((s or "").strip().split()) if (s or "").strip() else 0


def _acceptable_list(correct: str):
    """Parse correct_answer as JSON array of strings, or treat as single string."""
    correct = (correct or "").strip()
    if not correct:
        return []
    if correct.startswith("["):
        try:
            data = json.loads(correct)
            if isinstance(data, list):
                return [str(x) for x in data]
        except (json.JSONDecodeError, TypeError):
            pass
    return [correct]


def is_answer_correct(question, raw) -> bool:
    """Return True if the submitted value matches the keyed correct answer for this question type."""
    if raw is None or raw == "":
        return False
    qt = question.question_type
    correct = question.correct_answer or ""

    if getattr(question, "word_limit", None) and qt in ("completion", "short_answer"):
        if _word_count(raw) > int(question.word_limit):
            return False

    if qt in ("mcq", "ynng", "tfng", "headings", "match", "sentence_endings"):
        return _norm(raw) == _norm(correct)

    if qt == "matching_info":
        try:
            if isinstance(raw, str) and raw.strip().startswith("{"):
                user_obj = json.loads(raw)
            elif isinstance(raw, dict):
                user_obj = raw
            else:
                user_obj = None
            if user_obj is not None and correct.strip().startswith("{"):
                corr_obj = json.loads(correct)
                return user_obj == corr_obj
        except (json.JSONDecodeError, TypeError):
            pass
        return _norm(raw) == _norm(correct)

    if qt in ("completion", "short_answer"):
        user_n = _norm(raw)
        for acc in _acceptable_list(correct):
            if user_n == _norm(acc):
                return True
        return False

    return _norm(raw) == _norm(correct)


def score_questions(questions, answers: dict) -> tuple[int, int]:
    """answers: {str(question_id): submitted_value}. Returns (correct_count, total_count)."""
    total = 0
    ok = 0
    for q in questions:
        total += 1
        key = str(q.id)
        val = answers.get(key)
        if is_answer_correct(q, val):
            ok += 1
    return ok, total
