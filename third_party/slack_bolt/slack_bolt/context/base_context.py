# pytype: skip-file
# Note: Since 2021.12.8, the pytype code analyzer does not properly work for this file

from logging import Logger
from typing import Optional, Tuple

from slack_bolt.authorization import AuthorizeResult


class BaseContext(dict):
    """Context object associated with a request from Slack."""

    standard_property_names = [
        "logger",
        "token",
        "enterprise_id",
        "is_enterprise_install",
        "team_id",
        "user_id",
        "actor_enterprise_id",
        "actor_team_id",
        "actor_user_id",
        "channel_id",
        "response_url",
        "matches",
        "authorize_result",
        "bot_token",
        "bot_id",
        "bot_user_id",
        "user_token",
        "client",
        "ack",
        "say",
        "respond",
    ]

    @property
    def logger(self) -> Logger:
        """The properly configured logger that is available for middleware/listeners."""
        return self["logger"]

    @property
    def token(self) -> Optional[str]:
        """The (bot/user) token resolved for this request."""
        return self.get("token")

    @property
    def enterprise_id(self) -> Optional[str]:
        """The Enterprise Grid Organization ID of this request."""
        return self.get("enterprise_id")

    @property
    def is_enterprise_install(self) -> Optional[bool]:
        """True if the request is associated with an Org-wide installation."""
        return self.get("is_enterprise_install")

    @property
    def team_id(self) -> Optional[str]:
        """The Workspace ID of this request."""
        return self.get("team_id")

    @property
    def user_id(self) -> Optional[str]:
        """The user ID associated ith this request."""
        return self.get("user_id")

    @property
    def actor_enterprise_id(self) -> Optional[str]:
        """The action's actor's Enterprise Grid organization ID.
        Note that this property is especially useful for handling events in Slack Connect channels.
        That being said, it's not guaranteed to have a valid ID for all events due to server-side inconsistency.
        """
        return self.get("actor_enterprise_id")

    @property
    def actor_team_id(self) -> Optional[str]:
        """The action's actor's workspace ID.
        Note that this property is especially useful for handling events in Slack Connect channels.
        That being said, it's not guaranteed to have a valid ID for all events due to server-side inconsistency.
        """
        return self.get("actor_team_id")

    @property
    def actor_user_id(self) -> Optional[str]:
        """The action's actor's user ID.
        Note that this property is especially useful for handling events in Slack Connect channels.
        That being said, it's not guaranteed to have a valid ID for all events due to server-side inconsistency.
        """
        return self.get("actor_user_id")

    @property
    def channel_id(self) -> Optional[str]:
        """The conversation ID associated with this request."""
        return self.get("channel_id")

    @property
    def response_url(self) -> Optional[str]:
        """The `response_url` associated with this request."""
        return self.get("response_url")

    @property
    def matches(self) -> Optional[Tuple]:
        """Returns all the matched parts in message listener's regexp"""
        return self.get("matches")

    # --------------------------------

    @property
    def authorize_result(self) -> Optional[AuthorizeResult]:
        """The authorize result resolved for this request."""
        return self.get("authorize_result")

    @property
    def bot_token(self) -> Optional[str]:
        """The bot token resolved for this request."""
        return self.get("bot_token")

    @property
    def bot_id(self) -> Optional[str]:
        """The bot ID resolved for this request."""
        return self.get("bot_id")

    @property
    def bot_user_id(self) -> Optional[str]:
        """The bot user ID resolved for this request."""
        return self.get("bot_user_id")

    @property
    def user_token(self) -> Optional[str]:
        """The user token resolved for this request."""
        return self.get("user_token")

    def set_authorize_result(self, authorize_result: AuthorizeResult):
        self["authorize_result"] = authorize_result
        if authorize_result.bot_id is not None:
            self["bot_id"] = authorize_result.bot_id
        if authorize_result.bot_user_id is not None:
            self["bot_user_id"] = authorize_result.bot_user_id
        if authorize_result.bot_token is not None:
            self["bot_token"] = authorize_result.bot_token
        if authorize_result.user_id is not None:
            self["user_id"] = authorize_result.user_id
        if authorize_result.user_token is not None:
            self["user_token"] = authorize_result.user_token
