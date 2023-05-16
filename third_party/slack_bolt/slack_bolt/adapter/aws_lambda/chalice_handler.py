import logging
from os import getenv
from typing import Optional

from botocore.client import BaseClient

from chalice.app import Request, Response, Chalice

from slack_bolt.adapter.aws_lambda.chalice_lazy_listener_runner import (
    ChaliceLazyListenerRunner,
)
from slack_bolt.adapter.aws_lambda.internals import _first_value
from slack_bolt.app import App
from slack_bolt.logger import get_bolt_app_logger
from slack_bolt.oauth import OAuthFlow
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


class ChaliceSlackRequestHandler:
    def __init__(self, app: App, chalice: Chalice, lambda_client: Optional[BaseClient] = None):  # type: ignore
        self.app = app
        self.chalice = chalice
        self.logger = get_bolt_app_logger(app.name, ChaliceSlackRequestHandler, app.logger)

        if getenv("AWS_CHALICE_CLI_MODE") == "true" and lambda_client is None:
            try:
                from slack_bolt.adapter.aws_lambda.local_lambda_client import (
                    LocalLambdaClient,
                )

                lambda_client = LocalLambdaClient(self.chalice, None)
            except ImportError:
                logging.info("Failed to load LocalLambdaClient for CLI mode.")
                pass

        self.app.listener_runner.lazy_listener_runner = ChaliceLazyListenerRunner(
            logger=self.logger, lambda_client=lambda_client
        )

        if self.app.oauth_flow is not None:
            self.app.oauth_flow.settings.redirect_uri_page_renderer.install_path = "?"

    @classmethod
    def clear_all_log_handlers(cls):
        # https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)

    def handle(self, request: Request):
        body: str = request.raw_body.decode("utf-8") if request.raw_body else ""
        self.logger.debug(f"Incoming request: {request.to_dict()}, body: {body}")

        method = request.method
        if method is None:
            return not_found()
        if method == "GET":
            if self.app.oauth_flow is not None:
                oauth_flow: OAuthFlow = self.app.oauth_flow
                bolt_req: BoltRequest = to_bolt_request(request, body)
                query = bolt_req.query
                is_callback = query is not None and (
                    (_first_value(query, "code") is not None and _first_value(query, "state") is not None)
                    or _first_value(query, "error") is not None
                )
                if is_callback:
                    bolt_resp = oauth_flow.handle_callback(bolt_req)
                    return to_chalice_response(bolt_resp)
                else:
                    bolt_resp = oauth_flow.handle_installation(bolt_req)
                    return to_chalice_response(bolt_resp)
        elif method == "POST":
            bolt_req: BoltRequest = to_bolt_request(request, body)
            # https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
            aws_lambda_function_name = self.chalice.lambda_context.function_name
            bolt_req.context["aws_lambda_function_name"] = aws_lambda_function_name
            bolt_req.context["chalice_request"] = request.to_dict()
            bolt_resp = self.app.dispatch(bolt_req)
            aws_response = to_chalice_response(bolt_resp)
            return aws_response
        elif method == "NONE":
            bolt_req: BoltRequest = to_bolt_request(request, body)
            bolt_resp = self.app.dispatch(bolt_req)
            aws_response = to_chalice_response(bolt_resp)
            return aws_response

        return not_found()


def to_bolt_request(request: Request, body: str) -> BoltRequest:
    return BoltRequest(
        body=body,
        query=request.query_params,
        headers=request.headers,
    )


def to_chalice_response(resp: BoltResponse) -> Response:
    return Response(
        status_code=resp.status,
        body=resp.body,
        headers=resp.first_headers(),
    )


def not_found() -> Response:
    return Response(
        status_code=404,
        body="Not Found",
        headers={},
    )
