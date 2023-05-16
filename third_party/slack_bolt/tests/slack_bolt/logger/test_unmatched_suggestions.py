from slack_bolt.request import BoltRequest
from slack_bolt.logger.messages import warning_unhandled_request


class TestUnmatchedPatternSuggestions:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_unknown_patterns(self):
        req: BoltRequest = BoltRequest(body={"type": "foo"}, mode="socket_mode")
        message = warning_unhandled_request(req)
        assert f"Unhandled request ({req.body})" == message

    def test_block_actions(self):
        req: BoltRequest = BoltRequest(body=block_actions, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "block_actions",
            "block_id": "b",
            "action_id": "action-id-value",
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.action("action-id-value")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)
"""
            == message
        )

    def test_attachment_actions(self):
        req: BoltRequest = BoltRequest(body=attachment_actions, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "interactive_message",
            "callback_id": "pick_channel_for_fun",
            "actions": [
                {
                    "name": "channel_list",
                    "type": "select",
                    "selected_options": [{"value": "C111"}],
                }
            ],
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.action("pick_channel_for_fun")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)
"""
            == message
        )

    def test_app_mention_event(self):
        req: BoltRequest = BoltRequest(body=app_mention_event, mode="socket_mode")
        filtered_body = {
            "type": "event_callback",
            "event": {"type": "app_mention"},
        }
        message = warning_unhandled_request(req)
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.event("app_mention")
def handle_app_mention_events(body, logger):
    logger.info(body)
"""
            == message
        )

    def test_commands(self):
        req: BoltRequest = BoltRequest(body=slash_command, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": None,
            "command": "/start-conv",
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.command("/start-conv")
def handle_some_command(ack, body, logger):
    ack()
    logger.info(body)
"""
            == message
        )

    def test_shortcut(self):
        req: BoltRequest = BoltRequest(body=global_shortcut, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "shortcut",
            "callback_id": "test-shortcut",
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.shortcut("test-shortcut")
def handle_shortcuts(ack, body, logger):
    ack()
    logger.info(body)
"""
            == message
        )

        req: BoltRequest = BoltRequest(body=message_shortcut, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "message_action",
            "callback_id": "test-shortcut",
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.shortcut("test-shortcut")
def handle_shortcuts(ack, body, logger):
    ack()
    logger.info(body)
"""
            == message
        )

    def test_view(self):
        req: BoltRequest = BoltRequest(body=view_submission, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "view_submission",
            "view": {"type": "modal", "callback_id": "view-id"},
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.view("view-id")
def handle_view_submission_events(ack, body, logger):
    ack()
    logger.info(body)
"""
            == message
        )

        req: BoltRequest = BoltRequest(body=view_closed, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "view_closed",
            "view": {"type": "modal", "callback_id": "view-id"},
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.view_closed("view-id")
def handle_view_closed_events(ack, body, logger):
    ack()
    logger.info(body)
"""
            == message
        )

    def test_block_suggestion(self):
        req: BoltRequest = BoltRequest(body=block_suggestion, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "block_suggestion",
            "view": {"type": "modal", "callback_id": "view-id"},
            "block_id": "block-id",
            "action_id": "the-id",
            "value": "search word",
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.options("the-id")
def handle_some_options(ack):
    ack(options=[ ... ])
"""
            == message
        )

    def test_dialog_suggestion(self):
        req: BoltRequest = BoltRequest(body=dialog_suggestion, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "dialog_suggestion",
            "callback_id": "the-id",
            "value": "search keyword",
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

@app.options({{"type": "dialog_suggestion", "callback_id": "the-id"}})
def handle_some_options(ack):
    ack(options=[ ... ])
"""
            == message
        )

    def test_step(self):
        req: BoltRequest = BoltRequest(body=step_edit_payload, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "workflow_step_edit",
            "callback_id": "copy_review",
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

from slack_bolt.workflows.step import WorkflowStep
ws = WorkflowStep(
    callback_id="copy_review",
    edit=edit,
    save=save,
    execute=execute,
)
# Pass Step to set up listeners
app.step(ws)
"""
            == message
        )
        req: BoltRequest = BoltRequest(body=step_save_payload, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "view_submission",
            "view": {"type": "workflow_step", "callback_id": "copy_review"},
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

from slack_bolt.workflows.step import WorkflowStep
ws = WorkflowStep(
    callback_id="copy_review",
    edit=edit,
    save=save,
    execute=execute,
)
# Pass Step to set up listeners
app.step(ws)
"""
            == message
        )
        req: BoltRequest = BoltRequest(body=step_execute_payload, mode="socket_mode")
        message = warning_unhandled_request(req)
        filtered_body = {
            "type": "event_callback",
            "event": {"type": "workflow_step_execute"},
        }
        assert (
            f"""Unhandled request ({filtered_body})
---
[Suggestion] You can handle this type of event with the following listener function:

from slack_bolt.workflows.step import WorkflowStep
ws = WorkflowStep(
    callback_id="your-callback-id",
    edit=edit,
    save=save,
    execute=execute,
)
# Pass Step to set up listeners
app.step(ws)
"""
            == message
        )


