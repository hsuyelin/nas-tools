---
title: Logging
lang: en
slug: logging
order: 4
---

<div class="section-content">
By default, Bolt will log information from your app to the output destination. After you've imported the `logging` module, you can customize the root log level by passing the `level` parameter to `basicConfig()`. The available log levels in order of least to most severe are `debug`, `info`, `warning`, `error`, and `critical`.

Outside of a global context, you can also log a single message corresponding to a specific level. Because Bolt uses Python’s [standard logging module](https://docs.python.org/3/library/logging.html), you can use any its features.
</div>

```python
import logging

# logger in a global context
# requires importing logging
logging.basicConfig(level=logging.DEBUG)

@app.event("app_mention")
def handle_mention(body, say, logger):
    user = body["event"]["user"]
    # single logger call
    # global logger is passed to listener
    logger.debug(body)
    say(f"{user} mentioned your app")
```
