import logging
import os
import time
from datetime import datetime
from logging import Logger
from typing import Optional
from uuid import uuid4

import sqlalchemy
from databases import Database
from slack_sdk.oauth.installation_store import Bot, Installation
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore
from slack_sdk.oauth.state_store.async_state_store import AsyncOAuthStateStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore
from sqlalchemy import and_, desc, Table, MetaData

from slack_bolt.adapter.sanic import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings


class AsyncSQLAlchemyInstallationStore(AsyncInstallationStore):
    database_url: str
    client_id: str
    metadata: MetaData
    installations: Table
    bots: Table

    def __init__(
        self,
        client_id: str,
        database_url: str,
        logger: Logger = logging.getLogger(__name__),
    ):
        self.client_id = client_id
        self.database_url = database_url
        self._logger = logger
        self.metadata = MetaData()
        self.installations = SQLAlchemyInstallationStore.build_installations_table(
            metadata=self.metadata,
            table_name=SQLAlchemyInstallationStore.default_installations_table_name,
        )
        self.bots = SQLAlchemyInstallationStore.build_bots_table(
            metadata=self.metadata,
            table_name=SQLAlchemyInstallationStore.default_bots_table_name,
        )

    @property
    def logger(self) -> Logger:
        return self._logger

    async def async_save(self, installation: Installation):
        async with Database(self.database_url) as database:
            async with database.transaction():
                i = installation.to_dict()
                i["client_id"] = self.client_id
                await database.execute(self.installations.insert(), i)
                b = installation.to_bot().to_dict()
                b["client_id"] = self.client_id
                await database.execute(self.bots.insert(), b)

    async def async_find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool],
    ) -> Optional[Bot]:
        c = self.bots.c
        query = (
            self.bots.select()
            .where(
                and_(
                    c.enterprise_id == enterprise_id,
                    c.team_id == team_id,
                    c.is_enterprise_install == is_enterprise_install,
                )
            )
            .order_by(desc(c.installed_at))
            .limit(1)
        )
        async with Database(self.database_url) as database:
            result = await database.fetch_one(query)
            if result:
                return Bot(
                    app_id=result["app_id"],
                    enterprise_id=result["enterprise_id"],
                    team_id=result["team_id"],
                    bot_token=result["bot_token"],
                    bot_id=result["bot_id"],
                    bot_user_id=result["bot_user_id"],
                    bot_scopes=result["bot_scopes"],
                    installed_at=result["installed_at"],
                )
            else:
                return None


class AsyncSQLAlchemyOAuthStateStore(AsyncOAuthStateStore):
    database_url: str
    expiration_seconds: int
    metadata: MetaData
    oauth_states: Table

    def __init__(
        self,
        *,
        expiration_seconds: int,
        database_url: str,
        logger: Logger = logging.getLogger(__name__),
    ):
        self.expiration_seconds = expiration_seconds
        self.database_url = database_url
        self._logger = logger
        self.metadata = MetaData()
        self.oauth_states = SQLAlchemyOAuthStateStore.build_oauth_states_table(
            metadata=self.metadata,
            table_name=SQLAlchemyOAuthStateStore.default_table_name,
        )

    @property
    def logger(self) -> Logger:
        return self._logger

    async def async_issue(self) -> str:
        state: str = str(uuid4())
        now = datetime.utcfromtimestamp(time.time() + self.expiration_seconds)
        async with Database(self.database_url) as database:
            await database.execute(self.oauth_states.insert(), {"state": state, "expire_at": now})
            return state

    async def async_consume(self, state: str) -> bool:
        try:
            async with Database(self.database_url) as database:
                async with database.transaction():
                    c = self.oauth_states.c
                    query = self.oauth_states.select().where(and_(c.state == state, c.expire_at > datetime.utcnow()))
                    row = await database.fetch_one(query)
                    self.logger.debug(f"consume's query result: {row}")
                    await database.execute(self.oauth_states.delete().where(c.id == row["id"]))
                    return True
            return False
        except Exception as e:
            message = f"Failed to find any persistent data for state: {state} - {e}"
            self.logger.warning(message)
            return False


database_url = "sqlite:///slackapp.db"
# database_url = "postgresql://localhost/slackapp"  # pip install psycopg2 databases[postgresql]

logger = logging.getLogger(__name__)
client_id, client_secret, signing_secret = (
    os.environ["SLACK_CLIENT_ID"],
    os.environ["SLACK_CLIENT_SECRET"],
    os.environ["SLACK_SIGNING_SECRET"],
)

installation_store = AsyncSQLAlchemyInstallationStore(
    client_id=client_id,
    database_url=database_url,
    logger=logger,
)
oauth_state_store = AsyncSQLAlchemyOAuthStateStore(
    expiration_seconds=120,
    database_url=database_url,
    logger=logger,
)

app = AsyncApp(
    logger=logger,
    signing_secret=signing_secret,
    installation_store=installation_store,
    oauth_settings=AsyncOAuthSettings(
        client_id=client_id,
        client_secret=client_secret,
        state_store=oauth_state_store,
    ),
)
app_handler = AsyncSlackRequestHandler(app)


@app.event("app_mention")
async def handle_command(say: AsyncSay):
    await say("Hi!")


from sanic import Sanic
from sanic.request import Request

api = Sanic(name="awesome-slack-app")


@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)


@api.get("/slack/install")
async def install(req: Request):
    return await app_handler.handle(req)


@api.get("/slack/oauth_redirect")
async def oauth_redirect(req: Request):
    return await app_handler.handle(req)


async def init():
    try:
        async with Database(database_url) as database:
            await database.fetch_one("select count(*) from slack_bots")
    except Exception:
        engine = sqlalchemy.create_engine(database_url)
        installation_store.metadata.create_all(engine)
        oauth_state_store.metadata.create_all(engine)


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(init())
    api.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))

# pip install -r requirements_async.txt

# # -- OAuth flow -- #
# export SLACK_SIGNING_SECRET=***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,channels:history,im:history,chat:write

# python async_oauth_app.py
# or
# uvicorn async_oauth_app:api --reload --port 3000 --log-level warning