block_actions = {
    "type": "block_actions",
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "api_app_id": "A111",
    "token": "verification_token",
    "container": {
        "type": "message",
        "message_ts": "111.222",
        "channel_id": "C111",
        "is_ephemeral": True,
    },
    "trigger_id": "111.222.valid",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "channel": {"id": "C111", "name": "test-channel"},
    "response_url": "https://hooks.slack.com/actions/T111/111/random-value",
    "actions": [
        {
            "action_id": "action-id-value",
            "block_id": "b",
            "text": {"type": "plain_text", "text": "Button", "emoji": True},
            "value": "click_me_123",
            "type": "button",
            "action_ts": "1596530385.194939",
        }
    ],
}

attachment_actions = {
    "type": "interactive_message",
    "actions": [
        {
            "name": "channel_list",
            "type": "select",
            "selected_options": [{"value": "C111"}],
        }
    ],
    "callback_id": "pick_channel_for_fun",
    "team": {"id": "T111", "domain": "hooli-hq"},
    "channel": {"id": "C222", "name": "triage-random"},
    "user": {"id": "U111", "name": "gbelson"},
    "action_ts": "1520966872.245369",
    "message_ts": "1520965348.000538",
    "attachment_id": "1",
    "token": "verification_token",
    "is_app_unfurl": True,
    "original_message": {
        "text": "",
        "username": "Belson Bot",
        "bot_id": "B111",
        "attachments": [
            {
                "callback_id": "pick_channel_for_fun",
                "text": "Choose a channel",
                "id": 1,
                "color": "2b72cb",
                "actions": [
                    {
                        "id": "1",
                        "name": "channel_list",
                        "text": "Public channels",
                        "type": "select",
                        "data_source": "channels",
                    }
                ],
                "fallback": "Choose a channel",
            }
        ],
        "type": "message",
        "subtype": "bot_message",
        "ts": "1520965348.000538",
    },
    "response_url": "https://hooks.slack.com/actions/T111/111/xxxx",
    "trigger_id": "111.222.valid",
}


