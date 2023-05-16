# https://cloud.google.com/functions/docs/first-python

import logging

from slack_bolt.oauth.oauth_settings import OAuthSettings

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App
from datastore import GoogleDatastoreInstallationStore, GoogleDatastoreOAuthStateStore

from google.cloud import datastore

datastore_client = datastore.Client()
logger = logging.getLogger(__name__)

# process_before_response must be True when running on FaaS
app = App(
    process_before_response=True,
    installation_store=GoogleDatastoreInstallationStore(
        datastore_client=datastore_client,
        logger=logger,
    ),
    oauth_settings=OAuthSettings(
        state_store=GoogleDatastoreOAuthStateStore(
            datastore_client=datastore_client,
            logger=logger,
        ),
    ),
)


@app.command("/hello-bolt-python-gcp")
def hello_command(ack):
    ack("Hi from Google Cloud Functions!")


@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    say("Hi from Google Cloud Functions!")


# Flask adapter
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from flask import Request


handler = SlackRequestHandler(app)


# Cloud Function
def hello_bolt_app(req: Request):
    """HTTP Cloud Function.
    Args:
        req (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    return handler.handle(req)


# For local development
# python main.py
if __name__ == "__main__":
    from flask import Flask, request

    flask_app = Flask(__name__)

    @flask_app.route("/function", methods=["GET", "POST"])
    def handle_anything():
        return handler.handle(request)

    flask_app.run(port=3000)


# Step1: Create a new Slack App: https://api.slack.com/apps
# Bot Token Scopes: app_mentions:read,chat:write,commands

# Step2: Set env variables
# cp .env.yaml.oauth-sample .env.yaml
# vi .env.yaml

# Step3: Create a new Google Cloud project
# gcloud projects create YOUR_PROJECT_NAME
# gcloud config set project YOUR_PROJECT_NAME

# Step4: Deploy a function in the project
# cp oauth_main.py main.py
# gcloud functions deploy hello_bolt_app --runtime python38 --trigger-http --allow-unauthenticated --env-vars-file .env.yaml
# gcloud functions describe hello_bolt_app

# Step5: Set Request URL
# Set https://us-central1-YOUR_PROJECT_NAME.cloudfunctions.net/hello_bolt_app to the following:
#  * slash command: /hello-bolt-python-gcp
#  * Events Subscriptions & add `app_mention` event
