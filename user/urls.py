from . import views
from django.urls import path

app_name = "user"

urlpatterns = [
    path("login", views.signin, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("add_user", views.add_user, name="add_user"),
]
