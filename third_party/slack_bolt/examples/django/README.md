## Bolt for Python - Django integration example

This example demonstrates how you can use Bolt for Python in your Django application. The project consists of two apps.

### `simple_app` - Single-workspace App Example

If you want to run a simple app like the one you've tried in the [Getting Started Guide](https://slack.dev/bolt-python/tutorial/getting-started), this is the right one for you. By default, this Django project runs this application. If you want to switch to OAuth flow supported one, modify `myslackapp/urls.py`.

To run this app, all you need to do are:

* Create a new Slack app configuration at https://api.slack.com/apps?new_app=1
* Go to "OAuth & Permissions"
  * Add `app_mentions:read`, `chat:write` in Scopes > Bot Token Scopes
* Go to "Install App"
  * Click "Install to Workspace"
  * Complete the installation flow
  * Copy the "Bot User OAuth Token" value, which starts with `xoxb-`

You can start your Django application this way:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

export SLACK_SIGNING_SECRET=(You can find this value at Settings > Basic Information > App Credentials > Signing Secret)
export SLACK_BOT_TOKEN=(You can find this value at Settings > Install App > Bot User OAuth Token)

python manage.py migrate
python manage.py runserver 0.0.0.0:3000
```

As you did at [Getting Started Guide](https://slack.dev/bolt-python/tutorial/getting-started), configure ngrok or something similar to serve a public endpoint. Lastly,

* Go back to the Slack app configuration page
* Go to "Event Subscriptions"
  * Turn the feature on
  * Set the "Request URL" to `https://{your public domain}/slack/events`
* Go to the Slack workspace you've installed this app
* Invite the app's bot user to a channel
* Mention the bot user in the channel
* You'll see a reply from your app's bot user!

### `oauth_app` - Multiple-workspace App Example (OAuth flow supported)

By default, this Django project runs this application. If you want to switch to OAuth flow supported one, modify `myslackapp/urls.py`. 

This example uses SQLite. If you are looking for an example using MySQL, check the `mysql-docker-compose.yml` and the comment in `myslackapp/settings.py`.


To run this app, all you need to do are:

* Create a new Slack app configuration at https://api.slack.com/apps?new_app=1
* Go to "OAuth & Permissions"
  * Add `app_mentions:read`, `chat:write` in Scopes > Bot Token Scopes
* Follow the instructions [here](https://slack.dev/bolt-python/concepts#authenticating-oauth) for configuring OAuth flow supported Slack apps

You can start your Django application this way:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

export SLACK_SIGNING_SECRET=(You can find this value at Settings > Basic Information > App Credentials > Signing Secret)
export SLACK_CLIENT_ID=(You can find this value at Settings > Basic Information > App Credentials > Client ID)
export SLACK_CLIENT_SECRET=(You can find this value at Settings > Basic Information > App Credentials > Client Secret)
export SLACK_SCOPES=app_mentions:read,chat:write

python manage.py migrate
python manage.py runserver 0.0.0.0:3000
```

As you did at [Getting Started Guide](https://slack.dev/bolt-python/tutorial/getting-started), configure ngrok or something similar to serve a public endpoint. Lastly,

* Go back to the Slack app configuration page
* Go to "Event Subscriptions"
  * Turn the feature on
  * Set the "Request URL" to `https://{your public domain}/slack/events`
* Visit `https://{your public domain}/slack/install` and complete the installation flow
* Add `https://{your public domain}/slack/oauth_redirect` as your redirect URL for your app in Oauth & Permissions on the Slack app configuration page. 
* Invite the app's bot user to a channel
* Mention the bot user in the channel
* You'll see a reply from your app's bot user!
