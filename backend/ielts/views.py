from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Prefetch, Avg, Count, Max
from django.urls import reverse
import random
from .forms import LoginForm, RegisterForm
from .models import (
    WritingTask,
    WritingAttempt,
    WritingPaper,
    WritingFullSession,
    ReadingPassage,
    ReadingQuestion,
    ReadingAttempt,
    ReadingExam,
    ReadingExamSection,
    ReadingExamAttempt,
    LearnerProfile,
)
from .scoring import score_questions, is_answer_correct
from .band_mapping import reading_band_from_raw
from .analytics_helpers import (
    aggregate_question_type_stats,
    exam_trend_data,
    exam_type_breakdown,
    focus_recommendations,
    update_streak,
    weekly_practice_minutes,
    weakest_question_types,
)
from django.utils import timezone
import json


def _writing_word_count(content: str) -> int:
    t = (content or "").strip()
    return len(t.split()) if t else 0


def ensure_sample_data():
    from .sample_data import seed_if_needed

    seed_if_needed()
    if WritingTask.objects.count() == 0:
        WritingTask.objects.create(
            title="Writing Task 1 — Charts and graphs",
            prompt="Summarise the chart in at least 150 words. You have 20 minutes.",
            time_limit_minutes=20,
            task_kind=WritingTask.TASK_KIND_ACADEMIC_T1,
        )
        WritingTask.objects.create(
            title="Writing Task 2 — Essay",
            prompt="Write an essay of at least 250 words. You have 40 minutes.",
            time_limit_minutes=40,
            task_kind=WritingTask.TASK_KIND_ESSAY,
        )


