from slack_bolt.context.context import BoltContext
from slack_sdk.oauth.installation_store.installation_store import InstallationStore


class TokenRevocationListeners:
    """Listener functions to handle token revocation / uninstallation events"""

    installation_store: InstallationStore

    def __init__(self, installation_store: InstallationStore):
        self.installation_store = installation_store

    def handle_tokens_revoked_events(self, event: dict, context: BoltContext) -> None:
        user_ids = event.get("tokens", {}).get("oauth", [])
        if len(user_ids) > 0:
            for user_id in user_ids:
                self.installation_store.delete_installation(
                    enterprise_id=context.enterprise_id,
                    team_id=context.team_id,
                    user_id=user_id,
                )
        bots = event.get("tokens", {}).get("bot", [])
        if len(bots) > 0:
            self.installation_store.delete_bot(
                enterprise_id=context.enterprise_id,
                team_id=context.team_id,
            )

    def handle_app_uninstalled_events(self, context: BoltContext) -> None:
        self.installation_store.delete_all(
            enterprise_id=context.enterprise_id,
            team_id=context.team_id,
        )