app_mention_event = {
    "token": "verification_token",
    "team_id": "T111",
    "enterprise_id": "E111",
    "api_app_id": "A111",
    "event": {
        "client_msg_id": "9cbd4c5b-7ddf-4ede-b479-ad21fca66d63",
        "type": "app_mention",
        "text": "<@W111> Hi there!",
        "user": "W222",
        "ts": "1595926230.009600",
        "team": "T111",
        "channel": "C111",
        "event_ts": "1595926230.009600",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1595926230,
}

slash_command = {
    "token": "fixed-verification-token",
    "team_id": "T111",
    "team_domain": "maria",
    "channel_id": "C111",
    "channel_name": "general",
    "user_id": "U111",
    "user_name": "rainer",
    "command": "/start-conv",
    "text": "title",
    "response_url": "https://xxx.slack.com/commands/T111/xxx/zzz",
    "trigger_id": "111.222.xxx",
}

step_edit_payload = {
    "type": "workflow_step_edit",
    "token": "verification-token",
    "action_ts": "1601541356.268786",
    "team": {
        "id": "T111",
        "domain": "subdomain",
        "enterprise_id": "E111",
        "enterprise_name": "Org Name",
    },
    "user": {"id": "W111", "username": "primary-owner", "team_id": "T111"},
    "callback_id": "copy_review",
    "trigger_id": "111.222.xxx",
    "workflow_step": {
        "workflow_id": "12345",
        "step_id": "111-222-333-444-555",
        "inputs": {
            "taskAuthorEmail": {"value": "seratch@example.com"},
            "taskDescription": {"value": "This is the task for you!"},
            "taskName": {"value": "The important task"},
        },
        "outputs": [
            {"name": "taskName", "type": "text", "label": "Task Name"},
            {"name": "taskDescription", "type": "text", "label": "Task Description"},
            {"name": "taskAuthorEmail", "type": "text", "label": "Task Author Email"},
        ],
    },
}

step_save_payload = {
    "type": "view_submission",
    "team": {
        "id": "T111",
        "domain": "subdomain",
        "enterprise_id": "E111",
        "enterprise_name": "Org Name",
    },
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "api_app_id": "A111",
    "token": "verification-token",
    "trigger_id": "111.222.xxx",
    "view": {
        "id": "V111",
        "team_id": "T111",
        "type": "workflow_step",
        "blocks": [
            {
                "type": "section",
                "block_id": "intro-section",
                "text": {
                    "type": "plain_text",
                    "text": "Create a task in one of the listed projects. The link to the task and other details will be available as variable data in later steps.",
                },
            },
            {
                "type": "input",
                "block_id": "task_name_input",
                "label": {"type": "plain_text", "text": "Task name"},
                "optional": False,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "task_name",
                    "placeholder": {"type": "plain_text", "text": "Write a task name"},
                },
            },
            {
                "type": "input",
                "block_id": "task_description_input",
                "label": {"type": "plain_text", "text": "Task description"},
                "optional": False,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "task_description",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Write a description for your task",
                    },
                },
            },
            {
                "type": "input",
                "block_id": "task_author_input",
                "label": {"type": "plain_text", "text": "Task author"},
                "optional": False,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "task_author",
                    "placeholder": {"type": "plain_text", "text": "Write a task name"},
                },
            },
        ],
        "private_metadata": "",
        "callback_id": "copy_review",
        "state": {
            "values": {
                "task_name_input": {
                    "task_name": {
                        "type": "plain_text_input",
                        "value": "The important task",
                    }
                },
                "task_description_input": {
                    "task_description": {
                        "type": "plain_text_input",
                        "value": "This is the task for you!",
                    }
                },
                "task_author_input": {
                    "task_author": {
                        "type": "plain_text_input",
                        "value": "seratch@example.com",
                    }
                },
            }
        },
        "hash": "111.zzz",
        "submit_disabled": False,
        "app_id": "A111",
        "external_id": "",
        "app_installed_team_id": "T111",
        "bot_id": "B111",
    },
    "response_urls": [],
    "workflow_step": {
        "workflow_step_edit_id": "111.222.zzz",
        "workflow_id": "12345",
        "step_id": "111-222-333-444-555",
    },
}

step_execute_payload = {
    "token": "verification-token",
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
            "inputs": {
                "taskAuthorEmail": {"value": "ksera@slack-corp.com"},
                "taskDescription": {"value": "sdfsdf"},
                "taskName": {"value": "a"},
            },
            "outputs": [
                {"name": "taskName", "type": "text", "label": "Task Name"},
                {
                    "name": "taskDescription",
                    "type": "text",
                    "label": "Task Description",
                },
                {
                    "name": "taskAuthorEmail",
                    "type": "text",
                    "label": "Task Author Email",
                },
            ],
        },
        "event_ts": "1601541373.225894",
    },
    "type": "event_callback",
    "event_id": "Ev111",
    "event_time": 1601541373,
}

