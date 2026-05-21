from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class WritingTask(models.Model):
    TASK_KIND_ACADEMIC_T1 = "academic_t1"
    TASK_KIND_ESSAY = "t2_essay"
    TASK_KIND_CHOICES = (
        (TASK_KIND_ACADEMIC_T1, "Task 1 — Academic (graphs, charts, etc.)"),
        (TASK_KIND_ESSAY, "Task 2 — Essay"),
    )
    title = models.CharField(max_length=200)
    prompt = models.TextField()
    time_limit_minutes = models.IntegerField(default=20)
    task_kind = models.CharField(
        max_length=20,
        choices=TASK_KIND_CHOICES,
        default=TASK_KIND_ESSAY,
    )
    # Optional structured brief for GT letters: recipient, bullets, tone hint
    scenario = models.JSONField(default=dict, blank=True)
    # Chart/diagram spec: {"kind": "line"|"bar"|"pie"|"table"|"process"|"map", "spec": {...}}
    visual = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class ReadingPassage(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    source_note = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.title


class ReadingQuestion(models.Model):
    QUESTION_TYPES = (
        ("mcq", "Multiple Choice"),
        ("tfng", "True / False / Not Given"),
        ("ynng", "Yes / No / Not Given"),
        ("headings", "Matching Headings"),
        ("matching_info", "Matching Information"),
        ("match_features", "Matching Features"),
        ("sentence_endings", "Matching Sentence Endings"),
        ("sentence_completion", "Sentence Completion"),
        ("summary_completion", "Summary Completion"),
        ("note_completion", "Note / Table / Flow-chart Completion"),
        ("diagram_completion", "Diagram Label Completion"),
        ("short_answer", "Short Answer Questions"),
    )
    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    instruction = models.TextField(blank=True)
    word_limit = models.PositiveSmallIntegerField(null=True, blank=True)
    # For mcq/ynng/headings/matching_info/sentence_endings: list of option strings
    choices = models.JSONField(default=list, blank=True)
    # String, JSON list of acceptable strings (completion/short_answer), or JSON for structured match maps
    correct_answer = models.TextField(blank=True)
    question_type = models.CharField(max_length=24, choices=QUESTION_TYPES, default="mcq")

    def __str__(self):
        return f"Q for {self.passage.title}: {self.text[:40]}"


class ReadingExam(models.Model):
    slug = models.SlugField(unique=True, max_length=80)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit_minutes = models.IntegerField(default=60)

    def __str__(self):
        return self.title


class ReadingExamSection(models.Model):
    exam = models.ForeignKey(ReadingExam, on_delete=models.CASCADE, related_name="sections")
    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["exam", "order"]
        constraints = [
            models.UniqueConstraint(fields=["exam", "order"], name="unique_exam_section_order"),
        ]

    def __str__(self):
        return f"{self.exam.title} §{self.order}: {self.passage.title}"


class ReadingExamAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reading_exam_attempts")
    exam = models.ForeignKey(ReadingExam, on_delete=models.CASCADE)
    answers = models.JSONField(default=dict, blank=True)
    score = models.IntegerField(default=0)
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ExamAttempt({self.user.username}, {self.exam.title})"


class WritingAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(WritingTask, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    word_count = models.PositiveIntegerField(default=0)
    self_review = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"WritingAttempt({self.user.username}, {self.task.title})"


class LearnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="learner_profile")
    target_band = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    weekly_goal_minutes = models.PositiveIntegerField(default=120)
    streak_days = models.PositiveIntegerField(default=0)
    last_practice_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"LearnerProfile({self.user.username})"


class WritingPaper(models.Model):
    """Fixed Task 1 + Task 2 pair for a single-session full writing test (one shared timer)."""

    slug = models.SlugField(unique=True, max_length=80)
    title = models.CharField(max_length=200)
    task_one = models.ForeignKey(
        WritingTask,
        on_delete=models.PROTECT,
        related_name="papers_as_task_one",
    )
    task_two = models.ForeignKey(
        WritingTask,
        on_delete=models.PROTECT,
        related_name="papers_as_task_two",
    )
    time_limit_minutes = models.PositiveSmallIntegerField(default=60)

    def __str__(self):
        return self.title


class WritingFullSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="writing_full_sessions",
    )
    paper = models.ForeignKey(WritingPaper, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField(default=timezone.now)
    phase = models.PositiveSmallIntegerField(default=1)
    finished_at = models.DateTimeField(null=True, blank=True)
    task_one_submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "paper"],
                condition=models.Q(finished_at__isnull=True),
                name="ielts_unique_active_writing_full_session",
            ),
        ]

    def __str__(self):
        return f"WritingFullSession({self.user.username}, {self.paper.slug}, ph{self.phase})"


class ReadingAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE)
    answers = models.JSONField(default=dict, blank=True)
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ReadingAttempt({self.user.username}, {self.passage.title})"
