import logging
import os
from typing import Optional

from slack_sdk.socket_mode.aiohttp import SocketModeClient

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

logging.basicConfig(level=logging.DEBUG)

#
# Socket Mode Bolt app
#

# Install the Slack app and get xoxb- token in advance
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
socket_mode_client: Optional[SocketModeClient] = None


@app.event("app_mention")
async def event_test(event, say):
    await say(f"Hi there, <@{event['user']}>!")


#
# Web app for hosting the healthcheck endpoint for k8s etc.
#

from aiohttp import web


async def healthcheck(_req: web.Request):
    if socket_mode_client is not None and socket_mode_client.is_connected():
        return web.Response(status=200, text="OK")
    return web.Response(status=503, text="The Socket Mode client is inactive")


web_app = app.web_app()
web_app.add_routes([web.get("/health", healthcheck)])


#
# Start the app
#

if __name__ == "__main__":

    async def start_socket_mode(_web_app: web.Application):
        handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        await handler.connect_async()
        global socket_mode_client
        socket_mode_client = handler.client

    async def shutdown_socket_mode(_web_app: web.Application):
        await socket_mode_client.close()

    web_app.on_startup.append(start_socket_mode)
    web_app.on_shutdown.append(shutdown_socket_mode)
    web.run_app(app=web_app, port=8080)
