#
# Please note that this is an example implementation.
# You can reuse this implementation for your app,
# but we don't have short-term plans to add this code to slack-sdk package.
# Please maintain the code on your own if you copy this file.
#
# Also, please refer to the following gist for more discussion and better implementation:
# https://gist.github.com/seratch/d81a445ef4467b16f047156bf859cda8
#

import logging
from logging import Logger
from typing import Optional
from uuid import uuid4

from google.cloud import datastore
from google.cloud.datastore import Client, Entity, Query
from slack_sdk.oauth import OAuthStateStore, InstallationStore
from slack_sdk.oauth.installation_store import Installation, Bot


class GoogleDatastoreInstallationStore(InstallationStore):
    datastore_client: Client

    def __init__(
        self,
        *,
        datastore_client: Client,
        logger: Logger,
    ):
        self.datastore_client = datastore_client
        self._logger = logger

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    def installation_key(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str],
        suffix: Optional[str] = None,
        is_enterprise_install: Optional[bool] = None,
    ):
        enterprise_id = enterprise_id or "none"
        team_id = "none" if is_enterprise_install else team_id or "none"
        name = f"{enterprise_id}-{team_id}-{user_id}" if user_id else f"{enterprise_id}-{team_id}"
        if suffix is not None:
            name += "-" + suffix
        return self.datastore_client.key("installations", name)

    def bot_key(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        suffix: Optional[str] = None,
        is_enterprise_install: Optional[bool] = None,
    ):
        enterprise_id = enterprise_id or "none"
        team_id = "none" if is_enterprise_install else team_id or "none"
        name = f"{enterprise_id}-{team_id}"
        if suffix is not None:
            name += "-" + suffix
        return self.datastore_client.key("bots", name)

    def save(self, i: Installation):
        # the latest installation in the workspace
        installation_entity: Entity = datastore.Entity(
            key=self.installation_key(
                enterprise_id=i.enterprise_id,
                team_id=i.team_id,
                user_id=None,  # user_id is removed
                is_enterprise_install=i.is_enterprise_install,
            )
        )
        installation_entity.update(**i.to_dict())
        self.datastore_client.put(installation_entity)

        # the latest installation associated with a user
        user_entity: Entity = datastore.Entity(
            key=self.installation_key(
                enterprise_id=i.enterprise_id,
                team_id=i.team_id,
                user_id=i.user_id,
                is_enterprise_install=i.is_enterprise_install,
            )
        )
        user_entity.update(**i.to_dict())
        self.datastore_client.put(user_entity)
        # history data
        user_entity.key = self.installation_key(
            enterprise_id=i.enterprise_id,
            team_id=i.team_id,
            user_id=i.user_id,
            is_enterprise_install=i.is_enterprise_install,
            suffix=str(i.installed_at),
        )
        self.datastore_client.put(user_entity)

        # the latest bot authorization in the workspace
        bot = i.to_bot()
        bot_entity: Entity = datastore.Entity(
            key=self.bot_key(
                enterprise_id=i.enterprise_id,
                team_id=i.team_id,
                is_enterprise_install=i.is_enterprise_install,
            )
        )
        bot_entity.update(**bot.to_dict())
        self.datastore_client.put(bot_entity)
        # history data
        bot_entity.key = self.bot_key(
            enterprise_id=i.enterprise_id,
            team_id=i.team_id,
            is_enterprise_install=i.is_enterprise_install,
            suffix=str(i.installed_at),
        )
        self.datastore_client.put(bot_entity)

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        entity: Entity = self.datastore_client.get(
            self.bot_key(
                enterprise_id=enterprise_id,
                team_id=team_id,
                is_enterprise_install=is_enterprise_install,
            )
        )
        if entity is not None:
            entity["installed_at"] = entity["installed_at"].timestamp()
            return Bot(**entity)
        return None

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        entity: Entity = self.datastore_client.get(
            self.installation_key(
                enterprise_id=enterprise_id,
                team_id=team_id,
                user_id=user_id,
                is_enterprise_install=is_enterprise_install,
            )
        )
        if entity is not None:
            entity["installed_at"] = entity["installed_at"].timestamp()
            return Installation(**entity)
        return None

    def delete_installation(
        self,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str],
    ) -> None:
        installation_key = self.installation_key(
            enterprise_id=enterprise_id,
            team_id=team_id,
            user_id=user_id,
        )
        q: Query = self.datastore_client.query()
        q.key_filter(installation_key, ">=")
        for entity in q.fetch():
            if entity.key.name.startswith(installation_key.name):
                self.datastore_client.delete(entity.key)
            else:
                break

    def delete_bot(
        self,
        enterprise_id: Optional[str],
        team_id: Optional[str],
    ) -> None:
        bot_key = self.bot_key(
            enterprise_id=enterprise_id,
            team_id=team_id,
        )
        q: Query = self.datastore_client.query()
        q.key_filter(bot_key, ">=")
        for entity in q.fetch():
            if entity.key.name.startswith(bot_key.name):
                self.datastore_client.delete(entity.key)
            else:
                break

    def delete_all(
        self,
        enterprise_id: Optional[str],
        team_id: Optional[str],
    ):
        self.delete_bot(enterprise_id=enterprise_id, team_id=team_id)
        self.delete_installation(enterprise_id=enterprise_id, team_id=team_id, user_id=None)


class GoogleDatastoreOAuthStateStore(OAuthStateStore):
    logger: Logger
    datastore_client: Client
    collection_id: str

    def __init__(
        self,
        *,
        datastore_client: Client,
        logger: Logger,
    ):
        self.datastore_client = datastore_client
        self._logger = logger
        self.collection_id = "oauth_state_values"

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    def consume(self, state: str) -> bool:
        key = self.datastore_client.key(self.collection_id, state)
        entity = self.datastore_client.get(key)
        if entity is not None:
            self.datastore_client.delete(key)
            return True
        return False

    def issue(self, *args, **kwargs) -> str:
        state_value = str(uuid4())
        entity: Entity = datastore.Entity(key=self.datastore_client.key(self.collection_id, state_value))
        entity.update(value=state_value)
        self.datastore_client.put(entity)
        return state_value