def home(request):
    ensure_sample_data()
    ctx = {}
    if request.user.is_authenticated:
        ctx["home_stats"] = {
            "exam_count": ReadingExamAttempt.objects.filter(
                user=request.user, submitted_at__isnull=False
            ).count(),
            "writing_count": WritingAttempt.objects.filter(
                user=request.user, submitted=True
            ).count(),
        }
    return render(request, "ielts/home.html", ctx)


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data.get("email") or "",
                password=form.cleaned_data["password"],
            )
            login(request, user)
            return redirect("ielts:dashboard")
    else:
        form = RegisterForm()
    return render(request, "ielts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user:
                login(request, user)
                return redirect("ielts:dashboard")
            form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "ielts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("ielts:home")


@login_required
def dashboard(request):
    ensure_sample_data()
    writing_tasks = WritingTask.objects.all()
    reading_passages = ReadingPassage.objects.all()
    writing_attempts = WritingAttempt.objects.filter(user=request.user).order_by("-updated_at")[:10]
    reading_attempts = ReadingAttempt.objects.filter(user=request.user).order_by("-submitted_at")[:10]
    exams = ReadingExam.objects.all()
    exam_attempts = (
        ReadingExamAttempt.objects.filter(user=request.user, submitted_at__isnull=False)
        .select_related("exam")
        .order_by("-submitted_at")[:10]
    )
    exam_stats = ReadingExamAttempt.objects.filter(user=request.user, submitted_at__isnull=False).aggregate(
        n=Count("id"),
        avg_score=Avg("score"),
        best_score=Max("score"),
    )
    last_exam = exam_attempts.first() if exam_attempts else None
    last_exam_pct = None
    last_exam_band = None
    if last_exam:
        total_q = 0
        for sec in last_exam.exam.sections.prefetch_related("passage__questions"):
            total_q += sec.passage.questions.count()
        if total_q:
            last_exam_pct = round(100 * last_exam.score / total_q)
            last_exam_band = reading_band_from_raw(last_exam.score, total_q)
    profile, _ = LearnerProfile.objects.get_or_create(user=request.user)
    weekly_mins = weekly_practice_minutes(request.user)
    focus = focus_recommendations(request.user)
    return render(
        request,
        "ielts/dashboard.html",
        {
            "writing_tasks": writing_tasks,
            "reading_passages": reading_passages,
            "writing_attempts": writing_attempts,
            "reading_attempts": reading_attempts,
            "reading_exams": exams,
            "exam_attempts": exam_attempts,
            "exam_stats": exam_stats,
            "last_exam_attempt": last_exam,
            "last_exam_pct": last_exam_pct,
            "last_exam_band": last_exam_band,
            "learner_profile": profile,
            "weekly_minutes": weekly_mins,
            "weekly_goal": profile.weekly_goal_minutes,
            "focus": focus,
        },
    )


FULL_WRITING_GRACE_SECONDS = 120


def _full_remaining_seconds(session, paper):
    limit_sec = paper.time_limit_minutes * 60
    elapsed = (timezone.now() - session.started_at).total_seconds()
    return max(0, int(limit_sec - elapsed))


def _full_within_grace_window(session, paper):
    allowed = paper.time_limit_minutes * 60 + FULL_WRITING_GRACE_SECONDS
    elapsed = (timezone.now() - session.started_at).total_seconds()
    return elapsed <= allowed


def _save_submit_writing(user, task, content):
    attempt = (
        WritingAttempt.objects.filter(user=user, task=task, submitted=False).order_by("-updated_at").first()
    )
    now = timezone.now()
    if attempt is None:
        attempt = WritingAttempt.objects.create(
            user=user,
            task=task,
            content=content,
            submitted=True,
            submitted_at=now,
            word_count=_writing_word_count(content),
        )
    else:
        attempt.content = content
        attempt.submitted = True
        attempt.submitted_at = now
        attempt.word_count = _writing_word_count(content)
        attempt.save()
    update_streak(user)
    return attempt


def _submit_empty_task_two(user, task_two):
    attempt = (
        WritingAttempt.objects.filter(user=user, task=task_two, submitted=False).order_by("-updated_at").first()
    )
    if attempt is None:
        WritingAttempt.objects.create(user=user, task=task_two, content="", submitted=True)
    else:
        attempt.content = ""
        attempt.submitted = True
        attempt.save()


def _close_writing_full_session(session):
    session.finished_at = timezone.now()
    session.save(update_fields=["finished_at"])


def _expire_writing_full_on_server(request, session, paper):
    """Submit when the clock has reached zero (including after refresh)."""
    user = session.user
    if session.phase == 1:
        da = (
            WritingAttempt.objects.filter(user=user, task=paper.task_one, submitted=False)
            .order_by("-updated_at")
            .first()
        )
        c1 = da.content if da else ""
        _save_submit_writing(user, paper.task_one, c1)
        _submit_empty_task_two(user, paper.task_two)
    else:
        da = (
            WritingAttempt.objects.filter(user=user, task=paper.task_two, submitted=False)
            .order_by("-updated_at")
            .first()
        )
        c2 = da.content if da else ""
        _save_submit_writing(user, paper.task_two, c2)
    _close_writing_full_session(session)
    messages.warning(request, "Time is up — your answers were submitted automatically.")


@login_required
def writing_hub(request):
    ensure_sample_data()
    tasks = WritingTask.objects.all().order_by("task_kind", "time_limit_minutes")
    papers = WritingPaper.objects.select_related("task_one", "task_two").order_by("slug")
    return render(
        request,
        "ielts/writing_hub.html",
        {"writing_tasks": tasks, "writing_papers": papers},
    )


@login_required
def reading_hub(request):
    ensure_sample_data()
    exams = ReadingExam.objects.prefetch_related(
        Prefetch("sections", queryset=ReadingExamSection.objects.select_related("passage").order_by("order"))
    ).all()
    passages = ReadingPassage.objects.all()
    type_cards = [
        ("tfng", "True / False / Not Given", "Decide whether statements match the passage."),
        ("ynng", "Yes / No / Not Given", "Match claims to the writer’s views where applicable."),
        ("mcq", "Multiple choice", "Select one best answer from four options."),
        ("headings", "Matching headings", "Choose the paragraph or section that fits."),
        ("matching_info", "Matching information", "Locate where ideas appear in the text."),
        ("match_features", "Matching features", "Connect features or ideas to the right part of the passage."),
        ("sentence_completion", "Sentence completion", "Fill gaps using words from the passage (word limit stated)."),
        ("summary_completion", "Summary completion", "Complete a summary using words from the passage."),
        ("note_completion", "Note / Table / Flow-chart completion", "Complete notes or a table using words from the passage."),
        ("diagram_completion", "Diagram label completion", "Label a diagram using words from the passage."),
        ("short_answer", "Short answer", "Brief written answers — check spelling and word limits."),
        ("sentence_endings", "Sentence endings", "Complete a sentence stem from a list of endings."),
    ]
    return render(
        request,
        "ielts/reading_hub.html",
        {
            "reading_exams": exams,
            "reading_passages": passages,
            "question_type_cards": type_cards,
        },
    )


@login_required
def reading_single_passages_view(request):
    ensure_sample_data()
    passages = ReadingPassage.objects.all()
    return render(
        request,
        "ielts/reading_single_passages.html",
        {"reading_passages": passages},
    )


@login_required
def reading_exam_random(request):
    ensure_sample_data()
    # Pick 3 random passages
    passages = list(ReadingPassage.objects.all())
    if len(passages) < 3:
        messages.error(request, "Not enough passages to generate a full test. Need at least 3.")
        return redirect("ielts:reading_hub")
    
    random.shuffle(passages)
    selected_passages = passages[:3]
    
    # Create the exam
    time_str = timezone.now().strftime("%Y%m%d-%H%M%S")
    exam = ReadingExam.objects.create(
        slug=f"random-test-{time_str}-{random.randint(1000,9999)}",
        title=f"Full reading test (Random generated {timezone.now().strftime('%b %d, %H:%M')})",
        description="Three dynamically selected passages, 60 minutes. Timed like a real academic reading test.",
        time_limit_minutes=60,
    )
    
    # Create sections
    for i, passage in enumerate(selected_passages):
        ReadingExamSection.objects.create(exam=exam, passage=passage, order=i+1)
        
    return redirect("ielts:reading_exam", exam_id=exam.id)


@login_required
def reading_exam_view(request, exam_id):
    ensure_sample_data()
    exam = get_object_or_404(
        ReadingExam.objects.prefetch_related(
            Prefetch(
                "sections",
                queryset=ReadingExamSection.objects.select_related("passage")
                .prefetch_related("passage__questions")
                .order_by("order"),
            )
        ),
        pk=exam_id,
    )
    sections = list(exam.sections.all())
    if not sections:
        messages.error(request, "This exam has no passages configured yet.")
        return redirect("ielts:reading_hub")

    all_questions = []
    for sec in sections:
        for q in sec.passage.questions.all():
            all_questions.append(q)

    if request.method == "POST":
        answers = {}
        for key, val in request.POST.items():
            if key.startswith("q_"):
                qid = key[2:]
                if qid.isdigit():
                    answers[qid] = val
        score, total = score_questions(all_questions, answers)
        attempt = ReadingExamAttempt.objects.create(
            user=request.user,
            exam=exam,
            answers=answers,
            score=score,
            submitted_at=timezone.now(),
        )
        update_streak(request.user)
        return redirect("ielts:exam_result", attempt_id=attempt.id)

    exam_sections = []
    idx = 1
    for sec in sections:
        qs = list(sec.passage.questions.all())
        exam_sections.append({"section": sec, "questions": qs, "q_start": idx})
        idx += len(qs)

    return render(
        request,
        "ielts/reading_exam.html",
        {
            "exam": exam,
            "exam_sections": exam_sections,
            "total_questions": len(all_questions),
        },
    )


@login_required
def exam_result_view(request, attempt_id):
    attempt = get_object_or_404(ReadingExamAttempt, pk=attempt_id, user=request.user)
    sections = list(
        attempt.exam.sections.select_related("passage")
        .prefetch_related("passage__questions")
        .order_by("order")
    )
    detail_rows = []
    for sec in sections:
        for q in sec.passage.questions.all():
            key = str(q.id)
            given = attempt.answers.get(key, "")
            detail_rows.append(
                {
                    "passage": sec.passage.title,
                    "question": q,
                    "given": given,
                    "correct": is_answer_correct(q, given),
                }
            )
    total = len(detail_rows)
    band = reading_band_from_raw(attempt.score, total) if total else 0
    type_breakdown = exam_type_breakdown(attempt)
    return render(
        request,
        "ielts/exam_result.html",
        {
            "attempt": attempt,
            "detail_rows": detail_rows,
            "total_questions": total,
            "reading_band": band,
            "type_breakdown": type_breakdown,
        },
    )


PRACTICE_TYPES = frozenset(
    {
        "ynng",
        "tfng",
        "mcq",
        "headings",
        "matching_info",
        "match_features",
        "sentence_completion",
        "summary_completion",
        "note_completion",
        "diagram_completion",
        "short_answer",
        "sentence_endings",
        "mixed",
    }
)
MIXED_PRACTICE_COUNT = 16
MIXED_SESSION_KEY = "reading_mixed_practice_ids"


@login_required
def reading_practice_view(request, type_slug):
    if type_slug not in PRACTICE_TYPES:
        return redirect("ielts:reading_hub")

    result = None
    questions = None

    if type_slug == "mixed":
        if request.method == "POST":
            ids = request.session.get(MIXED_SESSION_KEY) or []
            if not ids:
                messages.warning(request, "Your mixed drill session expired. Start a new set.")
                return redirect("ielts:reading_hub")
            q_map = {
                q.id: q
                for q in ReadingQuestion.objects.filter(id__in=ids).select_related("passage")
            }
            questions = [q_map[i] for i in ids if i in q_map]
            if len(questions) < 4:
                messages.info(request, "Not enough questions in the bank yet.")
                return redirect("ielts:reading_hub")
        else:
            pool = list(ReadingQuestion.objects.select_related("passage").all())
            if len(pool) < 4:
                messages.info(request, "No practice items yet. Open a full test from the hub first.")
                return redirect("ielts:reading_hub")
            random.shuffle(pool)
            questions = pool[:MIXED_PRACTICE_COUNT]
            request.session[MIXED_SESSION_KEY] = [q.id for q in questions]
    else:
        questions = (
            ReadingQuestion.objects.filter(question_type=type_slug)
            .select_related("passage")
            .order_by("passage_id", "id")
        )
        if not questions.exists():
            messages.info(request, "No practice items for this type yet. Complete a full test first.")
            return redirect("ielts:reading_hub")
        questions = list(questions)

    if request.method == "POST":
        answers = {}
        for key, val in request.POST.items():
            if key.startswith("q_"):
                qid = key[2:]
                if qid.isdigit():
                    answers[qid] = val
        score, total = score_questions(questions, answers)
        result = {"score": score, "total": total, "answers": answers}
        if type_slug == "mixed":
            request.session.pop(MIXED_SESSION_KEY, None)

    return render(
        request,
        "ielts/reading_practice.html",
        {
            "practice_type": type_slug,
            "questions": questions,
            "result": result,
        },
    )


def _draft_writing_attempt(user, task):
    attempt = (
        WritingAttempt.objects.filter(user=user, task=task, submitted=False).order_by("-updated_at").first()
    )
    if attempt is None:
        attempt = WritingAttempt.objects.create(user=user, task=task, submitted=False)
    return attempt


@login_required
def writing_exam_random(request):
    ensure_sample_data()
    task1_pool = list(WritingTask.objects.filter(task_kind=WritingTask.TASK_KIND_ACADEMIC_T1))
    task2_pool = list(WritingTask.objects.filter(task_kind=WritingTask.TASK_KIND_ESSAY))
    
    if not task1_pool or not task2_pool:
        messages.error(request, "Not enough writing tasks in the bank to generate a full test. Need at least one Task 1 and one Task 2.")
        return redirect("ielts:writing_hub")

    task1 = random.choice(task1_pool)
    task2 = random.choice(task2_pool)

    time_str = timezone.now().strftime("%Y%m%d-%H%M%S")
    paper = WritingPaper.objects.create(
        slug=f"random-writing-{time_str}-{random.randint(1000,9999)}",
        title=f"Full writing test (Random generated {timezone.now().strftime('%b %d, %H:%M')})",
        task_one=task1,
        task_two=task2,
        time_limit_minutes=60,
    )
    
    return redirect("ielts:writing_full", paper_id=paper.id)


@login_required
def writing_full_view(request, paper_id):
    ensure_sample_data()
    paper = get_object_or_404(
        WritingPaper.objects.select_related("task_one", "task_two"),
        pk=paper_id,
    )
    session = WritingFullSession.objects.filter(
        user=request.user, paper=paper, finished_at__isnull=True
    ).first()
    if session is None:
        session = WritingFullSession.objects.create(user=request.user, paper=paper, phase=1)

    remaining = _full_remaining_seconds(session, paper)
    if remaining <= 0:
        _expire_writing_full_on_server(request, session, paper)
        return redirect("ielts:writing_hub")

    # Always load both task drafts
    draft_one = _draft_writing_attempt(request.user, paper.task_one)
    draft_two = _draft_writing_attempt(request.user, paper.task_two)

    return render(
        request,
        "ielts/writing_full.html",
        {
            "paper": paper,
            "session": session,
            "editor_content_one": draft_one.content,
            "editor_content_two": draft_two.content,
            "remaining_seconds": remaining,
            "submit_full_url": reverse("ielts:submit_writing_full", kwargs={"paper_id": paper.id}),
        },
    )



@login_required
@require_POST
def submit_writing_full(request, paper_id):
    paper = get_object_or_404(WritingPaper, pk=paper_id)
    session = WritingFullSession.objects.filter(
        user=request.user, paper=paper, finished_at__isnull=True
    ).first()
    if session is None:
        return JsonResponse({"ok": False, "error": "no_active_session"}, status=400)

    action = (request.POST.get("action") or "").strip()
    content_task1 = request.POST.get("content_task1", "")
    content_task2 = request.POST.get("content_task2", "")

    if not _full_within_grace_window(session, paper) and action not in ("timeout", ):
        return JsonResponse({"ok": False, "error": "time_window_closed"}, status=400)

    if action == "finish_all":
        _save_submit_writing(request.user, paper.task_one, content_task1)
        att2 = _save_submit_writing(request.user, paper.task_two, content_task2)
        _close_writing_full_session(session)
        messages.success(request, "Full writing test submitted successfully!")
        review_url = reverse("ielts:writing_review", kwargs={"attempt_id": att2.id})
        return JsonResponse({"ok": True, "redirect": review_url})

    if action == "timeout":
        _save_submit_writing(request.user, paper.task_one, content_task1)
        att2 = _save_submit_writing(request.user, paper.task_two, content_task2)
        _close_writing_full_session(session)
        messages.warning(request, "Time is up — your answers were submitted automatically.")
        review_url = reverse("ielts:writing_review", kwargs={"attempt_id": att2.id})
        return JsonResponse({"ok": True, "redirect": review_url})

    return JsonResponse({"ok": False, "error": "unknown_action"}, status=400)



@login_required
def writing_view(request, task_id):
    ensure_sample_data()
    task = get_object_or_404(WritingTask, pk=task_id)
    attempt = _draft_writing_attempt(request.user, task)
    return render(request, "ielts/writing.html", {"task": task, "attempt": attempt})


@login_required
@require_POST
def autosave_writing(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        task_id = int(data.get("task_id"))
        content = data.get("content", "")
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "invalid payload"}, status=400)
    task = get_object_or_404(WritingTask, pk=task_id)
    attempt = _draft_writing_attempt(request.user, task)
    attempt.content = content
    attempt.save()
    return JsonResponse({"ok": True, "saved_at": attempt.updated_at.isoformat()})


