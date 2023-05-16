---
title: Token rotation
lang: en
slug: token-rotation
order: 6
---

<div class="section-content">
Supported in Bolt for Python as of [v1.7.0](https://github.com/slackapi/bolt-python/releases/tag/v1.7.0), token rotation provides an extra layer of security for your access tokens and is defined by the [OAuth V2 RFC](https://datatracker.ietf.org/doc/html/rfc6749#section-10.4). 

Instead of an access token representing an existing installation of your Slack app indefinitely, with token rotation enabled, access tokens expire. A refresh token acts as a long-lived way to refresh your access tokens.

Bolt for Python supports and will handle token rotation automatically so long as the [built-in OAuth](https://slack.dev/bolt-python/concepts#authenticating-oauth) functionality is used.

For more information about token rotation, please see the [documentation](https://api.slack.com/authentication/rotation).
</div>
