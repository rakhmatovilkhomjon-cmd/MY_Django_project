from django.urls import path
from . import views

app_name = "ielts"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics_view, name="analytics"),
    path("writing/review/<int:attempt_id>/", views.writing_review_view, name="writing_review"),
    path("writing/", views.writing_hub, name="writing_hub"),
    path("writing/exam/random/", views.writing_exam_random, name="writing_exam_random"),
    path("writing/full/<int:paper_id>/", views.writing_full_view, name="writing_full"),
    path("writing/full/<int:paper_id>/submit/", views.submit_writing_full, name="submit_writing_full"),
    path("writing/<int:task_id>/", views.writing_view, name="writing"),
    path("autosave-writing/", views.autosave_writing, name="autosave_writing"),
    path("submit-writing/<int:task_id>/", views.submit_writing, name="submit_writing"),
    path("reading/", views.reading_hub, name="reading_hub"),
    path("reading/passages/", views.reading_single_passages_view, name="reading_single_passages"),
    path("reading/exam/random/", views.reading_exam_random, name="reading_exam_random"),
    path("reading/exam/<int:exam_id>/", views.reading_exam_view, name="reading_exam"),
    path("reading/passage/<int:passage_id>/", views.reading_passage_view, name="reading_passage"),
    path("reading/practice/<slug:type_slug>/", views.reading_practice_view, name="reading_practice"),
    path("submit-reading/<int:passage_id>/", views.submit_reading, name="submit_reading"),
    path("result/<int:attempt_id>/", views.result_view, name="result"),
    path("result/exam/<int:attempt_id>/", views.exam_result_view, name="exam_result"),
]
