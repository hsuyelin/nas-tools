import pytest

from slack_bolt.request.internals import (
    extract_channel_id,
    extract_user_id,
    extract_team_id,
    extract_enterprise_id,
    parse_query,
    extract_is_enterprise_install,
    extract_actor_enterprise_id,
    extract_actor_team_id,
    extract_actor_user_id,
)


class TestRequestInternals:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    # based on https://github.com/slackapi/bolt-js/blob/f8c25ffb5cd91827510bbc689e97556d2d5ad017/src/App.spec.ts#L1123
    requests = [
        {
            "event": {"channel": "C111", "user": "U111"},
            "team_id": "T111",
            "enterprise_id": "E111",
        },
        {
            "event": {"item": {"channel": "C111"}, "user": "U111", "item_user": "U222"},
            "team_id": "T111",
            "enterprise_id": "E111",
        },
        {
            "command": "/hello",
            "channel_id": "C111",
            "team_id": "T111",
            "enterprise_id": "E111",
            "user_id": "U111",
        },
        {
            "actions": [{}],
            "channel": {"id": "C111"},
            "user": {"id": "U111"},
            "team": {"id": "T111", "enterprise_id": "E111"},
        },
        {
            "type": "dialog_submission",
            "channel": {"id": "C111"},
            "user": {"id": "U111"},
            "team": {"id": "T111", "enterprise_id": "E111"},
        },
    ]

    enterprise_no_channel_requests = [
        {
            "type": "shortcut",
            "token": "xxx",
            "action_ts": "1606983924.521157",
            "team": {"id": "T111", "domain": "ddd"},
            "user": {"id": "U111", "username": "use", "team_id": "T111"},
            "is_enterprise_install": False,
            "enterprise": {"id": "E111", "domain": "eee"},
            "callback_id": "run-socket-mode",
            "trigger_id": "111.222.xxx",
        },
    ]

    no_enterprise_no_channel_requests = [
        {
            "type": "shortcut",
            "token": "xxx",
            "action_ts": "1606983924.521157",
            "team": {"id": "T111", "domain": "ddd"},
            "user": {"id": "U111", "username": "use", "team_id": "T111"},
            "is_enterprise_install": False,
            # This may be "null" in Socket Mode
            "enterprise": None,
            "callback_id": "run-socket-mode",
            "trigger_id": "111.222.xxx",
        },
    ]

    slack_connect_authorizations = [
        {
            "enterprise_id": "INSTALLED_ENTERPRISE_ID",
            "team_id": "INSTALLED_TEAM_ID",
            "user_id": "INSTALLED_BOT_USER_ID",
            "is_bot": True,
            "is_enterprise_install": False,
        }
    ]
    slack_connect_events_api_no_actor_team_requests = [
        {
            "team_id": "INSTALLED_TEAM_ID",
            "api_app_id": "A111",
            "event": {
                "type": "app_mention",
                "text": "<@INSTALLED_BOT_USER_ID> hey",
                "user": "USER_ID_ACTOR",
                "ts": "1678451405.023359",
                "team": "INSTALLED_TEAM_ID",
                "user_team": "ENTERPRISE_ID_ACTOR",
                "source_team": "ENTERPRISE_ID_ACTOR",
                "user_profile": {"team": "ENTERPRISE_ID_ACTOR"},
                "channel": "C111",
                "event_ts": "1678451405.023359",
            },
            "type": "event_callback",
            "authorizations": slack_connect_authorizations,
            "is_ext_shared_channel": True,
        },
    ]
    slack_connect_events_api_no_actor_enterprise_team_requests = [
        {
            "team_id": "INSTALLED_TEAM_ID",
            "context_team_id": "INSTALLED_TEAM_ID",
            "context_enterprise_id": "INSTALLED_ENTERPRISE_ID",
            "api_app_id": "A111",
            "event": {
                "type": "reaction_added",
                "user": "USER_ID_ACTOR",
                "reaction": "eyes",
                "item": {"type": "message", "channel": "C111", "ts": "1678453386.979699"},
                "event_ts": "1678456876.000900",
            },
            "type": "event_callback",
            "authorizations": slack_connect_authorizations,
            "is_ext_shared_channel": True,
        },
        {
            "enterprise_id": "INSTALLED_ENTERPRISE_ID",
            "team_id": "INSTALLED_TEAM_ID",
            "api_app_id": "A111",
            "event": {
                "file_id": "F111",
                "user_id": "USER_ID_ACTOR",
                "file": {"id": "F111"},
                "channel_id": "C111",
                "type": "file_shared",
                "event_ts": "1678454981.170300",
            },
            "type": "event_callback",
            "authorizations": slack_connect_authorizations,
            "is_ext_shared_channel": True,
        },
        {
            "team_id": "INSTALLED_TEAM_ID",
            "context_team_id": "INSTALLED_TEAM_ID",
            "context_enterprise_id": "INSTALLED_ENTERPRISE_ID",
            "api_app_id": "A111",
            "event": {
                "type": "reaction_added",
                "user": "USER_ID_ACTOR",
                "reaction": "rocket",
                "item": {"type": "message", "channel": "C111", "ts": "1678454602.316259"},
                "event_ts": "1678454724.000600",
            },
            "type": "event_callback",
            "authorizations": slack_connect_authorizations,
            "is_ext_shared_channel": True,
        },
        {
            "team_id": "TEAM_ID_ACTOR",
            "enterprise_id": "ENTERPRISE_ID_ACTOR",
            "context_team_id": "INSTALLED_TEAM_ID",
            "context_enterprise_id": "INSTALLED_ENTERPRISE_ID",
            "api_app_id": "A111",
            "event": {
                "type": "message_metadata_posted",
                "app_id": "A222",
                "bot_id": "B222",
                "user_id": "USER_ID_ACTOR",  # Although this is always a bot's user ID, we can call it an actor
                "team_id": "INSTALLED_TEAM_ID",
                "channel_id": "C111",
                "metadata": {"event_type": "task_created", "event_payload": {"id": "11223", "title": "Redesign Homepage"}},
                "message_ts": "1678458906.527119",
                "event_ts": "1678458906.527119",
            },
            "type": "event_callback",
            "authorizations": slack_connect_authorizations,
            "is_ext_shared_channel": True,
        },
    ]
    slack_connect_events_api_requests = [
        {
            "team_id": "TEAM_ID_ACTOR",
            "enterprise_id": "ENTERPRISE_ID_ACTOR",
            "context_team_id": "INSTALLED_TEAM_ID",
            "context_enterprise_id": "INSTALLED_ENTERPRISE_ID",
            "api_app_id": "A111",
            "event": {
                "type": "message",
                "text": "<@INSTALLED_BOT_USER_ID> Hey!",
                "user": "USER_ID_ACTOR",
                "ts": "1678455198.838499",
                "team": "TEAM_ID_ACTOR",
                "channel": "C111",
                "event_ts": "1678455198.838499",
                "channel_type": "channel",
            },
            "type": "event_callback",
            "authorizations": slack_connect_authorizations,
            "is_ext_shared_channel": True,
        },
        {
            "team_id": "TEAM_ID_ACTOR",
            "enterprise_id": "ENTERPRISE_ID_ACTOR",
            "context_team_id": "INSTALLED_TEAM_ID",
            "context_enterprise_id": "INSTALLED_ENTERPRISE_ID",
            "api_app_id": "A111",
            "event": {
                "type": "message",
                "text": "Hey!",
                "user": "USER_ID_ACTOR",
                "ts": "1678454365.204709",
                "team": "TEAM_ID_ACTOR",
                "channel": "C111",
                "event_ts": "1678454365.204709",
                "channel_type": "channel",
            },
            "type": "event_callback",
            "authorizations": slack_connect_authorizations,
            "is_ext_shared_channel": True,
        },
        {
            "team_id": "TEAM_ID_ACTOR",
            "enterprise_id": "ENTERPRISE_ID_ACTOR",
            "context_team_id": "INSTALLED_TEAM_ID",
            "context_enterprise_id": "INSTALLED_ENTERPRISE_ID",
            "api_app_id": "A111",
            "event": {
                "type": "message",
                "subtype": "channel_name",
                "ts": "1678454602.316259",
                "user": "USER_ID_ACTOR",
                "text": "renamed",
                "old_name": "old",
                "name": "new",
                "team": "TEAM_ID_ACTOR",
                "channel": "C111",
                "event_ts": "1678454602.316259",
                "channel_type": "channel",
            },
            "type": "event_callback",
            "authorizations": slack_connect_authorizations,
            "is_ext_shared_channel": True,
        },
    ]

    def test_channel_id_extraction(self):
        for req in self.requests:
            channel_id = extract_channel_id(req)
            assert channel_id == "C111"

    def test_user_id_extraction(self):
        for req in self.requests:
            user_id = extract_user_id(req)
            assert user_id == "U111"
        for req in self.enterprise_no_channel_requests:
            user_id = extract_user_id(req)
            assert user_id == "U111"
        for req in self.no_enterprise_no_channel_requests:
            user_id = extract_user_id(req)
            assert user_id == "U111"

    def test_team_id_extraction(self):
        for req in self.requests:
            team_id = extract_team_id(req)
            assert team_id == "T111"
        for req in self.enterprise_no_channel_requests:
            team_id = extract_team_id(req)
            assert team_id == "T111"
        for req in self.no_enterprise_no_channel_requests:
            team_id = extract_team_id(req)
            assert team_id == "T111"

    def test_enterprise_id_extraction(self):
        for req in self.requests:
            enterprise_id = extract_enterprise_id(req)
            assert enterprise_id == "E111"
        for req in self.enterprise_no_channel_requests:
            enterprise_id = extract_enterprise_id(req)
            assert enterprise_id == "E111"
        for req in self.no_enterprise_no_channel_requests:
            enterprise_id = extract_enterprise_id(req)
            assert enterprise_id is None

    def test_is_enterprise_install_extraction(self):
        for req in self.requests:
            should_be_false = extract_is_enterprise_install(req)
            assert should_be_false is False
        assert extract_is_enterprise_install({"is_enterprise_install": True}) is True
        assert extract_is_enterprise_install({"is_enterprise_install": False}) is False
        assert extract_is_enterprise_install({"is_enterprise_install": "true"}) is True
        assert extract_is_enterprise_install({"is_enterprise_install": "false"}) is False

    def test_actor_enterprise_id(self):
        for req in self.requests:
            enterprise_id = extract_actor_enterprise_id(req)
            assert enterprise_id == "E111"
        for req in self.slack_connect_events_api_requests:
            enterprise_id = extract_actor_enterprise_id(req)
            assert enterprise_id == "ENTERPRISE_ID_ACTOR"
        for req in self.slack_connect_events_api_no_actor_team_requests:
            enterprise_id = extract_actor_enterprise_id(req)
            assert enterprise_id == "ENTERPRISE_ID_ACTOR"
        for req in self.slack_connect_events_api_no_actor_enterprise_team_requests:
            enterprise_id = extract_actor_enterprise_id(req)
            assert enterprise_id is None

    def test_actor_team_id(self):
        for req in self.requests:
            team_id = extract_actor_team_id(req)
            assert team_id == "T111"
        for req in self.slack_connect_events_api_requests:
            team_id = extract_actor_team_id(req)
            assert team_id == "TEAM_ID_ACTOR"
        for req in self.slack_connect_events_api_no_actor_team_requests:
            team_id = extract_actor_team_id(req)
            assert team_id is None
        for req in self.slack_connect_events_api_no_actor_enterprise_team_requests:
            team_id = extract_actor_team_id(req)
            assert team_id is None

    def test_actor_user_id(self):
        for req in self.requests:
            user_id = extract_actor_user_id(req)
            assert user_id == "U111"
        for req in self.slack_connect_events_api_requests:
            user_id = extract_actor_user_id(req)
            assert user_id == "USER_ID_ACTOR"
        for req in self.slack_connect_events_api_no_actor_team_requests:
            user_id = extract_actor_user_id(req)
            assert user_id == "USER_ID_ACTOR"
        for req in self.slack_connect_events_api_no_actor_enterprise_team_requests:
            user_id = extract_actor_user_id(req)
            assert user_id is None

    def test_parse_query(self):
        expected = {"foo": ["bar"], "baz": ["123"]}

        q = parse_query("foo=bar&baz=123")
        assert q == expected

        q = parse_query({"foo": "bar", "baz": "123"})
        assert q == expected

        q = parse_query({"foo": ["bar"], "baz": ["123"]})
        assert q == expected

        with pytest.raises(ValueError):
            parse_query({"foo": {"bar": "ZZZ"}, "baz": {"123": "111"}})

    slack_connect_from_non_grid_test_patterns = [
        (
            {
                "team_id": "T03E94MJU",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "user": "U03E94MK0",
                    "team": "T03E94MJU",
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            # context.enterprise_id/team_id/user_id,
            (None, "T03E94MJU", "U03E94MK0"),
            # context.actor_enterprise_id/team_id/user_id,
            (None, "T03E94MJU", "U03E94MK0"),
        ),
        (
            {
                "team_id": "T03E94MJU",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "user": "U03E94MK0",
                    "team": "T03E94MJU",
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "U03E94MK0"),
            (None, "T03E94MJU", "U03E94MK0"),
        ),
        (
            {
                "team_id": "T03E94MJU",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "app_mention",
                    "text": "<@U04T5KKKLUE>",
                    "user": "U03E94MK0",
                    "team": "T03E94MJU",
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "U03E94MK0"),
            (None, "T03E94MJU", "U03E94MK0"),
        ),
        (
            {
                "team_id": "T03E94MJU",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "user": "U03E94MK0",
                    "team": "T03E94MJU",
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "U03E94MK0"),
            (None, "T03E94MJU", "U03E94MK0"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "app_mention",
                    "user": "U03E94MK0",
                    "team": "T014GJXU940",
                    "user_team": "T03E94MJU",
                    "source_team": "T03E94MJU",
                    "user_profile": {"team": "T03E94MJU"},
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "U03E94MK0"),
            (None, "T03E94MJU", "U03E94MK0"),
        ),
        (
            {
                "team_id": "T03E94MJU",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "subtype": "channel_join",
                    "user": "UL5CBM924",
                    "team": "T03E94MJU",
                    "inviter": "U03E94MK0",
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "UL5CBM924"),
            (None, "T03E94MJU", "UL5CBM924"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": "T03E94MJU",
                "context_enterprise_id": None,
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "member_joined_channel",
                    "user": "UL5CBM924",
                    "channel": "C04T3ACM40K",
                    "team": "T03E94MJU",
                    "inviter": "U03E94MK0",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "UL5CBM924"),
            (None, "T03E94MJU", "UL5CBM924"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": "T03E94MJU",
                "context_enterprise_id": None,
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "member_left_channel",
                    "user": "UL5CBM924",
                    "channel": "C04T3ACM40K",
                    "team": "T03E94MJU",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "UL5CBM924"),
            (None, "T03E94MJU", "UL5CBM924"),
        ),
        (
            {
                "team_id": "T03E94MJU",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "subtype": "channel_leave",
                    "user": "UL5CBM924",
                    "team": "T03E94MJU",
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "UL5CBM924"),
            (None, "T03E94MJU", "UL5CBM924"),
        ),
        (
            {
                "team_id": "T03E94MJU",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "files": [],
                    "upload": False,
                    "user": "U03E94MK0",
                    "display_as_bot": False,
                    "team": "T03E94MJU",
                    "channel": "C04T3ACM40K",
                    "subtype": "file_share",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "U03E94MK0"),
            (None, "T03E94MJU", "U03E94MK0"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "file_id": "F04TL3HA3PC",
                    "user_id": "U03E94MK0",
                    "file": {"id": "F04TL3HA3PC"},
                    "channel_id": "C04T3ACM40K",
                    "type": "file_shared",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "U03E94MK0"),
            # Note that a complete set of actor IDs are not deterministic in this scenario
            # So, we fall back to all None data for clarity
            (None, None, None),
        ),
        (
            {
                "team_id": "T03E94MJU",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "file_id": "F04TL3HA3PC",
                    "user_id": "U03E94MK0",
                    "file": {"id": "F04TL3HA3PC"},
                    "type": "file_public",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": False,
            },
            (None, "T03E94MJU", "U03E94MK0"),
            (None, "T03E94MJU", "U03E94MK0"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message_metadata_posted",
                    "app_id": "A013TFN1T7C",
                    "bot_id": "B013ZM43W3E",
                    "user_id": "W013TN008CB",
                    "team_id": "T014GJXU940",
                    "channel_id": "C04T3ACM40K",
                    "metadata": {
                        "event_type": "task_created",
                        "event_payload": {"id": "11223", "title": "Redesign Homepage"},
                    },
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "W013TN008CB"),
            # Note that a complete set of actor IDs are not deterministic in this scenario
            # So, we fall back to all None data for clarity
            (None, None, None),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "bot_id": "B013ZM43W3E",
                    "type": "message",
                    "user": "W013TN008CB",
                    "metadata": {
                        "event_type": "task_created",
                        "event_payload": {"id": "11223", "title": "Redesign Homepage"},
                    },
                    "app_id": "A013TFN1T7C",
                    "team": "T014GJXU940",
                    "bot_profile": {
                        "id": "B013ZM43W3E",
                        "app_id": "A013TFN1T7C",
                        "team_id": "T014GJXU940",
                    },
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "W013TN008CB"),
            ("E013Y3SHLAY", "T014GJXU940", "W013TN008CB"),
        ),
    ]

    slack_connect_from_grid_test_patterns = [
        (
            {
                "team_id": "T03E94MJU",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "app_mention",
                    "user": "W013QGS7BPF",
                    "team": "T03E94MJU",
                    "user_team": "E013Y3SHLAY",
                    "source_team": "E013Y3SHLAY",
                    "user_profile": {
                        "team": "E013Y3SHLAY",
                    },
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            # context.enterprise_id/team_id/user_id,
            (None, "T03E94MJU", "W013QGS7BPF"),
            # context.actor_enterprise_id/team_id/user_id,
            ("E013Y3SHLAY", None, "W013QGS7BPF"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "user": "W013QGS7BPF",
                    "team": "T014GJXU940",
                    "channel": "C04T3ACM40K",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "W013QGS7BPF"),
            ("E013Y3SHLAY", "T014GJXU940", "W013QGS7BPF"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "file_id": "F04TDEYDCT0",
                    "user_id": "W013QGS7BPF",
                    "file": {"id": "F04TDEYDCT0"},
                    "channel_id": "C04T3ACM40K",
                    "type": "file_shared",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "W013QGS7BPF"),
            (None, None, None),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "message",
                    "files": [],
                    "upload": False,
                    "user": "W013QGS7BPF",
                    "display_as_bot": False,
                    "team": "T014GJXU940",
                    "channel": "C04T3ACM40K",
                    "subtype": "file_share",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "W013QGS7BPF"),
            ("E013Y3SHLAY", "T014GJXU940", "W013QGS7BPF"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "file_id": "F04TDEYDCT0",
                    "user_id": "W013QGS7BPF",
                    "file": {"id": "F04TDEYDCT0"},
                    "type": "file_public",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": "E013Y3SHLAY",
                        "team_id": "T014GJXU940",
                        "user_id": "U04TDAM3YUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": False,
            },
            ("E013Y3SHLAY", "T014GJXU940", "W013QGS7BPF"),
            ("E013Y3SHLAY", "T014GJXU940", "W013QGS7BPF"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "member_joined_channel",
                    "user": "W013CV5UA87",
                    "channel": "C04T3ACM40K",
                    "team": "T014GJXU940",
                    "inviter": "W013QGS7BPF",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "W013CV5UA87"),
            ("E013Y3SHLAY", "T014GJXU940", "W013CV5UA87"),
        ),
        (
            {
                "team_id": "T014GJXU940",
                "enterprise_id": "E013Y3SHLAY",
                "context_team_id": "T014GJXU940",
                "context_enterprise_id": "E013Y3SHLAY",
                "api_app_id": "A04TEM7H4S0",
                "event": {
                    "type": "member_left_channel",
                    "user": "W013CV5UA87",
                    "channel": "C04T3ACM40K",
                    "team": "E013Y3SHLAY",
                },
                "type": "event_callback",
                "authorizations": [
                    {
                        "enterprise_id": None,
                        "team_id": "T03E94MJU",
                        "user_id": "U04T5KKKLUE",
                        "is_bot": True,
                        "is_enterprise_install": False,
                    }
                ],
                "is_ext_shared_channel": True,
            },
            (None, "T03E94MJU", "W013CV5UA87"),
            ("E013Y3SHLAY", "T014GJXU940", "W013CV5UA87"),
        ),
    ]

    def test_slack_connect_patterns(self):
        for (
            request,
            (enterprise_id, team_id, user_id),
            (actor_enterprise_id, actor_team_id, actor_user_id),
        ) in self.slack_connect_from_non_grid_test_patterns:
            assert extract_enterprise_id(request) == enterprise_id
            assert extract_team_id(request) == team_id
            assert extract_user_id(request) == user_id
            assert extract_actor_enterprise_id(request) == actor_enterprise_id
            assert extract_actor_team_id(request) == actor_team_id
            assert extract_actor_user_id(request) == actor_user_id

        for (
            request,
            (enterprise_id, team_id, user_id),
            (actor_enterprise_id, actor_team_id, actor_user_id),
        ) in self.slack_connect_from_grid_test_patterns:
            assert extract_enterprise_id(request) == enterprise_id
            assert extract_team_id(request) == team_id
            assert extract_user_id(request) == user_id
            assert extract_actor_enterprise_id(request) == actor_enterprise_id
            assert extract_actor_team_id(request) == actor_team_id
            assert extract_actor_user_id(request) == actor_user_id
