from typing import Optional, List, Union

from slack_sdk.web import SlackResponse


class AuthorizeResult(dict):
    """Authorize function call result"""

    enterprise_id: Optional[str]
    team_id: Optional[str]
    bot_id: Optional[str]
    bot_user_id: Optional[str]
    bot_token: Optional[str]
    bot_scopes: Optional[List[str]]  # since v1.17
    user_id: Optional[str]
    user_token: Optional[str]
    user_scopes: Optional[List[str]]  # since v1.17

    def __init__(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        # bot
        bot_user_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        bot_token: Optional[str] = None,
        bot_scopes: Optional[Union[List[str], str]] = None,
        # user
        user_id: Optional[str] = None,
        user_token: Optional[str] = None,
        user_scopes: Optional[Union[List[str], str]] = None,
    ):
        """
        Args:
            enterprise_id: Organization ID (Enterprise Grid) starting with `E`
            team_id: Workspace ID starting with `T`
            bot_user_id: Bot user's User ID starting with either `U` or `W`
            bot_id: Bot ID starting with `B`
            bot_token: Bot user access token starting with `xoxb-`
            bot_scopes: The scopes associated with the bot token
            user_id: The request user ID
            user_token: User access token starting with `xoxp-`
            user_scopes: The scopes associated wth the user token
        """
        self["enterprise_id"] = self.enterprise_id = enterprise_id
        self["team_id"] = self.team_id = team_id
        # bot
        self["bot_user_id"] = self.bot_user_id = bot_user_id
        self["bot_id"] = self.bot_id = bot_id
        self["bot_token"] = self.bot_token = bot_token
        if bot_scopes is not None and isinstance(bot_scopes, str):
            bot_scopes = [scope.strip() for scope in bot_scopes.split(",")]
        self["bot_scopes"] = self.bot_scopes = bot_scopes  # type: ignore
        # user
        self["user_id"] = self.user_id = user_id
        self["user_token"] = self.user_token = user_token
        if user_scopes is not None and isinstance(user_scopes, str):
            user_scopes = [scope.strip() for scope in user_scopes.split(",")]
        self["user_scopes"] = self.user_scopes = user_scopes  # type: ignore

    @classmethod
    def from_auth_test_response(
        cls,
        *,
        bot_token: Optional[str] = None,
        user_token: Optional[str] = None,
        bot_scopes: Optional[Union[List[str], str]] = None,
        user_scopes: Optional[Union[List[str], str]] = None,
        auth_test_response: SlackResponse,
        user_auth_test_response: Optional[SlackResponse] = None,
    ) -> "AuthorizeResult":
        bot_user_id: Optional[str] = (  # type:ignore
            auth_test_response.get("user_id") if auth_test_response.get("bot_id") is not None else None
        )
        user_id: Optional[str] = (  # type:ignore
            auth_test_response.get("user_id") if auth_test_response.get("bot_id") is None else None
        )
        # Since v1.28, user_id can be set when user_token w/ its auth.test response exists
        if user_id is None and user_auth_test_response is not None:
            user_id: Optional[str] = user_auth_test_response.get("user_id")  # type:ignore

        return AuthorizeResult(
            enterprise_id=auth_test_response.get("enterprise_id"),
            team_id=auth_test_response.get("team_id"),
            bot_id=auth_test_response.get("bot_id"),
            bot_user_id=bot_user_id,
            bot_scopes=bot_scopes,
            user_id=user_id,
            bot_token=bot_token,
            user_token=user_token,
            user_scopes=user_scopes,
        )
