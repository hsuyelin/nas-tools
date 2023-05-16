from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)


class AsyncTokenRevocationListeners:
    """Listener functions to handle token revocation / uninstallation events"""

    installation_store: AsyncInstallationStore

    def __init__(self, installation_store: AsyncInstallationStore):
        self.installation_store = installation_store

    async def handle_tokens_revoked_events(self, event: dict, context: AsyncBoltContext) -> None:
        user_ids = event.get("tokens", {}).get("oauth", [])
        if len(user_ids) > 0:
            for user_id in user_ids:
                await self.installation_store.async_delete_installation(
                    enterprise_id=context.enterprise_id,
                    team_id=context.team_id,
                    user_id=user_id,
                )
        bots = event.get("tokens", {}).get("bot", [])
        if len(bots) > 0:
            await self.installation_store.async_delete_bot(
                enterprise_id=context.enterprise_id,
                team_id=context.team_id,
            )

    async def handle_app_uninstalled_events(self, context: AsyncBoltContext) -> None:
        await self.installation_store.async_delete_all(
            enterprise_id=context.enterprise_id,
            team_id=context.team_id,
        )
