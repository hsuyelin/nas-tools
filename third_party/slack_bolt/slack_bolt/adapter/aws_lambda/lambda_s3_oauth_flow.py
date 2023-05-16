import logging
import os
from logging import Logger
from typing import Optional

import boto3

from slack_bolt.authorization.authorize import InstallationStoreAuthorize
from slack_bolt.oauth import OAuthFlow
from slack_sdk import WebClient
from slack_sdk.oauth.installation_store.amazon_s3 import AmazonS3InstallationStore
from slack_sdk.oauth.state_store.amazon_s3 import AmazonS3OAuthStateStore

from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.util.utils import create_web_client


class LambdaS3OAuthFlow(OAuthFlow):
    def __init__(
        self,
        *,
        client: Optional[WebClient] = None,
        logger: Optional[Logger] = None,
        settings: Optional[OAuthSettings] = None,
        oauth_state_bucket_name: Optional[str] = None,  # required
        installation_bucket_name: Optional[str] = None,  # required
    ):
        logger = logger or logging.getLogger(__name__)
        settings = settings or OAuthSettings(
            client_id=os.environ["SLACK_CLIENT_ID"],
            client_secret=os.environ["SLACK_CLIENT_SECRET"],
        )
        oauth_state_bucket_name = oauth_state_bucket_name or os.environ["SLACK_STATE_S3_BUCKET_NAME"]
        installation_bucket_name = installation_bucket_name or os.environ["SLACK_INSTALLATION_S3_BUCKET_NAME"]
        self.s3_client = boto3.client("s3")
        if settings.state_store is None or not isinstance(settings.state_store, AmazonS3OAuthStateStore):
            settings.state_store = AmazonS3OAuthStateStore(
                logger=logger,
                s3_client=self.s3_client,
                bucket_name=oauth_state_bucket_name,
                expiration_seconds=settings.state_expiration_seconds,
            )

        if settings.installation_store is None or not isinstance(settings.installation_store, AmazonS3InstallationStore):
            settings.installation_store = AmazonS3InstallationStore(
                logger=logger,
                s3_client=self.s3_client,
                bucket_name=installation_bucket_name,
                client_id=settings.client_id,
            )

        # Set up authorize function to surely use this installation_store.
        # When a developer use a settings initialized outside this constructor,
        # the settings may already have pre-defined authorize.
        # In this case, the /slack/events endpoint doesn't work along with the OAuth flow.
        settings.authorize = InstallationStoreAuthorize(
            logger=logger,
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            installation_store=settings.installation_store,
            bot_only=settings.installation_store_bot_only,
            user_token_resolution=(settings.user_token_resolution if settings is not None else "authed_user"),
        )

        OAuthFlow.__init__(self, client=client, logger=logger, settings=settings)

    @property
    def client(self) -> WebClient:
        if self._client is None:
            self._client = create_web_client(logger=self.logger)
        return self._client

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger
