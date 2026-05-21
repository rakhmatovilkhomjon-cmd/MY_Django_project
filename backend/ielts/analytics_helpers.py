from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from .band_mapping import reading_band_from_raw
from .models import (
    ReadingAttempt,
    ReadingExamAttempt,
    ReadingQuestion,
    WritingAttempt,
    WritingTask,
)
from .scoring import is_answer_correct


def _word_count(text: str) -> int:
    t = (text or "").strip()
    return len(t.split()) if t else 0


def aggregate_question_type_stats(user):
    """Return list of dicts: type, correct, total, accuracy (0-100)."""
    counts = defaultdict(lambda: {"correct": 0, "total": 0})

    for attempt in ReadingExamAttempt.objects.filter(user=user, submitted_at__isnull=False):
        for sec in attempt.exam.sections.prefetch_related("passage__questions"):
            for q in sec.passage.questions.all():
                key = str(q.id)
                given = attempt.answers.get(key, "")
                qt = q.question_type
                counts[qt]["total"] += 1
                if is_answer_correct(q, given):
                    counts[qt]["correct"] += 1

    for attempt in ReadingAttempt.objects.filter(user=user, submitted_at__isnull=False):
        for q in ReadingQuestion.objects.filter(passage=attempt.passage):
            key = str(q.id)
            given = attempt.answers.get(key, "")
            qt = q.question_type
            counts[qt]["total"] += 1
            if is_answer_correct(q, given):
                counts[qt]["correct"] += 1

    rows = []
    for qt, data in counts.items():
        total = data["total"]
        correct = data["correct"]
        acc = round(100 * correct / total) if total else 0
        rows.append(
            {
                "type": qt,
                "label": dict(ReadingQuestion.QUESTION_TYPES).get(qt, qt),
                "correct": correct,
                "total": total,
                "accuracy": acc,
            }
        )
    rows.sort(key=lambda r: (r["accuracy"], -r["total"]))
    return rows


def weakest_question_types(user, limit=3):
    stats = aggregate_question_type_stats(user)
    weak = [s for s in stats if s["total"] >= 2]
    weak.sort(key=lambda r: (r["accuracy"], -r["total"]))
    return weak[:limit]


def exam_trend_data(user, limit=12):
    attempts = (
        ReadingExamAttempt.objects.filter(user=user, submitted_at__isnull=False)
        .select_related("exam")
        .prefetch_related("exam__sections__passage__questions")
        .order_by("submitted_at")[:limit]
    )
    points = []
    for a in attempts:
        total_q = 0
        for sec in a.exam.sections.all():
            total_q += sec.passage.questions.count()
        pct = round(100 * a.score / total_q) if total_q else 0
        band = reading_band_from_raw(a.score, total_q)
        points.append(
            {
                "date": a.submitted_at.strftime("%d %b"),
                "exam": a.exam.title,
                "score": a.score,
                "total": total_q,
                "pct": pct,
                "band": band,
            }
        )
    return points


def focus_recommendations(user):
    """Suggested next steps for dashboard."""
    weak = weakest_question_types(user, limit=1)
    reading_tip = None
    if weak:
        w = weak[0]
        reading_tip = {
            "type_slug": w["type"],
            "label": w["label"],
            "accuracy": w["accuracy"],
        }

    week_ago = timezone.now() - timedelta(days=7)
    recent_t1 = WritingAttempt.objects.filter(
        user=user,
        submitted=True,
        task__task_kind=WritingTask.TASK_KIND_ACADEMIC_T1,
        submitted_at__gte=week_ago,
    ).exists()
    writing_tip = None
    if not recent_t1:
        t1 = WritingTask.objects.filter(task_kind=WritingTask.TASK_KIND_ACADEMIC_T1).first()
        if t1:
            writing_tip = {"task_id": t1.id, "title": t1.title}

    return {"reading": reading_tip, "writing": writing_tip}


def weekly_practice_minutes(user):
    """Sum approximate minutes from submitted attempts in the last 7 days."""
    since = timezone.now() - timedelta(days=7)
    minutes = 0
    for a in ReadingExamAttempt.objects.filter(user=user, submitted_at__gte=since):
        if a.started_at and a.submitted_at:
            minutes += max(1, int((a.submitted_at - a.started_at).total_seconds() / 60))
    for a in ReadingAttempt.objects.filter(user=user, submitted_at__gte=since):
        minutes += 15
    for a in WritingAttempt.objects.filter(user=user, submitted=True, submitted_at__gte=since):
        if a.started_at and a.submitted_at:
            minutes += max(1, int((a.submitted_at - a.started_at).total_seconds() / 60))
        else:
            minutes += a.task.time_limit_minutes
    return minutes


def update_streak(user):
    from .models import LearnerProfile

    profile, _ = LearnerProfile.objects.get_or_create(user=user)
    today = timezone.localdate()
    if profile.last_practice_date == today:
        return profile.streak_days
    if profile.last_practice_date == today - timedelta(days=1):
        profile.streak_days += 1
    elif profile.last_practice_date is None:
        profile.streak_days = 1
    else:
        profile.streak_days = 1
    profile.last_practice_date = today
    profile.save(update_fields=["streak_days", "last_practice_date"])
    return profile.streak_days


def exam_type_breakdown(attempt):
    """Per question-type stats for a single exam attempt."""
    counts = defaultdict(lambda: {"correct": 0, "total": 0})
    for sec in attempt.exam.sections.prefetch_related("passage__questions"):
        for q in sec.passage.questions.all():
            key = str(q.id)
            given = attempt.answers.get(key, "")
            qt = q.question_type
            counts[qt]["total"] += 1
            if is_answer_correct(q, given):
                counts[qt]["correct"] += 1
    rows = []
    for qt, data in counts.items():
        total = data["total"]
        correct = data["correct"]
        rows.append(
            {
                "type": qt,
                "label": dict(ReadingQuestion.QUESTION_TYPES).get(qt, qt),
                "correct": correct,
                "total": total,
                "accuracy": round(100 * correct / total) if total else 0,
            }
        )
    rows.sort(key=lambda r: r["label"])
    return rows
