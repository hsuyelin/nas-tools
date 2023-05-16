---
title: Authorization
lang: en
slug: authorization
order: 5
---

<div class="section-content">
Authorization is the process of determining which Slack credentials should be available while processing an incoming Slack request.

Apps installed on a single workspace can simply pass their bot token into the `App` constructor using the `token` parameter. However, if your app will be installed on multiple workspaces, you have two options. The easier option is to use the built-in OAuth support. This will handle setting up OAuth routes and verifying state. Read the section on [authenticating with OAuth](#authenticating-oauth) for details.

For a more custom solution, you can set the `authorize` parameter to a function upon `App` instantiation. The `authorize` function should return [an instance of `AuthorizeResult`](https://github.com/slackapi/bolt-python/blob/main/slack_bolt/authorization/authorize_result.py), which contains information about who and where the request is coming from.

`AuthorizeResult` should have a few specific properties, all of type `str`:
- Either **`bot_token`** (xoxb) *or* **`user_token`** (xoxp) are **required**. Most apps will use `bot_token` by default. Passing a token allows built-in functions (like `say()`) to work.
- **`bot_user_id`** and **`bot_id`**, if using a `bot_token`.
- **`enterprise_id`** and **`team_id`**, which can be found in requests sent to your app.
- **`user_id`** only when using `user_token`.
</div>

```python
import os
from slack_bolt import App
# Import the AuthorizeResult class
from slack_bolt.authorization import AuthorizeResult

# This is just an example (assumes there are no user tokens)
# You should store authorizations in a secure DB
installations = [
    {
      "enterprise_id": "E1234A12AB",
      "team_id": "T12345",
      "bot_token": "xoxb-123abc",
      "bot_id": "B1251",
      "bot_user_id": "U12385"
    },
    {
      "team_id": "T77712",
      "bot_token": "xoxb-102anc",
      "bot_id": "B5910",
      "bot_user_id": "U1239",
      "enterprise_id": "E1234A12AB"
    }
]

def authorize(enterprise_id, team_id, logger):
    # You can implement your own logic to fetch token here
    for team in installations:
        # enterprise_id doesn't exist for some teams
        is_valid_enterprise = True if (("enterprise_id" not in team) or (enterprise_id == team["enterprise_id"])) else False
        if ((is_valid_enterprise == True) and (team["team_id"] == team_id)):
          # Return an instance of AuthorizeResult
          # If you don't store bot_id and bot_user_id, could also call `from_auth_test_response` with your bot_token to automatically fetch them
          return AuthorizeResult(
              enterprise_id=enterprise_id,
              team_id=team_id,
              bot_token=team["bot_token"],
              bot_id=team["bot_id"],
              bot_user_id=team["bot_user_id"]
          )

    logger.error("No authorization information was found")

app = App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    authorize=authorize
)
```
