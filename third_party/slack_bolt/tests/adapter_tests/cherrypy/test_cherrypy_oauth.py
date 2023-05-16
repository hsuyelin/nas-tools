import cherrypy
from cherrypy.test import helper
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt.adapter.cherrypy import SlackRequestHandler
from slack_bolt.app import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestCherryPy(helper.CPWebCase):
    helper.CPWebCase.interactive = False
    signing_secret = "secret"
    signature_verifier = SignatureVerifier(signing_secret)

    @classmethod
    def setup_server(cls):
        cls.old_os_env = remove_os_env_temporarily()

        signing_secret = "secret"
        valid_token = "xoxb-valid"
        mock_api_server_base_url = "http://localhost:8888"
        web_client = WebClient(
            token=valid_token,
            base_url=mock_api_server_base_url,
        )
        app = App(
            client=web_client,
            signing_secret=signing_secret,
            oauth_settings=OAuthSettings(
                client_id="111.111",
                client_secret="xxx",
                scopes=["chat:write", "commands"],
            ),
        )
        handler = SlackRequestHandler(app)

        class SlackApp(object):
            @cherrypy.expose
            @cherrypy.tools.slack_in()
            def install(self, **kwargs):
                return handler.handle()

        cherrypy.tree.mount(SlackApp(), "/slack")

    @classmethod
    def teardown_class(cls):
        cls.supervisor.stop()
        restore_os_env(cls.old_os_env)

    def test_oauth(self):
        cherrypy.request.process_request_body = False
        self.getPage("/slack/install", method="GET")
        self.assertStatus("200 OK")