@login_required
@require_POST
def submit_writing(request, task_id):
    task = get_object_or_404(WritingTask, pk=task_id)
    attempt = (
        WritingAttempt.objects.filter(user=request.user, task=task, submitted=False).order_by("-updated_at").first()
    )
    content = request.POST.get("content", "")
    if attempt is None:
        attempt = WritingAttempt.objects.create(user=request.user, task=task, submitted=False, content=content)
    else:
        attempt.content = content
    attempt.submitted = True
    attempt.submitted_at = timezone.now()
    attempt.word_count = _writing_word_count(content)
    attempt.save()
    update_streak(request.user)
    messages.success(request, "Your writing has been submitted.")
    return redirect("ielts:writing_review", attempt_id=attempt.id)


@login_required
def reading_passage_view(request, passage_id):
    ensure_sample_data()
    passage = get_object_or_404(ReadingPassage, pk=passage_id)
    questions = passage.questions.all()
    if request.method == "POST":
        answers = {}
        for q in questions:
            val = request.POST.get(f"q_{q.id}")
            if val is not None:
                answers[str(q.id)] = val
        score, _ = score_questions(list(questions), answers)
        ra = ReadingAttempt.objects.create(
            user=request.user,
            passage=passage,
            answers=answers,
            score=score,
            submitted_at=timezone.now(),
        )
        update_streak(request.user)
        return redirect("ielts:result", attempt_id=ra.id)
    return render(
        request,
        "ielts/reading.html",
        {
            "passage": passage,
            "questions": questions,
            "passage_timer_minutes": 20,
        },
    )


