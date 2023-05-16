import json

from chalice.app import Chalice
from chalice.config import Config
from chalice.test import BaseClient, LambdaContext, InvokeResponse


class LocalLambdaClient(BaseClient):
    """Lambda client implementing `invoke` for use when running with Chalice CLI."""

    def __init__(self, app: Chalice, config: Config) -> None:
        self._app = app
        self._config = config if config else Config()

    def invoke(
        self,
        FunctionName: str,
        InvocationType: str = "Event",
        Payload: str = "{}",
    ) -> InvokeResponse:
        scoped = self._config.scope(self._config.chalice_stage, FunctionName)
        lambda_context = LambdaContext(FunctionName, memory_size=scoped.lambda_memory_size)

        with self._patched_env_vars(scoped.environment_variables):
            response = self._app(json.loads(Payload), lambda_context)
        return InvokeResponse(payload=response)
