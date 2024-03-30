from . import views
from django.urls import path

app_name = "app"

urlpatterns = [
    path("", views.home, name="home"),
    path('index/', views.index, name="index"),
    path(
        "problem_statement/<int:problem_statement_id>/",
        views.problem_statement,
        name="problem_statement",
    ),
    path(
        "create_problem_statement/",
        views.create_problem_statement,
        name="create_problem_statement",
    ),
    path(
        "submit_solution/<int:problem_statement_id>/",
        views.submit_solution,
        name="submit_solution",
    ),
    path("teacher_rating/<int:solution_id>/", views.teacher_rating, name="teacher_rating"),
    path("detail_solution/<int:solution_id>/", views.detail_solution, name="detail_solution"),
    path("autograde_solution/<int:solution_id>/", views.autograde_solution, name="autograde_solution"),
]
