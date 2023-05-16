from logging import Logger
from typing import Optional

from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)

from ..logger.messages import warning_installation_store_conflicts

# key: client_id, value: AsyncInstallationStore
default_installation_stores = {}


def get_or_create_default_installation_store(client_id: str) -> AsyncInstallationStore:
    store = default_installation_stores.get(client_id)
    if store is None:
        store = FileInstallationStore(client_id=client_id)
        default_installation_stores[client_id] = store
    return store


def select_consistent_installation_store(
    client_id: str,
    app_store: Optional[AsyncInstallationStore],
    oauth_flow_store: Optional[AsyncInstallationStore],
    logger: Logger,
) -> Optional[AsyncInstallationStore]:
    default = get_or_create_default_installation_store(client_id)
    if app_store is not None:
        if oauth_flow_store is not None:
            if oauth_flow_store is default:
                # only app_store is intentionally set in this case
                return app_store

            # if both are intentionally set, prioritize app_store
            if oauth_flow_store is not app_store:
                logger.warning(warning_installation_store_conflicts())
            return oauth_flow_store
        else:
            # only app_store is available
            return app_store
    else:
        # only oauth_flow_store is available
        return oauth_flow_store
