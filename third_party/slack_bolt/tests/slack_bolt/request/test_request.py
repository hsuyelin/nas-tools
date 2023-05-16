from urllib.parse import quote

from slack_bolt.request.request import BoltRequest


class TestRequest:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_all_none_inputs_http(self):
        req = BoltRequest(body=None, headers=None, query=None, context=None)
        assert req is not None
        assert req.raw_body == ""
        assert req.body == {}

    def test_all_none_inputs_socket_mode(self):
        req = BoltRequest(body=None, headers=None, query=None, context=None, mode="socket_mode")
        assert req is not None
        assert req.raw_body == ""
        assert req.body == {}

    def test_org_wide_installations_block_actions(self):
        payload = """
{
  "type": "block_actions",
  "user": {
    "id": "W111",
    "username": "primary-owner",
    "name": "primary-owner",
    "team_id": "T_expected"
  },
  "api_app_id": "A111",
  "token": "fixed-value",
  "container": {
    "type": "message",
    "message_ts": "1643113871.000700",
    "channel_id": "C111",
    "is_ephemeral": true
  },
  "trigger_id": "111.222.xxx",
  "team": null,
  "enterprise": {
    "id": "E111",
    "name": "Sandbox Org"
  },
  "is_enterprise_install": true,
  "channel": {
    "id": "C111",
    "name": "random"
  },
  "state": {
    "values": {}
  },
  "response_url": "https://hooks.slack.com/actions/E111/111/xxx",
  "actions": [
    {
      "action_id": "a",
      "block_id": "b",
      "text": {
        "type": "plain_text",
        "text": "Button"
      },
      "value": "click_me_123",
      "type": "button",
      "action_ts": "1643113877.645417"
    }
  ]
}
"""
        req = BoltRequest(body=f"payload={quote(payload)}")
        assert req is not None
        assert req.context.team_id == "T_expected"
        assert req.context.user_id == "W111"

    def test_org_wide_installations_view_submission(self):
        payload = """
{
  "type": "view_submission",
  "team": null,
  "user": {
    "id": "W111",
    "username": "primary-owner",
    "name": "primary-owner",
    "team_id": "T_unexpected"
  },
  "api_app_id": "A111",
  "token": "fixed-value",
  "trigger_id": "1111.222.xxx",
  "view": {
    "id": "V111",
    "team_id": "T_unexpected",
    "type": "modal",
    "blocks": [
      {
        "type": "input",
        "block_id": "+5B",
        "label": {
          "type": "plain_text",
          "text": "Label",
          "emoji": true
        },
        "optional": false,
        "dispatch_action": false,
        "element": {
          "type": "plain_text_input",
          "dispatch_action_config": {
            "trigger_actions_on": [
              "on_enter_pressed"
            ]
          },
          "action_id": "MMKH"
        }
      }
    ],
    "private_metadata": "",
    "callback_id": "view-id",
    "state": {
      "values": {
        "+5B": {
          "MMKH": {
            "type": "plain_text_input",
            "value": "test"
          }
        }
      }
    },
    "hash": "111.xxx",
    "title": {
      "type": "plain_text",
      "text": "My App"
    },
    "clear_on_close": false,
    "notify_on_close": false,
    "close": {
      "type": "plain_text",
      "text": "Cancel"
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit",
      "emoji": true
    },
    "previous_view_id": null,
    "root_view_id": "V111",
    "app_id": "A111",
    "external_id": "",
    "app_installed_team_id": "T_expected",
    "bot_id": "B111"
  },
  "response_urls": [],
  "is_enterprise_install": true,
  "enterprise": {
    "id": "E111",
    "name": "Sandbox Org"
  }
}
"""
        req = BoltRequest(body=f"payload={quote(payload)}")
        assert req is not None
        assert req.context.team_id == "T_expected"
        assert req.context.user_id == "W111"

    def test_org_wide_installations_view_closed(self):
        payload = """
{
  "type": "view_closed",
  "team": null,
  "user": {
    "id": "W111",
    "username": "primary-owner",
    "name": "primary-owner",
    "team_id": "T_unexpected"
  },
  "api_app_id": "A111",
  "token": "fixed-value",
  "view": {
    "id": "V111",
    "team_id": "T_unexpected",
    "type": "modal",
    "blocks": [
      {
        "type": "input",
        "block_id": "M2r2p",
        "label": {
          "type": "plain_text",
          "text": "Label"
        },
        "optional": false,
        "dispatch_action": false,
        "element": {
          "type": "plain_text_input",
          "dispatch_action_config": {
            "trigger_actions_on": [
              "on_enter_pressed"
            ]
          },
          "action_id": "xB+"
        }
      }
    ],
    "private_metadata": "",
    "callback_id": "view-id",
    "state": {
      "values": {}
    },
    "hash": "1643113987.gRY6ROtt",
    "title": {
      "type": "plain_text",
      "text": "My App"
    },
    "clear_on_close": false,
    "notify_on_close": true,
    "close": {
      "type": "plain_text",
      "text": "Cancel"
    },
    "submit": {
      "type": "plain_text",
      "text": "Submit"
    },
    "previous_view_id": null,
    "root_view_id": "V111",
    "app_id": "A111",
    "external_id": "",
    "app_installed_team_id": "T_expected",
    "bot_id": "B0302M47727"
  },
  "is_cleared": false,
  "is_enterprise_install": true,
  "enterprise": {
    "id": "E111",
    "name": "Sandbox Org"
  }
}
"""
        req = BoltRequest(body=f"payload={quote(payload)}")
        assert req is not None
        assert req.context.team_id == "T_expected"
        assert req.context.user_id == "W111"
