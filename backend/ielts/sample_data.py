"""
Seed reading exams and writing tasks. Invoked from views.ensure_sample_data.
"""
from .models import (
    ReadingExam,
    ReadingExamSection,
    ReadingPassage,
    ReadingQuestion,
    WritingPaper,
    WritingTask,
)
from .visual_specs import (
    GENERIC_BAR,
    HOUSEHOLD_INTERNET_LINE,
    RENEWABLE_ELECTRICITY_BAR,
    WATER_TREATMENT_PROCESS,
)


def _seed_writing_tasks():
    WritingTask.objects.update_or_create(
        title="Writing Task 1 — Charts and graphs",
        defaults={
            "prompt": (
                "You should spend about 20 minutes on this task.\n\n"
                "The chart(s) or diagram(s) show changes over time or differences between groups. "
                "Summarise the information by selecting and reporting the main features, "
                "and make comparisons where relevant.\n\n"
                "Write at least 150 words."
            ),
            "time_limit_minutes": 20,
            "task_kind": WritingTask.TASK_KIND_ACADEMIC_T1,
            "scenario": {},
            "visual": GENERIC_BAR,
        },
    )
    WritingTask.objects.update_or_create(
        title="Academic Task 1 — Household internet access (line graph)",
        defaults={
            "prompt": (
                "You should spend about 20 minutes on this task.\n\n"
                "The line graph shows the percentage of households with broadband internet access "
                "in three regions (North, Central, and South) between 2010 and 2020.\n\n"
                "Summarise the information by selecting and reporting the main features, "
                "and make comparisons where relevant.\n\n"
                "Write at least 150 words."
            ),
            "time_limit_minutes": 20,
            "task_kind": WritingTask.TASK_KIND_ACADEMIC_T1,
            "scenario": {},
            "visual": HOUSEHOLD_INTERNET_LINE,
        },
    )
    WritingTask.objects.update_or_create(
        title="Academic Task 1 — Renewable electricity (bar chart)",
        defaults={
            "prompt": (
                "You should spend about 20 minutes on this task.\n\n"
                "The bar chart compares the share of electricity generated from renewable sources "
                "(solar, wind, and hydro) in five countries in a single year.\n\n"
                "Summarise the information by selecting and reporting the main features, "
                "and make comparisons where relevant.\n\n"
                "Write at least 150 words."
            ),
            "time_limit_minutes": 20,
            "task_kind": WritingTask.TASK_KIND_ACADEMIC_T1,
            "scenario": {},
            "visual": RENEWABLE_ELECTRICITY_BAR,
        },
    )
    WritingTask.objects.update_or_create(
        title="Academic Task 1 — Urban water treatment (process)",
        defaults={
            "prompt": (
                "You should spend about 20 minutes on this task.\n\n"
                "The diagram illustrates the main stages in treating wastewater at a municipal plant, "
                "from initial screening to discharge of treated water.\n\n"
                "Summarise the information by selecting and reporting the main features. "
                "Where relevant, describe the process in sequence.\n\n"
                "Write at least 150 words."
            ),
            "time_limit_minutes": 20,
            "task_kind": WritingTask.TASK_KIND_ACADEMIC_T1,
            "scenario": {},
            "visual": WATER_TREATMENT_PROCESS,
        },
    )

    WritingTask.objects.update_or_create(
        title="Writing Task 2 — Essay",
        defaults={
            "prompt": (
                "You should spend about 40 minutes on this task.\n\n"
                "Write about the following topic:\n\n"
                "Some people think governments should spend more on public transport, "
                "while others believe investment in roads is more important.\n\n"
                "Discuss both these views and give your own opinion.\n\n"
                "Give reasons for your answer and include any relevant examples from your own knowledge or experience.\n\n"
                "Write at least 250 words."
            ),
            "time_limit_minutes": 40,
            "task_kind": WritingTask.TASK_KIND_ESSAY,
            "scenario": {},
        },
    )
    WritingTask.objects.update_or_create(
        title="Task 2 — Artificial intelligence in education",
        defaults={
            "prompt": (
                "You should spend about 40 minutes on this task.\n\n"
                "Write about the following topic:\n\n"
                "Some educators believe artificial intelligence tools will greatly improve learning, "
                "while others fear they will reduce critical thinking and encourage cheating.\n\n"
                "Discuss both these views and give your own opinion.\n\n"
                "Give reasons for your answer and include any relevant examples from your own knowledge or experience.\n\n"
                "Write at least 250 words."
            ),
            "time_limit_minutes": 40,
            "task_kind": WritingTask.TASK_KIND_ESSAY,
            "scenario": {},
        },
    )
    WritingTask.objects.update_or_create(
        title="Task 2 — Remote working",
        defaults={
            "prompt": (
                "You should spend about 40 minutes on this task.\n\n"
                "Write about the following topic:\n\n"
                "In many countries, more people now work from home than in the past.\n\n"
                "Do the advantages of this trend outweigh the disadvantages?\n\n"
                "Give reasons for your answer and include any relevant examples from your own knowledge or experience.\n\n"
                "Write at least 250 words."
            ),
            "time_limit_minutes": 40,
            "task_kind": WritingTask.TASK_KIND_ESSAY,
            "scenario": {},
        },
    )
    WritingTask.objects.update_or_create(
        title="Task 2 — Plastic packaging and consumers",
        defaults={
            "prompt": (
                "You should spend about 40 minutes on this task.\n\n"
                "Write about the following topic:\n\n"
                "Plastic packaging creates environmental problems, but it also keeps food fresh and reduces waste.\n\n"
                "What problems does this cause? What do you think are the solutions?\n\n"
                "Give reasons for your answer and include any relevant examples from your own knowledge or experience.\n\n"
                "Write at least 250 words."
            ),
            "time_limit_minutes": 40,
            "task_kind": WritingTask.TASK_KIND_ESSAY,
            "scenario": {},
        },
    )
    WritingTask.objects.update_or_create(
        title="Task 2 — University: specialist vs broad education",
        defaults={
            "prompt": (
                "You should spend about 40 minutes on this task.\n\n"
                "Write about the following topic:\n\n"
                "Some people think universities should train students in one specific subject "
                "to prepare them for a career. Others think universities should offer a wide range "
                "of subjects so graduates are more broadly educated.\n\n"
                "Discuss both these views and give your own opinion.\n\n"
                "Give reasons for your answer and include any relevant examples from your own knowledge or experience.\n\n"
                "Write at least 250 words."
            ),
            "time_limit_minutes": 40,
            "task_kind": WritingTask.TASK_KIND_ESSAY,
            "scenario": {},
        },
    )


