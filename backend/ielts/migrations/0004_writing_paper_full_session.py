# Generated manually for full writing test (Task 1 + Task 2, single timer)

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ielts", "0003_reading_writing_extensions"),
    ]

    operations = [
        migrations.CreateModel(
            name="WritingPaper",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("title", models.CharField(max_length=200)),
                ("time_limit_minutes", models.PositiveSmallIntegerField(default=60)),
                (
                    "task_one",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="papers_as_task_one",
                        to="ielts.writingtask",
                    ),
                ),
                (
                    "task_two",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="papers_as_task_two",
                        to="ielts.writingtask",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WritingFullSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("phase", models.PositiveSmallIntegerField(default=1)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("task_one_submitted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "paper",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sessions",
                        to="ielts.writingpaper",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="writing_full_sessions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="writingfullsession",
            constraint=models.UniqueConstraint(
                condition=models.Q(finished_at__isnull=True),
                fields=("user", "paper"),
                name="ielts_unique_active_writing_full_session",
            ),
        ),
    ]
