
from django.urls import re_path
from . import views

urlpatterns = [
    re_path('users', views.users_view),
    re_path('test', views.test, name="A test view app route"),
    re_path("user", views.user_view),
    re_path("signin", views.signin_view),
    re_path("signup", views.users_view),
    re_path("verify", views.verification),
]
