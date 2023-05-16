#
# docker build . -t your-repo/hello-bolt
#
FROM tiangolo/uvicorn-gunicorn:python3.8-slim
WORKDIR /app/
COPY *.py /app/
COPY requirements.txt /app/
RUN pip install -U pip && pip install -r requirements.txt

#
# docker run -e SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET -e SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN -e VARIABLE_NAME="api" -p 80:80 -it your-repo/hello-bolt
# or
# docker run -e SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET -e SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN -e VARIABLE_NAME="api" -p 3000:80 -it your-repo/hello-bolt
