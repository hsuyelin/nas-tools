from slack_bolt.oauth.async_oauth_flow import AsyncOAuthFlow

from slack_bolt.adapter.asgi.http_request import AsgiHttpRequest
from slack_bolt.adapter.asgi.builtin import SlackRequestHandler

from slack_bolt.async_app import AsyncApp

from slack_bolt.async_app import AsyncBoltRequest
from slack_bolt.response import BoltResponse


class AsyncSlackRequestHandler(SlackRequestHandler):
    app: AsyncApp

    def __init__(self, app: AsyncApp, path: str = "/slack/events"):
        """Setup Bolt as an ASGI web framework, this will make your application compatible with ASGI web servers.
        This can be used for production deployment.

        With the default settings, `http://localhost:3000/slack/events`
        Run Bolt with [uvicron](https://www.uvicorn.org/)

            # Python
            app = AsyncApp()
            api = SlackRequestHandler(app)

            # bash
            export SLACK_SIGNING_SECRET=***
            export SLACK_BOT_TOKEN=xoxb-***
            uvicorn app:api --port 3000 --log-level debug

        Args:
            app: Your bolt application
            path: The path to handle request from Slack (Default: `/slack/events`)
        """
        self.path = path
        self.app = app

    async def dispatch(self, request: AsgiHttpRequest) -> BoltResponse:
        return await self.app.async_dispatch(
            AsyncBoltRequest(body=await request.get_raw_body(), query=request.query_string, headers=request.get_headers())
        )

    async def handle_installation(self, request: AsgiHttpRequest) -> BoltResponse:
        oauth_flow: AsyncOAuthFlow = self.app.oauth_flow
        return await oauth_flow.handle_installation(
            AsyncBoltRequest(body=await request.get_raw_body(), query=request.query_string, headers=request.get_headers())
        )

    async def handle_callback(self, request: AsgiHttpRequest) -> BoltResponse:
        oauth_flow: AsyncOAuthFlow = self.app.oauth_flow
        return await oauth_flow.handle_callback(
            AsyncBoltRequest(body=await request.get_raw_body(), query=request.query_string, headers=request.get_headers())
        )
