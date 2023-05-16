import datetime
import logging
from logging import Logger
from typing import Optional

import pytest
from slack_sdk import WebClient
from slack_sdk.oauth import InstallationStore
from slack_sdk.oauth.installation_store import Bot, Installation

from slack_bolt import BoltContext
from slack_bolt.authorization.authorize import InstallationStoreAuthorize, Authorize
from slack_bolt.error import BoltError
from tests.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
    assert_auth_test_count,
)


class TestAuthorize:
    mock_api_server_base_url = "http://localhost:8888"

    def setup_method(self):
        setup_mock_web_api_server(self)

    def teardown_method(self):
        cleanup_mock_web_api_server(self)

    def test_root_class(self):
        authorize = Authorize()
        with pytest.raises(NotImplementedError):
            authorize(
                context=BoltContext(),
                enterprise_id="E111",
                team_id="T111",
                user_id="U111",
            )

    def test_installation_store_legacy(self):
        installation_store = LegacyMemoryInstallationStore()
        authorize = InstallationStoreAuthorize(logger=installation_store.logger, installation_store=installation_store)
        assert authorize.find_installation_available is True
        context = BoltContext()
        context["client"] = WebClient(base_url=self.mock_api_server_base_url)
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert authorize.find_installation_available is False
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token is None
        assert_auth_test_count(self, 1)

        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token is None
        assert_auth_test_count(self, 2)

    def test_installation_store_cached_legacy(self):
        installation_store = LegacyMemoryInstallationStore()
        authorize = InstallationStoreAuthorize(
            logger=installation_store.logger,
            installation_store=installation_store,
            cache_enabled=True,
        )
        assert authorize.find_installation_available is True
        context = BoltContext()
        context["client"] = WebClient(base_url=self.mock_api_server_base_url)
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert authorize.find_installation_available is False
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token is None
        assert_auth_test_count(self, 1)

        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token is None
        assert_auth_test_count(self, 1)  # cached

    def test_installation_store_bot_only(self):
        installation_store = BotOnlyMemoryInstallationStore()
        authorize = InstallationStoreAuthorize(
            logger=installation_store.logger,
            installation_store=installation_store,
            bot_only=True,
        )
        assert authorize.find_installation_available is True
        assert authorize.bot_only is True
        context = BoltContext()
        context["client"] = WebClient(base_url=self.mock_api_server_base_url)
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert authorize.find_installation_available is True
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token is None
        assert_auth_test_count(self, 1)

        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token is None
        assert_auth_test_count(self, 2)

    def test_installation_store_cached_bot_only(self):
        installation_store = BotOnlyMemoryInstallationStore()
        authorize = InstallationStoreAuthorize(
            logger=installation_store.logger,
            installation_store=installation_store,
            cache_enabled=True,
            bot_only=True,
        )
        assert authorize.find_installation_available is True
        assert authorize.bot_only is True
        context = BoltContext()
        context["client"] = WebClient(base_url=self.mock_api_server_base_url)
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert authorize.find_installation_available is True
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token is None
        assert_auth_test_count(self, 1)

        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token is None
        assert_auth_test_count(self, 1)  # cached

    def test_installation_store(self):
        installation_store = MemoryInstallationStore()
        authorize = InstallationStoreAuthorize(logger=installation_store.logger, installation_store=installation_store)
        assert authorize.find_installation_available is True
        context = BoltContext()
        context["client"] = WebClient(base_url=self.mock_api_server_base_url)
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token == "xoxp-valid"
        assert_auth_test_count(self, 1)

        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token == "xoxp-valid"
        assert_auth_test_count(self, 2)

    def test_installation_store_cached(self):
        installation_store = MemoryInstallationStore()
        authorize = InstallationStoreAuthorize(
            logger=installation_store.logger,
            installation_store=installation_store,
            cache_enabled=True,
        )
        assert authorize.find_installation_available is True
        context = BoltContext()
        context["client"] = WebClient(base_url=self.mock_api_server_base_url)
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token == "xoxp-valid"
        assert_auth_test_count(self, 1)

        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W11111")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.user_token == "xoxp-valid"
        assert_auth_test_count(self, 1)  # cached

    def test_fetch_different_user_token(self):
        installation_store = ValidUserTokenInstallationStore()
        authorize = InstallationStoreAuthorize(logger=installation_store.logger, installation_store=installation_store)
        context = BoltContext()
        context["client"] = WebClient(base_url=self.mock_api_server_base_url)
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W222")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.bot_token == "xoxb-valid"
        assert result.user_token == "xoxp-valid"
        assert_auth_test_count(self, 1)

    def test_fetch_different_user_token_with_rotation(self):
        context = BoltContext()
        mock_client = WebClient(base_url=self.mock_api_server_base_url)
        context["client"] = mock_client

        installation_store = ValidUserTokenRotationInstallationStore()
        invalid_authorize = InstallationStoreAuthorize(
            logger=installation_store.logger, installation_store=installation_store
        )
        with pytest.raises(BoltError):
            invalid_authorize(
                context=context,
                enterprise_id="E111",
                team_id="T0G9PQBBK",
                user_id="W222",
            )

        authorize = InstallationStoreAuthorize(
            client_id="111.222",
            client_secret="secret",
            client=mock_client,
            logger=installation_store.logger,
            installation_store=installation_store,
        )
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W222")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.bot_token == "xoxb-valid-refreshed"
        assert result.user_token == "xoxp-valid-refreshed"
        assert_auth_test_count(self, 1)

    def test_remove_latest_user_token_if_it_is_not_relevant(self):
        installation_store = ValidUserTokenInstallationStore()
        authorize = InstallationStoreAuthorize(logger=installation_store.logger, installation_store=installation_store)
        context = BoltContext()
        context["client"] = WebClient(base_url=self.mock_api_server_base_url)
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W333")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.bot_token == "xoxb-valid"
        assert result.user_token is None
        assert_auth_test_count(self, 1)

    def test_rotate_only_bot_token(self):
        context = BoltContext()
        mock_client = WebClient(base_url=self.mock_api_server_base_url)
        context["client"] = mock_client

        installation_store = ValidUserTokenRotationInstallationStore()
        invalid_authorize = InstallationStoreAuthorize(
            logger=installation_store.logger, installation_store=installation_store
        )
        with pytest.raises(BoltError):
            invalid_authorize(
                context=context,
                enterprise_id="E111",
                team_id="T0G9PQBBK",
                user_id="W333",
            )

        authorize = InstallationStoreAuthorize(
            client_id="111.222",
            client_secret="secret",
            client=mock_client,
            logger=installation_store.logger,
            installation_store=installation_store,
        )
        result = authorize(context=context, enterprise_id="E111", team_id="T0G9PQBBK", user_id="W333")
        assert result.bot_id == "BZYBOTHED"
        assert result.bot_user_id == "W23456789"
        assert result.bot_token == "xoxb-valid-refreshed"
        assert result.user_token is None
        assert_auth_test_count(self, 1)


