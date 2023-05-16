# pytype: skip-file
from logging import Logger
from typing import Callable, Awaitable, Dict, Any, Optional

from slack_bolt.context.ack.async_ack import AsyncAck
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.context.respond.async_respond import AsyncRespond
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from slack_sdk.web.async_client import AsyncWebClient


class AsyncArgs:
    """All the arguments in this class are available in any middleware / listeners.
    You can inject the named variables in the argument list in arbitrary order.

        @app.action("link_button")
        async def handle_buttons(ack, respond, logger, context, body, client):
            logger.info(f"request body: {body}")
            await ack()
            if context.channel_id is not None:
                await respond("Hi!")
            await client.views_open(
                trigger_id=body["trigger_id"],
                view={ ... }
            )

    Alternatively, you can include a parameter named `args` and it will be injected with an instance of this class.

        @app.action("link_button")
        async def handle_buttons(args):
            args.logger.info(f"request body: {args.body}")
            await args.ack()
            if args.context.channel_id is not None:
                await args.respond("Hi!")
            await args.client.views_open(
                trigger_id=args.body["trigger_id"],
                view={ ... }
            )

    """

    logger: Logger
    """Logger instance"""
    client: AsyncWebClient
    """`slack_sdk.web.async_client.AsyncWebClient` instance with a valid token"""
    req: AsyncBoltRequest
    """Incoming request from Slack"""
    resp: BoltResponse
    """Response representation"""
    request: AsyncBoltRequest
    """Incoming request from Slack"""
    response: BoltResponse
    """Response representation"""
    context: AsyncBoltContext
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
    ack: AsyncAck
    """`ack()` utility function, which returns acknowledgement to the Slack servers"""
    say: AsyncSay
    """`say()` utility function, which calls chat.postMessage API with the associated channel ID"""
    respond: AsyncRespond
    """`respond()` utility function, which utilizes the associated `response_url`"""
    # middleware
    next: Callable[[], Awaitable[None]]
    """`next()` utility function, which tells the middleware chain that it can continue with the next one"""
    next_: Callable[[], Awaitable[None]]
    """An alias of `next()` for avoiding the Python built-in method overrides in middleware functions"""

    def __init__(
        self,
        *,
        logger: Logger,
        client: AsyncWebClient,
        req: AsyncBoltRequest,
        resp: BoltResponse,
        context: AsyncBoltContext,
        body: Dict[str, Any],
        payload: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
        shortcut: Optional[Dict[str, Any]] = None,
        action: Optional[Dict[str, Any]] = None,
        view: Optional[Dict[str, Any]] = None,
        command: Optional[Dict[str, Any]] = None,
        event: Optional[Dict[str, Any]] = None,
        message: Optional[Dict[str, Any]] = None,
        ack: AsyncAck,
        say: AsyncSay,
        respond: AsyncRespond,
        next: Callable[[], Awaitable[None]],
        **kwargs  # noqa
    ):
        self.logger: Logger = logger
        self.client: AsyncWebClient = client
        self.request = self.req = req
        self.response = self.resp = resp
        self.context: AsyncBoltContext = context

        self.body: Dict[str, Any] = body
        self.payload: Dict[str, Any] = payload
        self.options: Optional[Dict[str, Any]] = options
        self.shortcut: Optional[Dict[str, Any]] = shortcut
        self.action: Optional[Dict[str, Any]] = action
        self.view: Optional[Dict[str, Any]] = view
        self.command: Optional[Dict[str, Any]] = command
        self.event: Optional[Dict[str, Any]] = event
        self.message: Optional[Dict[str, Any]] = message

        self.ack: AsyncAck = ack
        self.say: AsyncSay = say
        self.respond: AsyncRespond = respond
        self.next: Callable[[], Awaitable[None]] = next
        self.next_: Callable[[], Awaitable[None]] = next
