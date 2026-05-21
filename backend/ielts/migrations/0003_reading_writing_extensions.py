# Generated manually for IELTS plan extensions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ielts", "0002_reading_exam_and_question_types"),
    ]

    operations = [
        migrations.AddField(
            model_name="readingpassage",
            name="source_note",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name="readingquestion",
            name="instruction",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="readingquestion",
            name="word_limit",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="readingquestion",
            name="question_type",
            field=models.CharField(
                choices=[
                    ("mcq", "Multiple Choice"),
                    ("match", "Matching"),
                    ("ynng", "Yes / No / Not Given"),
                    ("tfng", "True / False / Not Given"),
                    ("headings", "Match Headings"),
                    ("matching_info", "Matching Information"),
                    ("completion", "Completion"),
                    ("short_answer", "Short answer"),
                    ("sentence_endings", "Sentence endings"),
                ],
                default="mcq",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="writingtask",
            name="scenario",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="writingtask",
            name="task_kind",
            field=models.CharField(
                choices=[
                    ("academic_t1", "Task 1 — Academic (visual description)"),
                    ("gt_t1_letter", "Task 1 — General Training (letter)"),
                    ("t2_essay", "Task 2 — Essay"),
                ],
                default="t2_essay",
                max_length=20,
            ),
        ),
    ]
