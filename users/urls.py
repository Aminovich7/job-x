from django.urls import path

from .views import (
    change_password_view,
    login_view,
    logout_view,
    profile_view,
    register_view,
)


urlpatterns = [
    path("register/", register_view),
    path("login/", login_view),
    path("logout/", logout_view),
    path("profile/", profile_view),
    path("profile/password/", change_password_view),
]
