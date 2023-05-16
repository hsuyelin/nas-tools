from slack_bolt.oauth.oauth_flow import OAuthFlow
from slack_bolt.adapter.asgi.http_request import AsgiHttpRequest

from slack_bolt import App

from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse

from slack_bolt.adapter.asgi.base_handler import BaseSlackRequestHandler


class SlackRequestHandler(BaseSlackRequestHandler):
    def __init__(self, app: App, path: str = "/slack/events"):  # type: ignore
        """Setup Bolt as an ASGI web framework, this will make your application compatible with ASGI web servers.
        This can be used for production deployment.

        With the default settings, `http://localhost:3000/slack/events`
        Run Bolt with [uvicron](https://www.uvicorn.org/)

            # Python
            app = App()
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
        return self.app.dispatch(
            BoltRequest(body=await request.get_raw_body(), query=request.query_string, headers=request.get_headers())
        )

    async def handle_installation(self, request: AsgiHttpRequest) -> BoltResponse:
        oauth_flow: OAuthFlow = self.app.oauth_flow
        return oauth_flow.handle_installation(
            BoltRequest(body=await request.get_raw_body(), query=request.query_string, headers=request.get_headers())
        )

    async def handle_callback(self, request: AsgiHttpRequest) -> BoltResponse:
        oauth_flow: OAuthFlow = self.app.oauth_flow
        return oauth_flow.handle_callback(
            BoltRequest(body=await request.get_raw_body(), query=request.query_string, headers=request.get_headers())
        )
