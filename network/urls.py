
from django.urls import path

from . import views

urlpatterns = [
    # Pages
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API
    path("save_post", views.save_post, name="save_post"),
    path("upd_post", views.upd_post, name="upd_post"),
    path("get_posts", views.get_posts, name="get_posts"),
    path("get_profile", views.get_profile, name="get_profile"),
    path("upd_like", views.upd_like, name="upd_like"),
    path("upd_follow", views.upd_follow, name="follow")
]
