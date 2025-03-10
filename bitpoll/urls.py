"""bitpoll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path
import django.conf.urls.i18n

from bitpoll import settings

urlpatterns = [
    re_path(r"^poll/", include("bitpoll.poll.urls")),
    re_path(r"^", include("bitpoll.base.urls")),
    re_path(r"^invitations/", include("bitpoll.invitations.urls")),
    re_path(r"^$", lambda req: redirect("index"), name="home"),
    re_path(
        r"^login/$",
        auth_views.LoginView.as_view(),
        name="login",
    ),
    # urls for nextcloud oauth login interaction
    re_path(r"^accounts/", include("allauth.urls")),
    re_path(r"^logout/$", auth_views.LogoutView.as_view(next_page="index"), name="logout"),
    re_path(r"^registration/", include("bitpoll.registration.urls")),
    re_path(r"^i18n/", include(django.conf.urls.i18n)),
    re_path(r"^admin/", admin.site.urls),
]

if settings.CALENDAR_ENABLED:
    urlpatterns += [
        re_path(r"^caldav/", include("bitpoll.caldav.urls")),
    ]

if settings.GROUP_MANAGEMENT:
    urlpatterns += [
        re_path(r"^groups/", include("bitpoll.groups.urls")),
    ]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

url_prefix = getattr(settings, "URL_PREFIX", "")
if url_prefix not in ("", "/", None):
    if not url_prefix.endswith("/"):
        url_prefix += "/"
    urlpatterns = [path(url_prefix, include(urlpatterns))]


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    use_sentry = False
    sentry_dsn = None
    event_id = None
    try:
        import sentry_sdk

        if sentry_sdk.Hub.current.client:
            use_sentry = True
            sentry_dsn = sentry_sdk.Hub.current.client.dsn
            event_id = sentry_sdk.last_event_id()
    except ImportError:
        pass

    return render(
        request,
        "500.html",
        status=500,
        context={
            "use_sentry": use_sentry,
            "sentry_public_dsn": sentry_dsn,
            "event_id": event_id,
        },
    )
