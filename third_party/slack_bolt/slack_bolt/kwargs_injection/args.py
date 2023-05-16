# pytype: skip-file
import logging
from logging import Logger
from typing import Callable, Dict, Any, Optional

from slack_bolt.context import BoltContext
from slack_bolt.context.ack import Ack
from slack_bolt.context.respond import Respond
from slack_bolt.context.say import Say
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from slack_sdk import WebClient


class Args:
    """All the arguments in this class are available in any middleware / listeners.
    You can inject the named variables in the argument list in arbitrary order.

        @app.action("link_button")
        def handle_buttons(ack, respond, logger, context, body, client):
            logger.info(f"request body: {body}")
            ack()
            if context.channel_id is not None:
                respond("Hi!")
            client.views_open(
                trigger_id=body["trigger_id"],
                view={ ... }
            )

    Alternatively, you can include a parameter named `args` and it will be injected with an instance of this class.

        @app.action("link_button")
        def handle_buttons(args):
            args.logger.info(f"request body: {args.body}")
            args.ack()
            if args.context.channel_id is not None:
                args.respond("Hi!")
            args.client.views_open(
                trigger_id=args.body["trigger_id"],
                view={ ... }
            )

    """

    client: WebClient
    """`slack_sdk.web.WebClient` instance with a valid token"""
    logger: Logger
    """Logger instance"""
    req: BoltRequest
    """Incoming request from Slack"""
    resp: BoltResponse
    """Response representation"""
    request: BoltRequest
    """Incoming request from Slack"""
    response: BoltResponse
    """Response representation"""
    context: BoltContext
    """Context data associated with the incoming request"""
    body: Dict[str, Any]
    """Parsed request body data"""
    # payload
    payload: Dict[str, Any]
    """The unwrapped core data in the request body"""
    options: Optional[Dict[str, Any]]  # payload alias
    """An alias for payload in an `@app.options` listener"""
    shortcut: Optional[Dict[str, Any]]  # payload alias
    """An alias for payload in an `@app.shortcut` listener"""
    action: Optional[Dict[str, Any]]  # payload alias
    """An alias for payload in an `@app.action` listener"""
    view: Optional[Dict[str, Any]]  # payload alias
    """An alias for payload in an `@app.view` listener"""
    command: Optional[Dict[str, Any]]  # payload alias
    """An alias for payload in an `@app.command` listener"""
    event: Optional[Dict[str, Any]]  # payload alias
    """An alias for payload in an `@app.event` listener"""
    message: Optional[Dict[str, Any]]  # payload alias
    """An alias for payload in an `@app.message` listener"""
    # utilities
    ack: Ack
    """`ack()` utility function, which returns acknowledgement to the Slack servers"""
    say: Say
    """`say()` utility function, which calls `chat.postMessage` API with the associated channel ID"""
    respond: Respond
    """`respond()` utility function, which utilizes the associated `response_url`"""
    # middleware
    next: Callable[[], None]
    """`next()` utility function, which tells the middleware chain that it can continue with the next one"""
    next_: Callable[[], None]
    """An alias of `next()` for avoiding the Python built-in method overrides in middleware functions"""

    def __init__(
        self,
        *,
        logger: logging.Logger,
        client: WebClient,
        req: BoltRequest,
        resp: BoltResponse,
        context: BoltContext,
        body: Dict[str, Any],
        payload: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
        shortcut: Optional[Dict[str, Any]] = None,
        action: Optional[Dict[str, Any]] = None,
        view: Optional[Dict[str, Any]] = None,
        command: Optional[Dict[str, Any]] = None,
        event: Optional[Dict[str, Any]] = None,
        message: Optional[Dict[str, Any]] = None,
        ack: Ack,
        say: Say,
        respond: Respond,
        # As this method is not supposed to be invoked by bolt-python users,
        # the naming conflict with the built-in one affects
        # only the internals of this method
        next: Callable[[], None],
        **kwargs  # noqa
    ):
        self.logger: logging.Logger = logger
        self.client: WebClient = client
        self.request = self.req = req
        self.response = self.resp = resp
        self.context: BoltContext = context

        self.body: Dict[str, Any] = body
        self.payload: Dict[str, Any] = payload
        self.options: Optional[Dict[str, Any]] = options
        self.shortcut: Optional[Dict[str, Any]] = shortcut
        self.action: Optional[Dict[str, Any]] = action
        self.view: Optional[Dict[str, Any]] = view
        self.command: Optional[Dict[str, Any]] = command
        self.event: Optional[Dict[str, Any]] = event
        self.message: Optional[Dict[str, Any]] = message

        self.ack: Ack = ack
        self.say: Say = say
        self.respond: Respond = respond
        self.next: Callable[[], None] = next
        self.next_: Callable[[], None] = next
