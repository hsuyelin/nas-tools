"""Lazy listener runner is a beta feature for the apps running on Function-as-a-Service platforms.

    def respond_to_slack_within_3_seconds(body, ack):
        text = body.get("text")
        if text is None or len(text) == 0:
            ack(f":x: Usage: /start-process (description here)")
        else:
            ack(f"Accepted! (task: {body['text']})")

    import time
    def run_long_process(respond, body):
        time.sleep(5)  # longer than 3 seconds
        respond(f"Completed! (task: {body['text']})")

    app.command("/start-process")(
        # ack() is still called within 3 seconds
        ack=respond_to_slack_within_3_seconds,
        # Lazy function is responsible for processing the event
        lazy=[run_long_process]
    )

Refer to https://slack.dev/bolt-python/concepts#lazy-listeners for more details.
"""
# Don't add async module imports here
from .runner import LazyListenerRunner
from .thread_runner import ThreadLazyListenerRunner

__all__ = [
    "LazyListenerRunner",
    "ThreadLazyListenerRunner",
]
