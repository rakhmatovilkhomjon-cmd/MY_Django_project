from django.contrib import admin

from .models import (
    LearnerProfile,
    ReadingExam,
    ReadingExamSection,
    ReadingPassage,
    ReadingQuestion,
    WritingPaper,
    WritingTask,
)


@admin.register(WritingTask)
class WritingTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "task_kind", "time_limit_minutes")
    list_filter = ("task_kind",)
    search_fields = ("title", "prompt")


@admin.register(ReadingPassage)
class ReadingPassageAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title", "content")


@admin.register(ReadingQuestion)
class ReadingQuestionAdmin(admin.ModelAdmin):
    list_display = ("passage", "question_type", "text")
    list_filter = ("question_type",)


@admin.register(ReadingExam)
class ReadingExamAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "time_limit_minutes")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ReadingExamSection)
class ReadingExamSectionAdmin(admin.ModelAdmin):
    list_display = ("exam", "passage", "order")


@admin.register(WritingPaper)
class WritingPaperAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "time_limit_minutes")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "target_band", "streak_days", "weekly_goal_minutes")
