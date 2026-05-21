from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import (
    ReadingExam,
    ReadingExamAttempt,
    ReadingQuestion,
    WritingPaper,
    WritingTask,
    WritingAttempt,
    WritingFullSession,
)
from .views import ensure_sample_data
from .band_mapping import reading_band_from_raw


class HubAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("hubuser", password="testpass123")

    def test_reading_hub_redirects_anonymous(self):
        r = self.client.get(reverse("ielts:reading_hub"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r["Location"])

    def test_writing_hub_redirects_anonymous(self):
        r = self.client.get(reverse("ielts:writing_hub"))
        self.assertEqual(r.status_code, 302)

    def test_reading_hub_authenticated(self):
        self.client.login(username="hubuser", password="testpass123")
        ensure_sample_data()
        r = self.client.get(reverse("ielts:reading_hub"))
        self.assertEqual(r.status_code, 200)


class ExamSubmissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("examuser", password="testpass123")
        self.client.login(username="examuser", password="testpass123")
        ensure_sample_data()
        self.exam = ReadingExam.objects.get(slug="full-sample")

    def test_exam_post_creates_attempt_with_score(self):
        url = reverse("ielts:reading_exam", args=[self.exam.id])
        q = ReadingQuestion.objects.first()
        payload = {f"q_{q.id}": q.correct_answer}
        r = self.client.post(url, payload)
        self.assertEqual(r.status_code, 302)
        att = ReadingExamAttempt.objects.filter(user=self.user, exam=self.exam).order_by("-id").first()
        self.assertIsNotNone(att)
        self.assertGreaterEqual(att.score, 1)

    def test_exam_post_empty_answers_zero_score(self):
        url = reverse("ielts:reading_exam", args=[self.exam.id])
        r = self.client.post(url, {})
        self.assertEqual(r.status_code, 302)
        att = ReadingExamAttempt.objects.filter(user=self.user, exam=self.exam).order_by("-id").first()
        self.assertIsNotNone(att)
        self.assertEqual(att.score, 0)


class WritingSubmitTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("writeuser", password="testpass123")
        self.client.login(username="writeuser", password="testpass123")
        ensure_sample_data()
        self.task = WritingTask.objects.order_by("id").first()

    def test_submit_writing_marks_submitted(self):
        url = reverse("ielts:submit_writing", args=[self.task.id])
        r = self.client.post(url, {"content": "Test response body."})
        self.assertEqual(r.status_code, 302)
        wa = WritingAttempt.objects.get(user=self.user, task=self.task, submitted=True)
        self.assertEqual(wa.content, "Test response body.")
        self.assertGreater(wa.word_count, 0)
        self.assertIsNotNone(wa.submitted_at)
        self.assertIn("writing/review", r["Location"])

    def test_new_draft_after_submit(self):
        self.client.post(reverse("ielts:submit_writing", args=[self.task.id]), {"content": "First."})
        r = self.client.get(reverse("ielts:writing", args=[self.task.id]))
        self.assertEqual(r.status_code, 200)
        self.assertIn("writing-form", r.content.decode())


class WritingFullTestFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("fullwrite", password="testpass123")
        self.client.login(username="fullwrite", password="testpass123")
        ensure_sample_data()
        self.paper = WritingPaper.objects.get(slug="full-academic")
        self.url_page = reverse("ielts:writing_full", args=[self.paper.id])
        self.url_submit = reverse("ielts:submit_writing_full", args=[self.paper.id])

    def test_full_writing_page_loads(self):
        r = self.client.get(self.url_page)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Submit Full Test")
        self.assertContains(r, "writing-chart-canvas")

    def test_finish_all_submits_both_tasks(self):
        self.client.get(self.url_page)
        r = self.client.post(
            self.url_submit,
            {
                "action": "finish_all",
                "content_task1": "Introduction overview and trends.",
                "content_task2": "Essay body with opinion and examples.",
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["ok"], True)
        self.assertIn("writing/review", r.json()["redirect"])

        self.assertFalse(
            WritingFullSession.objects.filter(user=self.user, paper=self.paper, finished_at__isnull=True).exists()
        )
        a1 = WritingAttempt.objects.filter(
            user=self.user, task=self.paper.task_one, submitted=True
        ).order_by("-updated_at").first()
        a2 = WritingAttempt.objects.filter(
            user=self.user, task=self.paper.task_two, submitted=True
        ).order_by("-updated_at").first()
        self.assertIsNotNone(a1)
        self.assertIsNotNone(a2)
        self.assertIn("trends", a1.content)
        self.assertIn("Essay body", a2.content)

    def test_timeout_submits_both_tasks(self):
        self.client.get(self.url_page)
        r = self.client.post(
            self.url_submit,
            {
                "action": "timeout",
                "content_task1": "Only task one.",
                "content_task2": "",
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["ok"], True)
        a2 = WritingAttempt.objects.filter(
            user=self.user, task=self.paper.task_two, submitted=True
        ).order_by("-updated_at").first()
        self.assertIsNotNone(a2)


class BandMappingTests(TestCase):
    def test_band_mapping_40_questions(self):
        self.assertEqual(reading_band_from_raw(39, 40), 9.0)
        self.assertEqual(reading_band_from_raw(30, 40), 7.0)
        self.assertEqual(reading_band_from_raw(0, 40), 0.0)


class Task1VisualTests(TestCase):
    def test_academic_tasks_have_visual_after_seed(self):
        ensure_sample_data()
        t1_tasks = WritingTask.objects.filter(task_kind=WritingTask.TASK_KIND_ACADEMIC_T1)
        self.assertGreater(t1_tasks.count(), 0)
        for task in t1_tasks:
            self.assertTrue(task.visual.get("kind"), msg=task.title)
