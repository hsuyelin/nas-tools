from moto import mock_s3

from slack_bolt.adapter.aws_lambda.lambda_s3_oauth_flow import LambdaS3OAuthFlow
from slack_bolt.oauth.oauth_settings import OAuthSettings
from tests.utils import remove_os_env_temporarily, restore_os_env


class TestLambdaS3OAuthFlow:
    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()

    def teardown_method(self):
        restore_os_env(self.old_os_env)

    @mock_s3
    def test_instantiation(self):
        oauth_flow = LambdaS3OAuthFlow(
            settings=OAuthSettings(
                client_id="111.222",
                client_secret="xxx",
                scopes=["chat:write"],
            ),
            installation_bucket_name="dummy-installation",
            oauth_state_bucket_name="dummy-state",
        )
        assert oauth_flow is not None
        assert oauth_flow.client is not None
        assert oauth_flow.logger is not None
