"""myslackapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin  # noqa: F401
from django.urls import path

# Set this flag to False if you want to enable oauth_app instead
is_simple_app = True

if is_simple_app:
    # A simple app that works only for a single Slack workspace
    # (prerequisites)
    # export SLACK_BOT_TOKEN=
    # export SLACK_SIGNING_SECRET=
    from simple_app.urls import slack_events_handler

    urlpatterns = [path("slack/events", slack_events_handler)]
else:
    # OAuth flow supported app
    # (prerequisites)
    # export SLACK_CLIENT_ID=
    # export SLACK_CLIENT_SECRET=
    # export SLACK_SIGNING_SECRET=
    # export SLACK_SCOPES=app_mentions:read
    from oauth_app.urls import slack_events_handler, slack_oauth_handler

    urlpatterns = [
        path("slack/events", slack_events_handler, name="handle"),
        path("slack/install", slack_oauth_handler, name="install"),
        path("slack/oauth_redirect", slack_oauth_handler, name="oauth_redirect"),
    ]
