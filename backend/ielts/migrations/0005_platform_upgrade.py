from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ielts", "0004_writing_paper_full_session"),
    ]

    operations = [
        migrations.AddField(
            model_name="writingtask",
            name="visual",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="writingattempt",
            name="submitted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="writingattempt",
            name="word_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="writingattempt",
            name="self_review",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.CreateModel(
            name="LearnerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("target_band", models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ("weekly_goal_minutes", models.PositiveIntegerField(default=120)),
                ("streak_days", models.PositiveIntegerField(default=0)),
                ("last_practice_date", models.DateField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learner_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
