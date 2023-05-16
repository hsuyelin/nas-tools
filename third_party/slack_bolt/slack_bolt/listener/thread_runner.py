import time
from concurrent.futures import Executor
from logging import Logger
from typing import Optional, Callable

from slack_bolt.lazy_listener import LazyListenerRunner
from slack_bolt.listener import Listener
from slack_bolt.listener.listener_start_handler import ListenerStartHandler
from slack_bolt.listener.listener_completion_handler import ListenerCompletionHandler
from slack_bolt.listener.listener_error_handler import ListenerErrorHandler
from slack_bolt.logger.messages import (
    debug_responding,
    debug_running_lazy_listener,
    warning_did_not_call_ack,
)
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.util.utils import create_copy, get_name_for_callable


class ThreadListenerRunner:
    logger: Logger
    process_before_response: bool
    listener_error_handler: ListenerErrorHandler
    listener_start_handler: ListenerStartHandler
    listener_completion_handler: ListenerCompletionHandler
    listener_executor: Executor
    lazy_listener_runner: LazyListenerRunner

    def __init__(
        self,
        logger: Logger,
        process_before_response: bool,
        listener_error_handler: ListenerErrorHandler,
        listener_start_handler: ListenerStartHandler,
        listener_completion_handler: ListenerCompletionHandler,
        listener_executor: Executor,
        lazy_listener_runner: LazyListenerRunner,
    ):
        self.logger = logger
        self.process_before_response = process_before_response
        self.listener_error_handler = listener_error_handler
        self.listener_start_handler = listener_start_handler
        self.listener_completion_handler = listener_completion_handler
        self.listener_executor = listener_executor
        self.lazy_listener_runner = lazy_listener_runner

    def run(  # type: ignore
        self,
        request: BoltRequest,
        response: BoltResponse,
        listener_name: str,
        listener: Listener,
        starting_time: Optional[float] = None,
    ) -> Optional[BoltResponse]:
        ack = request.context.ack
        starting_time = starting_time if starting_time is not None else time.time()
        if self.process_before_response:
            if not request.lazy_only:
                try:
                    self.listener_start_handler.handle(
                        request=request,
                        response=response,
                    )
                    returned_value = listener.run_ack_function(request=request, response=response)
                    if isinstance(returned_value, BoltResponse):
                        response = returned_value
                    if ack.response is None and listener.auto_acknowledgement:
                        ack()  # automatic ack() call if the call is not yet done
                except Exception as e:
                    # The default response status code is 500 in this case.
                    # You can customize this by passing your own error handler.
                    if response is None:
                        response = BoltResponse(status=500)
                    response.status = 500
                    self.listener_error_handler.handle(
                        error=e,
                        request=request,
                        response=response,
                    )
                    ack.response = response
                finally:
                    self.listener_completion_handler.handle(
                        request=request,
                        response=response,
                    )

            for lazy_func in listener.lazy_functions:
                if request.lazy_function_name:
                    func_name = get_name_for_callable(lazy_func)
                    if func_name == request.lazy_function_name:
                        self.lazy_listener_runner.run(function=lazy_func, request=request)
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
                ack()

            if not request.lazy_only:
                # start the listener function asynchronously
                def run_ack_function_asynchronously():
                    nonlocal ack, request, response
                    try:
                        self.listener_start_handler.handle(
                            request=request,
                            response=response,
                        )
                        listener.run_ack_function(request=request, response=response)
                    except Exception as e:
                        # The default response status code is 500 in this case.
                        # You can customize this by passing your own error handler.
                        if listener.auto_acknowledgement:
                            self.listener_error_handler.handle(
                                error=e,
                                request=request,
                                response=response,
                            )
                        else:
                            if response is None:
                                response = BoltResponse(status=500)
                            response.status = 500
                            if ack.response is not None:  # already acknowledged
                                response = None
                            self.listener_error_handler.handle(
                                error=e,
                                request=request,
                                response=response,
                            )
                            ack.response = response
                    finally:
                        self.listener_completion_handler.handle(
                            request=request,
                            response=response,
                        )

                self.listener_executor.submit(run_ack_function_asynchronously)

            for lazy_func in listener.lazy_functions:
                if request.lazy_function_name:
                    func_name = get_name_for_callable(lazy_func)
                    if func_name == request.lazy_function_name:
                        self.lazy_listener_runner.run(function=lazy_func, request=request)
                        # This HTTP response won't be sent to Slack API servers.
                        return BoltResponse(status=200)
                    else:
                        continue
                else:
                    self._start_lazy_function(lazy_func, request)

            # await for the completion of ack() in the async listener execution
            while ack.response is None and time.time() - starting_time <= 3:
                time.sleep(0.01)

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

    def _start_lazy_function(self, lazy_func: Callable[..., None], request: BoltRequest) -> None:
        # Start a lazy function asynchronously
        func_name: str = get_name_for_callable(lazy_func)
        self.logger.debug(debug_running_lazy_listener(func_name))
        copied_request = self._build_lazy_request(request, func_name)
        self.lazy_listener_runner.start(function=lazy_func, request=copied_request)

    @staticmethod
    def _build_lazy_request(request: BoltRequest, lazy_func_name: str) -> BoltRequest:
        copied_request = create_copy(request.to_copyable())
        copied_request.method = "NONE"
        copied_request.lazy_only = True
        copied_request.lazy_function_name = lazy_func_name
        return copied_request

    def _debug_log_completion(self, starting_time: float, response: BoltResponse) -> None:
        millis = int((time.time() - starting_time) * 1000)
        self.logger.debug(debug_responding(response.status, response.body, millis))
