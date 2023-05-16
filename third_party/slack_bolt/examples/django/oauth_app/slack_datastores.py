# ----------------------
# Bolt store implementations
# ----------------------

from logging import Logger
from typing import Optional
from uuid import uuid4
from django.db.models import F
from django.utils import timezone
from django.utils.timezone import is_naive, make_aware
from slack_sdk.oauth import InstallationStore, OAuthStateStore
from slack_sdk.oauth.installation_store import Bot, Installation

from .models import SlackBot, SlackInstallation, SlackOAuthState


class DjangoInstallationStore(InstallationStore):
    client_id: str

    def __init__(
        self,
        client_id: str,
        logger: Logger,
    ):
        self.client_id = client_id
        self._logger = logger

    @property
    def logger(self) -> Logger:
        return self._logger

    def save(self, installation: Installation):
        i = installation.to_dict()
        if is_naive(i["installed_at"]):
            i["installed_at"] = make_aware(i["installed_at"])
        if i.get("bot_token_expires_at") is not None and is_naive(i["bot_token_expires_at"]):
            i["bot_token_expires_at"] = make_aware(i["bot_token_expires_at"])
        if i.get("user_token_expires_at") is not None and is_naive(i["user_token_expires_at"]):
            i["user_token_expires_at"] = make_aware(i["user_token_expires_at"])
        i["client_id"] = self.client_id
        row_to_update = (
            SlackInstallation.objects.filter(client_id=self.client_id)
            .filter(enterprise_id=installation.enterprise_id)
            .filter(team_id=installation.team_id)
            .filter(installed_at=i["installed_at"])
            .first()
        )
        if row_to_update is not None:
            for key, value in i.items():
                setattr(row_to_update, key, value)
            row_to_update.save()
        else:
            SlackInstallation(**i).save()

        self.save_bot(installation.to_bot())

    def save_bot(self, bot: Bot):
        b = bot.to_dict()
        if is_naive(b["installed_at"]):
            b["installed_at"] = make_aware(b["installed_at"])
        if b.get("bot_token_expires_at") is not None and is_naive(b["bot_token_expires_at"]):
            b["bot_token_expires_at"] = make_aware(b["bot_token_expires_at"])
        b["client_id"] = self.client_id

        row_to_update = (
            SlackBot.objects.filter(client_id=self.client_id)
            .filter(enterprise_id=bot.enterprise_id)
            .filter(team_id=bot.team_id)
            .filter(installed_at=b["installed_at"])
            .first()
        )
        if row_to_update is not None:
            for key, value in b.items():
                setattr(row_to_update, key, value)
            row_to_update.save()
        else:
            SlackBot(**b).save()

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        e_id = enterprise_id or None
        t_id = team_id or None
        if is_enterprise_install:
            t_id = None
        rows = (
            SlackBot.objects.filter(client_id=self.client_id)
            .filter(enterprise_id=e_id)
            .filter(team_id=t_id)
            .order_by(F("installed_at").desc())[:1]
        )
        if len(rows) > 0:
            b = rows[0]
            return Bot(
                app_id=b.app_id,
                enterprise_id=b.enterprise_id,
                team_id=b.team_id,
                bot_token=b.bot_token,
                bot_refresh_token=b.bot_refresh_token,
                bot_token_expires_at=b.bot_token_expires_at,
                bot_id=b.bot_id,
                bot_user_id=b.bot_user_id,
                bot_scopes=b.bot_scopes,
                installed_at=b.installed_at,
            )
        return None

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        e_id = enterprise_id or None
        t_id = team_id or None
        if is_enterprise_install:
            t_id = None
        if user_id is None:
            rows = (
                SlackInstallation.objects.filter(client_id=self.client_id)
                .filter(enterprise_id=e_id)
                .filter(team_id=t_id)
                .order_by(F("installed_at").desc())[:1]
            )
        else:
            rows = (
                SlackInstallation.objects.filter(client_id=self.client_id)
                .filter(enterprise_id=e_id)
                .filter(team_id=t_id)
                .filter(user_id=user_id)
                .order_by(F("installed_at").desc())[:1]
            )

        if len(rows) > 0:
            i = rows[0]
            if user_id is not None:
                # Fetch the latest bot token
                latest_bot_rows = (
                    SlackInstallation.objects.filter(client_id=self.client_id)
                    .exclude(bot_token__isnull=True)
                    .filter(enterprise_id=e_id)
                    .filter(team_id=t_id)
                    .order_by(F("installed_at").desc())[:1]
                )
                if len(latest_bot_rows) > 0:
                    b = latest_bot_rows[0]
                    i.bot_id = b.bot_id
                    i.bot_user_id = b.bot_user_id
                    i.bot_scopes = b.bot_scopes
                    i.bot_token = b.bot_token
                    i.bot_refresh_token = b.bot_refresh_token
                    i.bot_token_expires_at = b.bot_token_expires_at

            return Installation(
                app_id=i.app_id,
                enterprise_id=i.enterprise_id,
                team_id=i.team_id,
                bot_token=i.bot_token,
                bot_refresh_token=i.bot_refresh_token,
                bot_token_expires_at=i.bot_token_expires_at,
                bot_id=i.bot_id,
                bot_user_id=i.bot_user_id,
                bot_scopes=i.bot_scopes,
                user_id=i.user_id,
                user_token=i.user_token,
                user_refresh_token=i.user_refresh_token,
                user_token_expires_at=i.user_token_expires_at,
                user_scopes=i.user_scopes,
                incoming_webhook_url=i.incoming_webhook_url,
                incoming_webhook_channel_id=i.incoming_webhook_channel_id,
                incoming_webhook_configuration_url=i.incoming_webhook_configuration_url,
                installed_at=i.installed_at,
            )
        return None


class DjangoOAuthStateStore(OAuthStateStore):
    expiration_seconds: int

    def __init__(
        self,
        expiration_seconds: int,
        logger: Logger,
    ):
        self.expiration_seconds = expiration_seconds
        self._logger = logger

    @property
    def logger(self) -> Logger:
        return self._logger

    def issue(self) -> str:
        state: str = str(uuid4())
        expire_at = timezone.now() + timezone.timedelta(seconds=self.expiration_seconds)
        row = SlackOAuthState(state=state, expire_at=expire_at)
        row.save()
        return state

    def consume(self, state: str) -> bool:
        rows = SlackOAuthState.objects.filter(state=state).filter(expire_at__gte=timezone.now())
        if len(rows) > 0:
            for row in rows:
                row.delete()
            return True
        return False