class LegacyMemoryInstallationStore(InstallationStore):
    @property
    def logger(self) -> Logger:
        return logging.getLogger(__name__)

    def save(self, installation: Installation):
        pass

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        return Bot(
            app_id="A111",
            enterprise_id="E111",
            team_id="T0G9PQBBK",
            bot_token="xoxb-valid-1",
            bot_id="B",
            bot_user_id="W",
            bot_scopes=["commands", "chat:write"],
            installed_at=datetime.datetime.now().timestamp(),
        )


class MemoryInstallationStore(LegacyMemoryInstallationStore):
    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        return Installation(
            app_id="A111",
            enterprise_id="E111",
            team_id="T0G9PQBBK",
            bot_token="xoxb-valid-2",
            bot_id="B",
            bot_user_id="W",
            bot_scopes=["commands", "chat:write"],
            user_id="W11111",
            user_token="xoxp-valid",
            user_scopes=["search:read"],
            installed_at=datetime.datetime.now().timestamp(),
        )


class BotOnlyMemoryInstallationStore(LegacyMemoryInstallationStore):
    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        raise ValueError


class ValidUserTokenInstallationStore(InstallationStore):
    @property
    def logger(self) -> Logger:
        return logging.getLogger(__name__)

    def save(self, installation: Installation):
        pass

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        if user_id is None:
            return Installation(
                app_id="A111",
                enterprise_id="E111",
                team_id="T0G9PQBBK",
                bot_token="xoxb-valid",
                bot_id="B",
                bot_user_id="W",
                bot_scopes=["commands", "chat:write"],
                user_id="W11111",
                user_token="xoxp-different-installer",
                user_scopes=["search:read"],
                installed_at=datetime.datetime.now().timestamp(),
            )
        elif user_id == "W222":
            return Installation(
                app_id="A111",
                enterprise_id="E111",
                team_id="T0G9PQBBK",
                user_id="W222",
                user_token="xoxp-valid",
                user_scopes=["search:read"],
                installed_at=datetime.datetime.now().timestamp(),
            )


class ValidUserTokenRotationInstallationStore(InstallationStore):
    @property
    def logger(self) -> Logger:
        return logging.getLogger(__name__)

    def save(self, installation: Installation):
        pass

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        if user_id is None:
            return Installation(
                app_id="A111",
                enterprise_id="E111",
                team_id="T0G9PQBBK",
                bot_token="xoxb-valid",
                bot_refresh_token="xoxe-bot-valid",
                bot_token_expires_in=-10,
                bot_id="B",
                bot_user_id="W",
                bot_scopes=["commands", "chat:write"],
                user_id="W11111",
                user_token="xoxp-different-installer",
                user_refresh_token="xoxe-1-user-valid",
                user_token_expires_in=-10,
                user_scopes=["search:read"],
                installed_at=datetime.datetime.now().timestamp(),
            )
        elif user_id == "W222":
            return Installation(
                app_id="A111",
                enterprise_id="E111",
                team_id="T0G9PQBBK",
                user_id="W222",
                user_token="xoxp-valid",
                user_refresh_token="xoxe-1-user-valid",
                user_token_expires_in=-10,
                user_scopes=["search:read"],
                installed_at=datetime.datetime.now().timestamp(),
            )