@login_required
def submit_reading(request, passage_id):
    return reading_passage_view(request, passage_id)


@login_required
def result_view(request, attempt_id):
    attempt = get_object_or_404(ReadingAttempt, pk=attempt_id, user=request.user)
    writing = WritingAttempt.objects.filter(user=request.user, submitted=True).order_by("-updated_at").first()
    return render(request, "ielts/result.html", {"reading_attempt": attempt, "writing_attempt": writing})


@login_required
def analytics_view(request):
    ensure_sample_data()
    type_stats = aggregate_question_type_stats(request.user)
    trend = exam_trend_data(request.user)
    weak = weakest_question_types(request.user, limit=5)
    return render(
        request,
        "ielts/analytics.html",
        {
            "type_stats": type_stats,
            "trend": trend,
            "weak_types": weak,
        },
    )


@login_required
def writing_review_view(request, attempt_id):
    attempt = get_object_or_404(
        WritingAttempt.objects.select_related("task"),
        pk=attempt_id,
        user=request.user,
        submitted=True,
    )
    task = attempt.task
    min_words = 150 if task.time_limit_minutes <= 20 else 250

    if request.method == "POST":
        self_review = {
            "ta": int(request.POST.get("ta") or 0),
            "cc": int(request.POST.get("cc") or 0),
            "lr": int(request.POST.get("lr") or 0),
            "gra": int(request.POST.get("gra") or 0),
            "notes": (request.POST.get("notes") or "").strip()[:2000],
        }
        attempt.self_review = self_review
        attempt.save(update_fields=["self_review"])
        messages.success(request, "Self-review saved.")
        return redirect("ielts:dashboard")

    return render(
        request,
        "ielts/writing_review.html",
        {
            "attempt": attempt,
            "task": task,
            "min_words": min_words,
            "review": attempt.self_review or {},
        },
    )
