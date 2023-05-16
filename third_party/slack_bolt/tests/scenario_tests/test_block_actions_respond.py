from slack_sdk import WebClient

from slack_bolt import BoltRequest, App, Say, Respond, Ack
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestBlockActionsRespond:
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    web_client = WebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)

    def test_mock_server_is_running(self):
        resp = self.web_client.api_test()
        assert resp is not None

    def test_success(self):
        app = App(client=self.web_client)

        @app.event("app_mention")
        def handle_app_mention_events(say: Say):
            say(
                text="This is a section block with a button.",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This is a section block with a button.",
                        },
                        "accessory": {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Click Me"},
                            "value": "clicked",
                            "action_id": "button",
                        },
                    }
                ],
            )

        @app.action("button")
        def handle_button_clicks(body: dict, ack: Ack, respond: Respond):
            respond(
                text="hey!",
                thread_ts=body["message"]["ts"],
                response_type="in_channel",
                replace_original=False,
            )
            ack()

        # app_mention event
        request = BoltRequest(
            mode="socket_mode",
            body={
                "team_id": "T0G9PQBBK",
                "api_app_id": "A111",
                "event": {
                    "type": "app_mention",
                    "text": "<@U111> hey",
                    "user": "U222",
                    "ts": "1678252212.229129",
                    "blocks": [
                        {
                            "type": "rich_text",
                            "block_id": "BCCO",
                            "elements": [
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {"type": "user", "user_id": "U111"},
                                        {"type": "text", "text": " hey"},
                                    ],
                                }
                            ],
                        }
                    ],
                    "team": "T0G9PQBBK",
                    "channel": "C111",
                    "event_ts": "1678252212.229129",
                },
                "type": "event_callback",
                "event_id": "Ev04SPP46R6J",
                "event_time": 1678252212,
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T0G9PQBBK",
                        "user_id": "U111",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": False,
                "event_context": "4-xxx",
            },
        )
        response = app.dispatch(request)
        assert response.status == 200

        # block_actions request
        request = BoltRequest(
            mode="socket_mode",
            body={
                "type": "block_actions",
                "user": {"id": "U111"},
                "api_app_id": "A111",
                "container": {
                    "type": "message",
                    "message_ts": "1678252213.679169",
                    "channel_id": "C111",
                    "is_ephemeral": False,
                },
                "trigger_id": "4916855695380.xxx.yyy",
                "team": {"id": "T0G9PQBBK"},
                "enterprise": None,
                "is_enterprise_install": False,
                "channel": {"id": "C111"},
                "message": {
                    "bot_id": "B111",
                    "type": "message",
                    "text": "This is a section block with a button.",
                    "user": "U222",
                    "ts": "1678252213.679169",
                    "app_id": "A111",
                    "blocks": [
                        {
                            "type": "section",
                            "block_id": "8KR",
                            "text": {
                                "type": "mrkdwn",
                                "text": "This is a section block with a button.",
                                "verbatim": False,
                            },
                            "accessory": {
                                "type": "button",
                                "action_id": "button",
                                "text": {"type": "plain_text", "text": "Click Me"},
                                "value": "clicked",
                            },
                        }
                    ],
                    "team": "T0G9PQBBK",
                },
                "state": {"values": {}},
                "response_url": "http://localhost:8888/webhook",
                "actions": [
                    {
                        "action_id": "button",
                        "block_id": "8KR",
                        "text": {"type": "plain_text", "text": "Click Me"},
                        "value": "clicked",
                        "type": "button",
                        "action_ts": "1678252216.469172",
                    }
                ],
            },
        )
        response = app.dispatch(request)
        assert response.status == 200
