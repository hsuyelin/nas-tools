import logging

from chalice import Chalice, Response

from slack_bolt import App
from slack_bolt.adapter.aws_lambda.chalice_handler import ChaliceSlackRequestHandler
from slack_bolt.adapter.aws_lambda.lambda_s3_oauth_flow import LambdaS3OAuthFlow

# process_before_response must be True when running on FaaS
bolt_app = App(
    process_before_response=True,
    authorization_test_enabled=False,
    oauth_flow=LambdaS3OAuthFlow(
        install_path="/api/slack/install",
        redirect_uri_path="/api/slack/oauth_redirect",
    ),
)


@bolt_app.event("app_mention")
def handle_app_mentions(body, say, logger):
    logger.info(body)
    say("What's up? I'm a Chalice app :wave:")


@bolt_app.command("/hello-bolt-python-chalice")
def respond_to_slack_within_3_seconds(ack):
    ack("Thanks!")


ChaliceSlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

# Don't change this variable name "app"
app = Chalice(app_name="bolt-python-chalice")
slack_handler = ChaliceSlackRequestHandler(app=bolt_app, chalice=app)


@app.route(
    "/slack/events",
    methods=["POST"],
    content_types=["application/x-www-form-urlencoded", "application/json"],
)
def events() -> Response:
    return slack_handler.handle(app.current_request)


@app.route("/slack/install", methods=["GET"])
def install() -> Response:
    return slack_handler.handle(app.current_request)


@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect() -> Response:
    return slack_handler.handle(app.current_request)


# configure aws credentials properly
# pip install -r requirements.txt
# cp -p .chalice/config.json.oauth .chalice/config.json
# # edit .chalice/config.json
# rm -rf vendor/latest_slack_bolt && cp -pr ../../src vendor/latest_slack_bolt
# chalice deploy

# for local dev
# chalice local --stage dev --port 3000
