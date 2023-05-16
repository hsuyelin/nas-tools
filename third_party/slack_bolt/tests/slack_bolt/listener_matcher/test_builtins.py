import json
import re
from urllib.parse import quote

from slack_bolt import BoltRequest, BoltResponse
from slack_bolt.listener_matcher.builtins import (
    block_action,
    action,
    workflow_step_execute,
    event,
    shortcut,
)


class TestBuiltins:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_block_action(self):
        body = {
            "type": "block_actions",
            "actions": [
                {
                    "type": "button",
                    "action_id": "valid_action_id",
                    "block_id": "b",
                    "action_ts": "111.222",
                    "value": "v",
                }
            ],
        }
        raw_body = f"payload={quote(json.dumps(body))}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        req = BoltRequest(body=raw_body, headers=headers)
        resp = BoltResponse(status=404)

        assert block_action("valid_action_id").matches(req, resp) is True
        assert block_action("invalid_action_id").matches(req, resp) is False
        assert block_action(re.compile("valid_.+")).matches(req, resp) is True
        assert block_action(re.compile("invalid_.+")).matches(req, resp) is False

        assert action("valid_action_id").matches(req, resp) is True
        assert action("invalid_action_id").matches(req, resp) is False
        assert action(re.compile("valid_.+")).matches(req, resp) is True
        assert action(re.compile("invalid_.+")).matches(req, resp) is False

        assert action({"action_id": "valid_action_id"}).matches(req, resp) is True
        assert action({"action_id": "invalid_action_id"}).matches(req, resp) is False
        assert action({"action_id": re.compile("valid_.+")}).matches(req, resp) is True
        assert action({"action_id": re.compile("invalid_.+")}).matches(req, resp) is False

        # block_id + action_id
        assert action({"action_id": "valid_action_id", "block_id": "b"}).matches(req, resp) is True
        assert action({"action_id": "invalid_action_id", "block_id": "b"}).matches(req, resp) is False
        assert action({"action_id": re.compile("valid_.+"), "block_id": "b"}).matches(req, resp) is True
        assert action({"action_id": re.compile("invalid_.+"), "block_id": "b"}).matches(req, resp) is False

        assert action({"action_id": "valid_action_id", "block_id": "bbb"}).matches(req, resp) is False
        assert action({"action_id": "invalid_action_id", "block_id": "bbb"}).matches(req, resp) is False
        assert action({"action_id": re.compile("valid_.+"), "block_id": "bbb"}).matches(req, resp) is False
        assert action({"action_id": re.compile("invalid_.+"), "block_id": "bbb"}).matches(req, resp) is False

        # with type
        assert action({"action_id": "valid_action_id", "type": "block_actions"}).matches(req, resp) is True
        assert action({"callback_id": "valid_action_id", "type": "interactive_message"}).matches(req, resp) is False
        assert action({"callback_id": "valid_action_id", "type": "workflow_step_edit"}).matches(req, resp) is False

    def test_workflow_step_execute(self):
        payload = {
            "team_id": "T111",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "workflow_step_execute",
                "callback_id": "copy_review",
                "workflow_step": {
                    "workflow_step_execute_id": "zzz-execution",
                    "workflow_id": "12345",
                    "workflow_instance_id": "11111",
                    "step_id": "111-222-333-444-555",
                    "inputs": {"taskName": {"value": "a"}},
                    "outputs": [{"name": "taskName", "type": "text", "label": "Task Name"}],
                },
                "event_ts": "1601541373.225894",
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1601541373,
        }

        request = BoltRequest(body=f"payload={quote(json.dumps(payload))}")

        m = workflow_step_execute("copy_review")
        assert m.matches(request, None) == True

        m = workflow_step_execute("copy_review_2")
        assert m.matches(request, None) == False

        m = workflow_step_execute(re.compile("copy_.+"))
        assert m.matches(request, None) == True

    def test_events(self):
        request = BoltRequest(body=json.dumps(event_payload))

        m = event("app_mention")
        assert m.matches(request, None)
        m = event({"type": "app_mention"})
        assert m.matches(request, None)
        m = event("message")
        assert not m.matches(request, None)
        m = event({"type": "message"})
        assert not m.matches(request, None)

        request = BoltRequest(body=f"payload={quote(json.dumps(shortcut_payload))}")

        m = event("app_mention")
        assert not m.matches(request, None)
        m = event({"type": "app_mention"})
        assert not m.matches(request, None)

    def test_global_shortcuts(self):
        request = BoltRequest(body=f"payload={quote(json.dumps(shortcut_payload))}")

        m = shortcut("test-shortcut")
        assert m.matches(request, None)
        m = shortcut({"callback_id": "test-shortcut", "type": "shortcut"})
        assert m.matches(request, None)

        m = shortcut("test-shortcut!!!")
        assert not m.matches(request, None)
        m = shortcut({"callback_id": "test-shortcut", "type": "message_action"})
        assert not m.matches(request, None)
        m = shortcut({"callback_id": "test-shortcut!!!", "type": "shortcut"})
        assert not m.matches(request, None)

    def test_message_shortcuts(self):
        request = BoltRequest(body=f"payload={quote(json.dumps(message_shortcut_payload))}")

        m = shortcut("test-shortcut")
        assert m.matches(request, None)
        m = shortcut({"callback_id": "test-shortcut", "type": "message_action"})
        assert m.matches(request, None)

        m = shortcut("test-shortcut!!!")
        assert not m.matches(request, None)
        m = shortcut({"callback_id": "test-shortcut", "type": "shortcut"})
        assert not m.matches(request, None)
        m = shortcut({"callback_id": "test-shortcut!!!", "type": "message_action"})
        assert not m.matches(request, None)


event_payload = {
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "type": "app_mention",
        "text": "<@W111> Hi there!",
        "user": "W222",
        "ts": "1595926230.009600",
        "event_ts": "1595926230.009600",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1595926230,
    "authorizations": [
        {
            "enterprise_id": "E111",
            "team_id": "T111",
            "user_id": "W111",
            "is_bot": True,
            "is_enterprise_install": True,
        }
    ],
}

shortcut_payload = {
    "type": "shortcut",
    "token": "verification_token",
    "action_ts": "111.111",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Org Name",
    },
    "user": {"id": "W111", "username": "primary-owner", "team_id": "T111"},
    "callback_id": "test-shortcut",
    "trigger_id": "111.111.xxxxxx",
}


message_shortcut_payload = {
    "type": "message_action",
    "token": "verification_token",
    "action_ts": "1583637157.207593",
    "team": {
        "id": "T111",
        "domain": "test-test",
        "enterprise_id": "E111",
        "enterprise_name": "Org Name",
    },
    "user": {"id": "W111", "name": "test-test"},
    "channel": {"id": "C111", "name": "dev"},
    "callback_id": "test-shortcut",
    "trigger_id": "111.222.xxx",
    "message_ts": "1583636382.000300",
    "message": {
        "client_msg_id": "zzzz-111-222-xxx-yyy",
        "type": "message",
        "text": "<@W222> test",
        "user": "W111",
        "ts": "1583636382.000300",
        "team": "T111",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "d7eJ",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "user", "user_id": "U222"},
                            {"type": "text", "text": " test"},
                        ],
                    }
                ],
            }
        ],
    },
    "response_url": "https://hooks.slack.com/app/T111/111/xxx",
}
