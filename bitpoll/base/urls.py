from django.urls import path, include, re_path

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r"social_account", views.SocialAccountViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    re_path(r"^settings/$", views.user_settings, name="settings"),
    re_path(r"^$", views.index, name="index"),
    re_path(r"^imprint/$", views.imprint, name="imprint"),
    re_path(r"^about/$", views.about, name="about"),
    re_path(r"^licenses/$", views.licenses, name="base_licenses"),
    re_path(r"^technical_info/$", views.tecnical, name="technical"),
    re_path(r"^autocomplete$", views.autocomplete, name="base_autocomplete"),
    re_path(r"^problems$", views.problems, name="base_problems"),
]