def _seed_writing_papers():
    t_ac1 = WritingTask.objects.filter(
        title="Academic Task 1 — Household internet access (line graph)"
    ).first()
    t_ac2 = WritingTask.objects.filter(title="Task 2 — Artificial intelligence in education").first()
    if t_ac1 and t_ac2:
        WritingPaper.objects.update_or_create(
            slug="full-academic",
            defaults={
                "title": "Full test — Academic (Task 1 + Task 2)",
                "task_one": t_ac1,
                "task_two": t_ac2,
                "time_limit_minutes": 60,
            },
        )


def _seed_full_sample_legacy():
    if ReadingExam.objects.filter(slug="full-sample").exists():
        return

    p1_text = """**Paragraph A**
Urban green spaces—parks, tree-lined streets, and community gardens—play a measurable role in public health. Studies link proximity to vegetation with lower stress markers and more walking for transport.

**Paragraph B**
Critics argue that planting programmes are cosmetic unless paired with maintenance budgets. Without irrigation and stewardship, new trees can fail within a few seasons, wasting public funds.

**Paragraph C**
Several cities now embed “green corridors” into zoning law, requiring developers to preserve or replace canopy cover. Early results suggest slower heat-island growth in districts that adopted the rules early.

**Paragraph D**
Volunteer groups often fill gaps where municipal funding is thin. Weekend planting events can mobilise hundreds of residents, but long-term watering plans remain a weak point in many programmes."""

    p2_text = """**Section 1**
Digital textbooks promise instant updates and lower printing costs. Adoption in secondary schools has risen steadily where devices are available and bandwidth is reliable.

**Section 2**
Teachers report a split outcome: richer multimedia aids explanation, yet notifications and multitasking undermine focus. Classroom policies on phone use vary widely between institutions.

**Section 3**
Equity concerns persist. Students without home internet may fall behind when assignments assume always-on access. Some districts lend hotspots; others still rely on paper packets.

**Section 4**
Longitudinal data on standardised scores remain inconclusive. Gains in engagement do not always translate into measurable learning outcomes within a single academic year."""

    p3_text = """**Part 1**
Renewable capacity has expanded faster than grid planners anticipated in several regions. Curtailment—wasting available wind or solar because the grid cannot absorb it—has become more common.

**Part 2**
Battery storage is scaling, but capital costs and raw-material supply chains constrain deployment. Policy incentives often favour generation over storage, skewing investment.

**Part 3**
Industrial users are experimenting with demand shifting: running heavy loads when renewables peak. This behavioural layer complements hardware upgrades.

**Part 4**
International interconnectors can smooth variability by sharing surpluses across time zones, yet geopolitical risk and permitting delays slow construction."""

    p1 = ReadingPassage.objects.create(
        title="Urban green infrastructure",
        content=p1_text,
        source_note="Original short practice passage for this site.",
    )
    p2 = ReadingPassage.objects.create(
        title="Technology in schools",
        content=p2_text,
        source_note="Original short practice passage for this site.",
    )
    p3 = ReadingPassage.objects.create(
        title="Renewables and the grid",
        content=p3_text,
        source_note="Original short practice passage for this site.",
    )

    def add_q(passage, text, qtype, choices, correct):
        ReadingQuestion.objects.create(
            passage=passage,
            text=text,
            question_type=qtype,
            choices=choices,
            correct_answer=correct,
        )

    yn = ["Yes", "No", "Not Given"]
    add_q(p1, "Green spaces are associated with more walking for everyday travel.", "ynng", yn, "Yes")
    add_q(p1, "All critics agree that tree planting is always beneficial.", "ynng", yn, "No")
    add_q(p1, "The passage gives exact rainfall figures for three cities.", "ynng", yn, "Not Given")
    add_q(p1, "Volunteer groups never help with urban planting.", "ynng", yn, "No")
    add_q(
        p1,
        "What is the main risk critics highlight about planting programmes?",
        "mcq",
        ["Lack of species variety", "Maintenance funding", "Noise pollution", "Soil acidity"],
        "Maintenance funding",
    )
    add_q(
        p1,
        "Zoning rules requiring canopy cover are linked to:",
        "mcq",
        ["Higher crime rates", "Reduced heat-island growth", "Fewer parks", "More driving"],
        "Reduced heat-island growth",
    )
    add_q(
        p1,
        "Which paragraph discusses legal requirements for developers?",
        "headings",
        ["Paragraph A", "Paragraph B", "Paragraph C", "Paragraph D"],
        "Paragraph C",
    )
    add_q(
        p1,
        "Which paragraph focuses on limitations of volunteer efforts?",
        "headings",
        ["Paragraph A", "Paragraph B", "Paragraph C", "Paragraph D"],
        "Paragraph D",
    )
    add_q(
        p1,
        "Match: focus on health evidence — which paragraph?",
        "matching_info",
        ["Paragraph A", "Paragraph B", "Paragraph C", "Paragraph D"],
        "Paragraph A",
    )
    add_q(
        p1,
        "Match: cosmetic vs substance criticism — which paragraph?",
        "matching_info",
        ["Paragraph A", "Paragraph B", "Paragraph C", "Paragraph D"],
        "Paragraph B",
    )
    add_q(
        p1,
        "Match the idea: zoning and canopy rules",
        "match",
        ["Paragraph A", "Paragraph B", "Paragraph C", "Paragraph D"],
        "Paragraph C",
    )
    add_q(
        p1,
        "The passage primarily discusses:",
        "mcq",
        ["Ocean fishing", "Urban green spaces and policy", "Airport design", "Rural railways"],
        "Urban green spaces and policy",
    )
    add_q(
        p1,
        "Volunteer events mainly struggle with:",
        "mcq",
        ["Advertising", "Long-term watering plans", "Seed patents", "Winter sports"],
        "Long-term watering plans",
    )

    add_q(p2, "Digital textbooks always raise test scores within one year.", "ynng", yn, "No")
    add_q(p2, "Some students lack reliable home internet.", "ynng", yn, "Yes")
    add_q(p2, "The author recommends banning all devices in schools.", "ynng", yn, "Not Given")
    add_q(p2, "Engagement gains always equal learning gains.", "ynng", yn, "No")
    add_q(
        p2,
        "What split outcome do teachers report?",
        "mcq",
        [
            "Cheaper books and worse literacy",
            "Richer media but distraction risk",
            "No change in behaviour",
            "Uniform policies everywhere",
        ],
        "Richer media but distraction risk",
    )
    add_q(
        p2,
        "Which section covers equity and home access?",
        "headings",
        ["Section 1", "Section 2", "Section 3", "Section 4"],
        "Section 3",
    )
    add_q(
        p2,
        "Which section discusses inconclusive score data?",
        "headings",
        ["Section 1", "Section 2", "Section 3", "Section 4"],
        "Section 4",
    )
    add_q(
        p2,
        "Match: adoption where bandwidth is reliable",
        "matching_info",
        ["Section 1", "Section 2", "Section 3", "Section 4"],
        "Section 1",
    )
    add_q(
        p2,
        "Match: classroom focus and phone policies",
        "matching_info",
        ["Section 1", "Section 2", "Section 3", "Section 4"],
        "Section 2",
    )
    add_q(
        p2,
        "District responses to connectivity gaps include:",
        "mcq",
        ["Only ignoring the issue", "Lending hotspots in some places", "Closing schools", "Banning teachers"],
        "Lending hotspots in some places",
    )
    add_q(
        p2,
        "Longitudinal data on scores are:",
        "mcq",
        ["Definitively positive", "Inconclusive in the short term", "Missing entirely", "Illegal to collect"],
        "Inconclusive in the short term",
    )
    add_q(
        p2,
        "Digital textbooks mainly offer:",
        "match",
        ["Slower updates", "Instant updates and lower print costs", "No multimedia", "Mandatory phones"],
        "Instant updates and lower print costs",
    )
    add_q(
        p2,
        "The tone toward technology in classrooms is best described as:",
        "mcq",
        ["Purely negative", "Balanced, noting trade-offs", "Sarcastic", "Unrelated to education"],
        "Balanced, noting trade-offs",
    )

    add_q(p3, "Curtailment means using more coal automatically.", "ynng", yn, "No")
    add_q(p3, "Battery storage faces supply-chain constraints.", "ynng", yn, "Yes")
    add_q(p3, "The passage states exact battery prices for 2030.", "ynng", yn, "Not Given")
    add_q(p3, "Interconnectors never face permitting delays.", "ynng", yn, "No")
    add_q(
        p3,
        "Renewable output sometimes exceeds what the grid can take in—this is called:",
        "mcq",
        ["Baseload", "Curtailment", "Refining", "Subduction"],
        "Curtailment",
    )
    add_q(
        p3,
        "Policy often favours which investment over storage?",
        "mcq",
        ["Generation", "Fossil retirement only", "Nuclear fusion", "Coal subsidies"],
        "Generation",
    )
    add_q(
        p3,
        "Which part discusses industrial demand shifting?",
        "headings",
        ["Part 1", "Part 2", "Part 3", "Part 4"],
        "Part 3",
    )
    add_q(
        p3,
        "Which part mentions cross-border power lines?",
        "headings",
        ["Part 1", "Part 2", "Part 3", "Part 4"],
        "Part 4",
    )
    add_q(
        p3,
        "Match: faster-than-expected renewable build",
        "matching_info",
        ["Part 1", "Part 2", "Part 3", "Part 4"],
        "Part 1",
    )
    add_q(
        p3,
        "Match: batteries and material constraints",
        "matching_info",
        ["Part 1", "Part 2", "Part 3", "Part 4"],
        "Part 2",
    )
    add_q(
        p3,
        "Geopolitical risk affects:",
        "match",
        ["Battery chemistry only", "Interconnector projects", "Tidal clocks", "Farm subsidies"],
        "Interconnector projects",
    )
    add_q(
        p3,
        "Running heavy loads during renewable peaks is an example of:",
        "mcq",
        ["Curtailment", "Demand shifting", "Carbon tariffs", "Grid privatisation"],
        "Demand shifting",
    )
    add_q(
        p3,
        "Storage deployment is limited partly by:",
        "mcq",
        ["Lack of wind", "Capital cost and supply chains", "Too much rainfall", "Student devices"],
        "Capital cost and supply chains",
    )
    add_q(
        p3,
        "The passage’s overall scope is:",
        "mcq",
        ["Urban parks", "Renewables, grids, and flexibility tools", "Oil refining", "Shipbuilding"],
        "Renewables, grids, and flexibility tools",
    )

    exam = ReadingExam.objects.create(
        slug="full-sample",
        title="Full reading test — Sample",
        description="Three passages, 60 minutes, 40 questions. Timed like a computer-delivered academic reading test.",
        time_limit_minutes=60,
    )
    ReadingExamSection.objects.create(exam=exam, passage=p1, order=1)
    ReadingExamSection.objects.create(exam=exam, passage=p2, order=2)
    ReadingExamSection.objects.create(exam=exam, passage=p3, order=3)


def seed_if_needed():
    _seed_writing_tasks()
    _seed_writing_papers()
    _seed_full_sample_legacy()
    from .academic_expanded_seed import create_academic_expanded

    create_academic_expanded()