global_shortcut = {
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

message_shortcut = {
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

view_submission = {
    "type": "view_submission",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "api_app_id": "A111",
    "token": "verification_token",
    "trigger_id": "111.222.valid",
    "view": {
        "id": "V111",
        "team_id": "T111",
        "type": "modal",
        "blocks": [
            {
                "type": "input",
                "block_id": "hspI",
                "label": {
                    "type": "plain_text",
                    "text": "Label",
                },
                "optional": False,
                "element": {"type": "plain_text_input", "action_id": "maBWU"},
            }
        ],
        "private_metadata": "This is for you!",
        "callback_id": "view-id",
        "state": {"values": {"hspI": {"maBWU": {"type": "plain_text_input", "value": "test"}}}},
        "hash": "1596530361.3wRYuk3R",
        "title": {
            "type": "plain_text",
            "text": "My App",
        },
        "clear_on_close": False,
        "notify_on_close": False,
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
        "previous_view_id": None,
        "root_view_id": "V111",
        "app_id": "A111",
        "external_id": "",
        "app_installed_team_id": "T111",
        "bot_id": "B111",
    },
    "response_urls": [],
}

view_closed = {
    "type": "view_closed",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "api_app_id": "A111",
    "token": "verification_token",
    "view": {
        "id": "V111",
        "team_id": "T111",
        "type": "modal",
        "blocks": [
            {
                "type": "input",
                "block_id": "hspI",
                "label": {
                    "type": "plain_text",
                    "text": "Label",
                },
                "optional": False,
                "element": {"type": "plain_text_input", "action_id": "maBWU"},
            }
        ],
        "private_metadata": "This is for you!",
        "callback_id": "view-id",
        "state": {"values": {}},
        "hash": "1596530361.3wRYuk3R",
        "title": {
            "type": "plain_text",
            "text": "My App",
        },
        "clear_on_close": False,
        "notify_on_close": False,
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
        "previous_view_id": None,
        "root_view_id": "V111",
        "app_id": "A111",
        "external_id": "",
        "app_installed_team_id": "T111",
        "bot_id": "B111",
    },
    "response_urls": [],
}

block_suggestion = {
    "type": "block_suggestion",
    "user": {
        "id": "W111",
        "username": "primary-owner",
        "name": "primary-owner",
        "team_id": "T111",
    },
    "container": {"type": "view", "view_id": "V111"},
    "api_app_id": "A111",
    "token": "verification_token",
    "action_id": "the-id",
    "block_id": "block-id",
    "value": "search word",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "view": {
        "id": "V111",
        "team_id": "T111",
        "type": "modal",
        "blocks": [
            {
                "type": "input",
                "block_id": "5ar+",
                "label": {"type": "plain_text", "text": "Label"},
                "optional": False,
                "element": {"type": "plain_text_input", "action_id": "i5IpR"},
            },
            {
                "type": "input",
                "block_id": "es_b",
                "label": {"type": "plain_text", "text": "Search"},
                "optional": False,
                "element": {
                    "type": "external_select",
                    "action_id": "es_a",
                    "placeholder": {"type": "plain_text", "text": "Select an item"},
                },
            },
            {
                "type": "input",
                "block_id": "mes_b",
                "label": {"type": "plain_text", "text": "Search (multi)"},
                "optional": False,
                "element": {
                    "type": "multi_external_select",
                    "action_id": "mes_a",
                    "placeholder": {"type": "plain_text", "text": "Select an item"},
                },
            },
        ],
        "private_metadata": "",
        "callback_id": "view-id",
        "state": {"values": {}},
        "hash": "111.xxx",
        "title": {"type": "plain_text", "text": "My App"},
        "clear_on_close": False,
        "notify_on_close": False,
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "previous_view_id": None,
        "root_view_id": "V111",
        "app_id": "A111",
        "external_id": "",
        "app_installed_team_id": "T111",
        "bot_id": "B111",
    },
}

dialog_suggestion = {
    "type": "dialog_suggestion",
    "token": "verification_token",
    "action_ts": "1596603332.676855",
    "team": {
        "id": "T111",
        "domain": "workspace-domain",
        "enterprise_id": "E111",
        "enterprise_name": "Sandbox Org",
    },
    "user": {"id": "W111", "name": "primary-owner", "team_id": "T111"},
    "channel": {"id": "C111", "name": "test-channel"},
    "name": "types",
    "value": "search keyword",
    "callback_id": "the-id",
    "state": "Limo",
}
