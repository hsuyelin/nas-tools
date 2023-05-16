#
# https://cloud.google.com/run/docs/quickstarts/build-and-deploy
#
# export PROJECT_ID=`gcloud config get-value project`
# export SLACK_SIGNING_SECRET=
# export SLACK_BOT_TOKEN=
# gcloud builds submit --tag gcr.io/$PROJECT_ID/helloworld
# gcloud run deploy helloworld --image gcr.io/$PROJECT_ID/helloworld --platform managed --update-env-vars SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET,SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN
#

# ----------------------------------------------
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8.5-slim-buster

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install -U pip && pip install -r requirements.txt

# Start Sanic server
ENTRYPOINT python main.py
