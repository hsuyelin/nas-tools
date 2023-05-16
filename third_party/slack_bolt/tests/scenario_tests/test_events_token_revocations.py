import json
from time import time, sleep
from typing import Optional

import pytest as pytest
from slack_sdk.oauth import InstallationStore
from slack_sdk.oauth.installation_store import Installation
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient

from slack_bolt import App, BoltRequest
from slack_bolt.error import BoltError
from tests.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
    assert_auth_test_count,
)
from tests.utils import remove_os_env_temporarily, restore_os_env

valid_token = "xoxb-valid"


class MyInstallationStore(InstallationStore):
    def __init__(self):
        self.delete_bot_called = False
        self.delete_installation_called = False
        self.delete_all_called = False

    def delete_bot(self, *, enterprise_id: Optional[str], team_id: Optional[str]) -> None:
        self.delete_bot_called = True

    def delete_installation(
        self, *, enterprise_id: Optional[str], team_id: Optional[str], user_id: Optional[str] = None
    ) -> None:
        self.delete_installation_called = True

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False
    ) -> Optional[Installation]:
        assert enterprise_id == "E111"
        assert team_id is None
        return Installation(
            enterprise_id="E111",
            team_id=None,
            user_id=user_id,
            bot_token=valid_token,
            bot_id="B111",
        )

    def delete_all(self, *, enterprise_id: Optional[str], team_id: Optional[str]):
        super().delete_all(enterprise_id=enterprise_id, team_id=team_id)
        self.delete_all_called = True


class TestEventsTokenRevocations:
    signing_secret = "secret"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client: WebClient = WebClient(
        token=None,
        base_url=mock_api_server_base_url,
    )

    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.old_os_env)

    def generate_signature(self, body: str, timestamp: str):
        return self.signature_verifier.generate_signature(
            body=body,
            timestamp=timestamp,
        )

    def build_headers(self, timestamp: str, body: str):
        return {
            "content-type": ["application/json"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    def test_no_installation_store(self):
        self.web_client.token = valid_token
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
        )
        with pytest.raises(BoltError):
            app.default_tokens_revoked_event_listener()
        with pytest.raises(BoltError):
            app.default_app_uninstalled_event_listener()
        with pytest.raises(BoltError):
            app.enable_token_revocation_listeners()

    def test_tokens_revoked(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=MyInstallationStore(),
        )

        event_payload = {
            "token": "verification-token",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {
                "type": "tokens_revoked",
                "tokens": {"oauth": ["W111"], "bot": ["W222"]},
            },
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1606805974,
        }

        timestamp, body = str(int(time())), json.dumps(event_payload)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 404

        # Enable the built-in event listeners
        app.enable_token_revocation_listeners()
        response = app.dispatch(request)
        assert response.status == 200

        # auth.test API call must be skipped
        assert_auth_test_count(self, 0)
        sleep(1)  # wait a bit after auto ack()
        assert app.installation_store.delete_bot_called is True
        assert app.installation_store.delete_installation_called is True
        assert app.installation_store.delete_all_called is False

    def test_app_uninstalled(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret,
            installation_store=MyInstallationStore(),
        )

        event_payload = {
            "token": "verification-token",
            "enterprise_id": "E111",
            "api_app_id": "A111",
            "event": {"type": "app_uninstalled"},
            "type": "event_callback",
            "event_id": "Ev111",
            "event_time": 1606805974,
        }

        timestamp, body = str(int(time())), json.dumps(event_payload)
        request: BoltRequest = BoltRequest(body=body, headers=self.build_headers(timestamp, body))
        response = app.dispatch(request)
        assert response.status == 404

        # Enable the built-in event listeners
        app.enable_token_revocation_listeners()
        response = app.dispatch(request)
        assert response.status == 200
        # auth.test API call must be skipped
        assert_auth_test_count(self, 0)
        sleep(1)  # wait a bit after auto ack()
        assert app.installation_store.delete_bot_called is True
        assert app.installation_store.delete_installation_called is True
        assert app.installation_store.delete_all_called is True
