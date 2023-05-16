# Getting Started with ⚡️ Bolt for Python
> Slack app example from 📚 [Getting started with Bolt for Python][1]

## Overview

This is a Slack app built with the [Bolt for Python framework][2] that showcases
responding to events and interactive buttons.

## Running locally

### 1. Setup environment variables

```zsh
# Replace with your signing secret and token
export SLACK_BOT_TOKEN=<your-bot-token>
export SLACK_SIGNING_SECRET=<your-signing-secret>
```

### 2. Setup your local project

```zsh
# Clone this project onto your machine
git clone https://github.com/slackapi/bolt-python.git

# Change into this project
cd bolt-python/examples/getting_started/

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### 3. Start servers

[Setup ngrok][3] to create a local requests URL for development.

```zsh
ngrok http 3000
python3 app.py
```

[1]: https://slack.dev/bolt-python/tutorial/getting-started
[2]: https://slack.dev/bolt-python/
[3]: https://slack.dev/bolt-python/tutorial/getting-started#setting-up-events
