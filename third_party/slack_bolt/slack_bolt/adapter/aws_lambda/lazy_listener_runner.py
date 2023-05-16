import json
from logging import Logger
from typing import Callable, Optional, Any

import boto3

from slack_bolt import BoltRequest
from slack_bolt.lazy_listener import LazyListenerRunner


class LambdaLazyListenerRunner(LazyListenerRunner):
    def __init__(self, logger: Logger, lambda_client: Optional[Any] = None):
        self.lambda_client = lambda_client
        self.logger = logger

    def start(self, function: Callable[..., None], request: BoltRequest) -> None:
        if self.lambda_client is None:
            self.lambda_client = boto3.client("lambda")

        event: dict = request.context["lambda_request"]
        headers = event["headers"]
        headers["x-slack-bolt-lazy-only"] = "1"  # not an array
        headers["x-slack-bolt-lazy-function-name"] = request.lazy_function_name  # not an array
        event["method"] = "NONE"
        invocation = self.lambda_client.invoke(
            FunctionName=request.context["aws_lambda_invoked_function_arn"],
            InvocationType="Event",
            Payload=json.dumps(event),
        )
        self.logger.info(invocation)
