import logging

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App, Ack

app = App()


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.command("/hello-bolt-python")
def test_command(body, client, ack, logger):
    logger.info(body)
    ack("I got it!")
    res = client.dialog_open(
        trigger_id=body["trigger_id"],
        dialog={
            "callback_id": "dialog-callback-id",
            "title": "Request a Ride",
            "submit_label": "Request",
            "notify_on_cancel": True,
            "state": "Limo",
            "elements": [
                {"type": "text", "label": "Pickup Location", "name": "loc_origin"},
                {
                    "type": "text",
                    "label": "Dropoff Location",
                    "name": "loc_destination",
                },
                {
                    "label": "Type",
                    "name": "types",
                    "type": "select",
                    "data_source": "external",
                },
            ],
        },
    )
    logger.info(res)


@app.action("dialog-callback-id")
def dialog_submission_or_cancellation(ack: Ack, body: dict):
    if body["type"] == "dialog_cancellation":
        # This can be sent only when notify_on_cancel is True
        ack()
        return

    errors = []
    submission = body["submission"]
    if len(submission["loc_origin"]) <= 3:
        errors = [
            {
                "name": "loc_origin",
                "error": "Pickup Location must be longer than 3 characters",
            }
        ]
    if len(errors) > 0:
        # or ack({"errors": errors})
        ack(errors=errors)
    else:
        ack()


# @app.action({"type": "dialog_submission", "callback_id": "dialog-callback-id"})
# def dialog_submission_or_cancellation(ack: Ack, body: dict):
#     errors = []
#     submission = body["submission"]
#     if len(submission["loc_origin"]) <= 3:
#         errors = [
#             {
#                 "name": "loc_origin",
#                 "error": "Pickup Location must be longer than 3 characters"
#             }
#         ]
#     if len(errors) > 0:
#         # or ack({"errors": errors})
#         ack(errors=errors)
#     else:
#         ack()
#
# @app.action({"type": "dialog_cancellation", "callback_id": "dialog-callback-id"})
# def dialog_cancellation(ack):
#     ack()


# @app.options({"type": "dialog_suggestion", "callback_id": "dialog-callback-id"})
@app.options("dialog-callback-id")
def dialog_suggestion(ack):
    ack(
        {
            "options": [
                {
                    "label": "[UXD-342] The button color should be artichoke green, not jalapeño",
                    "value": "UXD-342",
                },
                {"label": "[FE-459] Remove the marquee tag", "value": "FE-459"},
                {
                    "label": "[FE-238] Too many shades of gray in master CSS",
                    "value": "FE-238",
                },
            ]
        }
    )


if __name__ == "__main__":
    app.start(3000)

# pip install slack_bolt
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# python dialogs_app.py
