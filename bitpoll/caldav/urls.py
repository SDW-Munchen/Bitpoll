from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^change/$", views.change_calendar, name="change_calendar"),
    re_path(r"^edit/(\d+)/save/$", views.change_calendar, name="edit_save_calendar"),
    re_path(r"^edit/(\d+)/$", views.edit_calendar, name="edit_calendar"),
]
