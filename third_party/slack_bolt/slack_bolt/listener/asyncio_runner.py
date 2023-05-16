import asyncio
import time
from asyncio import Future
from logging import Logger
from typing import Optional, Callable, Awaitable

from slack_bolt.context.ack.async_ack import AsyncAck
from slack_bolt.lazy_listener.async_runner import AsyncLazyListenerRunner
from slack_bolt.listener.async_listener import AsyncListener
from slack_bolt.listener.async_listener_start_handler import (
    AsyncListenerStartHandler,
)
from slack_bolt.listener.async_listener_completion_handler import (
    AsyncListenerCompletionHandler,
)
from slack_bolt.listener.async_listener_error_handler import AsyncListenerErrorHandler
from slack_bolt.logger.messages import (
    debug_responding,
    debug_running_lazy_listener,
    warning_did_not_call_ack,
)
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.util.utils import create_copy, get_name_for_callable


class AsyncioListenerRunner:
    logger: Logger
    process_before_response: bool
    listener_error_handler: AsyncListenerErrorHandler
    listener_start_handler: AsyncListenerStartHandler
    listener_completion_handler: AsyncListenerCompletionHandler
    lazy_listener_runner: AsyncLazyListenerRunner

    def __init__(
        self,
        logger: Logger,
        process_before_response: bool,
        listener_error_handler: AsyncListenerErrorHandler,
        listener_start_handler: AsyncListenerStartHandler,
        listener_completion_handler: AsyncListenerCompletionHandler,
        lazy_listener_runner: AsyncLazyListenerRunner,
    ):
        self.logger = logger
        self.process_before_response = process_before_response
        self.listener_error_handler = listener_error_handler
        self.listener_start_handler = listener_start_handler
        self.listener_completion_handler = listener_completion_handler
        self.lazy_listener_runner = lazy_listener_runner

    async def run(
        self,
        request: AsyncBoltRequest,
        response: BoltResponse,
        listener_name: str,
        listener: AsyncListener,
        starting_time: Optional[float] = None,
    ) -> Optional[BoltResponse]:
        ack = request.context.ack
        starting_time = starting_time if starting_time is not None else time.time()
        if self.process_before_response:
            if not request.lazy_only:
                try:
                    await self.listener_start_handler.handle(request=request, response=response)
                    returned_value = await listener.run_ack_function(request=request, response=response)
                    if isinstance(returned_value, BoltResponse):
                        response = returned_value
                    if ack.response is None and listener.auto_acknowledgement:
                        await ack()  # automatic ack() call if the call is not yet done
                except Exception as e:
                    # The default response status code is 500 in this case.
                    # You can customize this by passing your own error handler.
                    if response is None:
                        response = BoltResponse(status=500)
                    response.status = 500
                    await self.listener_error_handler.handle(
                        error=e,
                        request=request,
                        response=response,
                    )
                    ack.response = response
                finally:
                    await self.listener_completion_handler.handle(request=request, response=response)

            for lazy_func in listener.lazy_functions:
                if request.lazy_function_name:
                    func_name = get_name_for_callable(lazy_func)
                    if func_name == request.lazy_function_name:
                        await self.lazy_listener_runner.run(function=lazy_func, request=request)
                        # This HTTP response won't be sent to Slack API servers.
                        return BoltResponse(status=200)
                    else:
                        continue
                else:
                    self._start_lazy_function(lazy_func, request)

            if response is not None:
                self._debug_log_completion(starting_time, response)
                return response
            elif ack.response is not None:
                self._debug_log_completion(starting_time, ack.response)
                return ack.response
        else:
            if listener.auto_acknowledgement:
                # acknowledge immediately in case of Events API
                await ack()

            if not request.lazy_only:
                # start the listener function asynchronously
                # NOTE: intentionally
                async def run_ack_function_asynchronously(
                    ack: AsyncAck,
                    request: AsyncBoltRequest,
                    response: BoltResponse,
                ):
                    try:
                        await self.listener_start_handler.handle(request=request, response=response)
                        await listener.run_ack_function(request=request, response=response)
                    except Exception as e:
                        # The default response status code is 500 in this case.
                        # You can customize this by passing your own error handler.
                        if response is None:
                            response = BoltResponse(status=500)
                        response.status = 500
                        if ack.response is not None:  # already acknowledged
                            response = None

                        await self.listener_error_handler.handle(
                            error=e,
                            request=request,
                            response=response,
                        )
                        ack.response = response
                    finally:
                        await self.listener_completion_handler.handle(request=request, response=response)

                _f: Future = asyncio.ensure_future(run_ack_function_asynchronously(ack, request, response))

            for lazy_func in listener.lazy_functions:
                if request.lazy_function_name:
                    func_name = get_name_for_callable(lazy_func)
                    if func_name == request.lazy_function_name:
                        await self.lazy_listener_runner.run(function=lazy_func, request=request)
                        # This HTTP response won't be sent to Slack API servers.
                        return BoltResponse(status=200)
                    else:
                        continue
                else:
                    self._start_lazy_function(lazy_func, request)

            # await for the completion of ack() in the async listener execution
            while ack.response is None and time.time() - starting_time <= 3:
                await asyncio.sleep(0.01)

            if response is None and ack.response is None:
                self.logger.warning(warning_did_not_call_ack(listener_name))
                return None

            if response is None and ack.response is not None:
                response = ack.response
                self._debug_log_completion(starting_time, response)
                return response

            if response is not None:
                return response

        # None for both means no ack() in the listener
        return None

    def _start_lazy_function(self, lazy_func: Callable[..., Awaitable[None]], request: AsyncBoltRequest) -> None:
        # Start a lazy function asynchronously
        func_name: str = get_name_for_callable(lazy_func)
        self.logger.debug(debug_running_lazy_listener(func_name))
        copied_request = self._build_lazy_request(request, func_name)
        self.lazy_listener_runner.start(function=lazy_func, request=copied_request)

    @staticmethod
    def _build_lazy_request(request: AsyncBoltRequest, lazy_func_name: str) -> AsyncBoltRequest:
        copied_request = create_copy(request.to_copyable())
        copied_request.method = "NONE"
        copied_request.lazy_only = True
        copied_request.lazy_function_name = lazy_func_name
        return copied_request

    def _debug_log_completion(self, starting_time: float, response: BoltResponse) -> None:
        millis = int((time.time() - starting_time) * 1000)
        self.logger.debug(debug_responding(response.status, response.body, millis))
