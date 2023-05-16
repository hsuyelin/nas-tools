import json
from logging import Logger
from typing import Callable, Optional

import boto3
from botocore.client import BaseClient

from slack_bolt import BoltRequest
from slack_bolt.lazy_listener import LazyListenerRunner


class ChaliceLazyListenerRunner(LazyListenerRunner):
    def __init__(self, logger: Logger, lambda_client: Optional[BaseClient] = None):
        self.lambda_client = lambda_client
        self.logger = logger

    def start(self, function: Callable[..., None], request: BoltRequest) -> None:
        if self.lambda_client is None:
            self.lambda_client = boto3.client("lambda")

        chalice_request: dict = request.context["chalice_request"]
        request.headers["x-slack-bolt-lazy-only"] = ["1"]
        request.headers["x-slack-bolt-lazy-function-name"] = [request.lazy_function_name]
        payload = {
            "method": "NONE",
            "headers": {k: v[0] for k, v in request.headers.items()},
            "multiValueQueryStringParameters": request.query,
            "queryStringParameters": {k: v[0] for k, v in request.query.items()},
            "pathParameters": {},
            "stageVariables": {},
            "requestContext": chalice_request["context"],
            "body": request.raw_body,
            "isBase64Encoded": False,
        }
        invocation = self.lambda_client.invoke(
            FunctionName=request.context["aws_lambda_function_name"],
            InvocationType="Event",
            Payload=json.dumps(payload),
        )
