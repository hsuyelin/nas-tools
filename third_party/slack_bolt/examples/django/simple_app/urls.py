from django.urls import path

from slack_bolt.adapter.django import SlackRequestHandler
from .slack_listeners import app

handler = SlackRequestHandler(app=app)

from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def slack_events_handler(request: HttpRequest):
    return handler.handle(request)


urlpatterns = [
    path("slack/events", slack_events_handler, name="slack_events"),
]
