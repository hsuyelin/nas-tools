from functools import wraps
from logging import Logger
from typing import Callable, Union, Optional, Sequence, Pattern, List

from slack_bolt.context.context import BoltContext
from slack_bolt.error import BoltError
from slack_bolt.listener import Listener, CustomListener
from slack_bolt.listener_matcher import ListenerMatcher, CustomListenerMatcher
from slack_bolt.listener_matcher.builtins import (
    workflow_step_edit,
    workflow_step_save,
    workflow_step_execute,
)
from slack_bolt.middleware import CustomMiddleware, Middleware
from slack_bolt.response import BoltResponse
from slack_bolt.workflows.step.internals import _is_used_without_argument
from slack_bolt.workflows.step.utilities.complete import Complete
from slack_bolt.workflows.step.utilities.configure import Configure
from slack_bolt.workflows.step.utilities.fail import Fail
from slack_bolt.workflows.step.utilities.update import Update
from slack_sdk.web import WebClient


class WorkflowStepBuilder:
    """Steps from Apps
    Refer to https://api.slack.com/workflows/steps for details.
    """

    callback_id: Union[str, Pattern]
    _base_logger: Optional[Logger]
    _edit: Optional[Listener]
    _save: Optional[Listener]
    _execute: Optional[Listener]

    def __init__(
        self,
        callback_id: Union[str, Pattern],
        app_name: Optional[str] = None,
        base_logger: Optional[Logger] = None,
    ):
        """This builder is supposed to be used as decorator.

            my_step = WorkflowStep.builder("my_step")
            @my_step.edit
            def edit_my_step(ack, configure):
                pass
            @my_step.save
            def save_my_step(ack, step, update):
                pass
            @my_step.execute
            def execute_my_step(step, complete, fail):
                pass
            app.step(my_step)

        For further information about WorkflowStep specific function arguments
        such as `configure`, `update`, `complete`, and `fail`,
        refer to `slack_bolt.workflows.step.utilities` API documents.

        Args:
            callback_id: The callback_id for the workflow
            app_name: The application name mainly for logging
            base_logger: The base logger
        """
        self.callback_id = callback_id
        self.app_name = app_name or __name__
        self._base_logger = base_logger
        self._edit = None
        self._save = None
        self._execute = None

    def edit(
        self,
        *args,
        matchers: Optional[Union[Callable[..., bool], ListenerMatcher]] = None,
        middleware: Optional[Union[Callable, Middleware]] = None,
        lazy: Optional[List[Callable[..., None]]] = None,
    ):
        """Registers a new edit listener with details.
        You can use this method as decorator as well.

            @my_step.edit
            def edit_my_step(ack, configure):
                pass

        It's also possible to add additional listener matchers and/or middleware

            @my_step.edit(matchers=[is_valid], middleware=[update_context])
            def edit_my_step(ack, configure):
                pass

        For further information about WorkflowStep specific function arguments
        such as `configure`, `update`, `complete`, and `fail`,
        refer to `slack_bolt.workflows.step.utilities` API documents.

        Args:
            *args: This method can behave as either decorator or a method
            matchers: Listener matchers
            middleware: Listener middleware
            lazy: Lazy listeners
        """

        if _is_used_without_argument(args):
            func = args[0]
            self._edit = self._to_listener("edit", func, matchers, middleware)
            return func

        def _inner(func):
            functions = [func] + (lazy if lazy is not None else [])
            self._edit = self._to_listener("edit", functions, matchers, middleware)

            @wraps(func)
            def _wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return _wrapper

        return _inner

    def save(
        self,
        *args,
        matchers: Optional[Union[Callable[..., bool], ListenerMatcher]] = None,
        middleware: Optional[Union[Callable, Middleware]] = None,
        lazy: Optional[List[Callable[..., None]]] = None,
    ):
        """Registers a new save listener with details.
        You can use this method as decorator as well.

            @my_step.save
            def save_my_step(ack, step, update):
                pass

        It's also possible to add additional listener matchers and/or middleware

            @my_step.save(matchers=[is_valid], middleware=[update_context])
            def save_my_step(ack, step, update):
                pass

        For further information about WorkflowStep specific function arguments
        such as `configure`, `update`, `complete`, and `fail`,
        refer to `slack_bolt.workflows.step.utilities` API documents.

        Args:
            *args: This method can behave as either decorator or a method
            matchers: Listener matchers
            middleware: Listener middleware
            lazy: Lazy listeners
        """
        if _is_used_without_argument(args):
            func = args[0]
            self._save = self._to_listener("save", func, matchers, middleware)
            return func

        def _inner(func):
            functions = [func] + (lazy if lazy is not None else [])
            self._save = self._to_listener("save", functions, matchers, middleware)

            @wraps(func)
            def _wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return _wrapper

        return _inner

    def execute(
        self,
        *args,
        matchers: Optional[Union[Callable[..., bool], ListenerMatcher]] = None,
        middleware: Optional[Union[Callable, Middleware]] = None,
        lazy: Optional[List[Callable[..., None]]] = None,
    ):
        """Registers a new execute listener with details.
        You can use this method as decorator as well.

            @my_step.execute
            def execute_my_step(step, complete, fail):
                pass

        It's also possible to add additional listener matchers and/or middleware

            @my_step.save(matchers=[is_valid], middleware=[update_context])
            def execute_my_step(step, complete, fail):
                pass

        For further information about WorkflowStep specific function arguments
        such as `configure`, `update`, `complete`, and `fail`,
        refer to `slack_bolt.workflows.step.utilities` API documents.

        Args:
            *args: This method can behave as either decorator or a method
            matchers: Listener matchers
            middleware: Listener middleware
            lazy: Lazy listeners
        """
        if _is_used_without_argument(args):
            func = args[0]
            self._execute = self._to_listener("execute", func, matchers, middleware)
            return func

        def _inner(func):
            functions = [func] + (lazy if lazy is not None else [])
            self._execute = self._to_listener("execute", functions, matchers, middleware)

            @wraps(func)
            def _wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return _wrapper

        return _inner

    def build(self, base_logger: Optional[Logger] = None) -> "WorkflowStep":
        """Constructs a WorkflowStep object. This method may raise an exception
        if the builder doesn't have enough configurations to build the object.

        Returns:
            WorkflowStep object
        """
        if self._edit is None:
            raise BoltError("edit listener is not registered")
        if self._save is None:
            raise BoltError("save listener is not registered")
        if self._execute is None:
            raise BoltError("execute listener is not registered")

        return WorkflowStep(
            callback_id=self.callback_id,
            edit=self._edit,
            save=self._save,
            execute=self._execute,
            app_name=self.app_name,
            base_logger=base_logger,
        )

    # ---------------------------------------

    def _to_listener(
        self,
        name: str,
        listener_or_functions: Union[Listener, Callable, List[Callable]],
        matchers: Optional[Union[Callable[..., bool], ListenerMatcher]] = None,
        middleware: Optional[Union[Callable, Middleware]] = None,
    ) -> Listener:
        return WorkflowStep.build_listener(
            callback_id=self.callback_id,
            app_name=self.app_name,
            listener_or_functions=listener_or_functions,
            name=name,
            matchers=self.to_listener_matchers(self.app_name, matchers, self._base_logger),
            middleware=self.to_listener_middleware(self.app_name, middleware, self._base_logger),
            base_logger=self._base_logger,
        )

    @staticmethod
    def to_listener_matchers(
        app_name: str,
        matchers: Optional[List[Union[Callable[..., bool], ListenerMatcher]]],
        base_logger: Optional[Logger] = None,
    ) -> List[ListenerMatcher]:
        _matchers = []
        if matchers is not None:
            for m in matchers:
                if isinstance(m, ListenerMatcher):
                    _matchers.append(m)
                elif isinstance(m, Callable):
                    _matchers.append(
                        CustomListenerMatcher(
                            app_name=app_name,
                            func=m,
                            base_logger=base_logger,
                        )
                    )
                else:
                    raise ValueError(f"Invalid matcher: {type(m)}")
        return _matchers  # type: ignore

    @staticmethod
    def to_listener_middleware(
        app_name: str,
        middleware: Optional[List[Union[Callable, Middleware]]],
        base_logger: Optional[Logger] = None,
    ) -> List[Middleware]:
        _middleware = []
        if middleware is not None:
            for m in middleware:
                if isinstance(m, Middleware):
                    _middleware.append(m)
                elif isinstance(m, Callable):
                    _middleware.append(
                        CustomMiddleware(
                            app_name=app_name,
                            func=m,
                            base_logger=base_logger,
                        )
                    )
                else:
                    raise ValueError(f"Invalid middleware: {type(m)}")
        return _middleware  # type: ignore


class WorkflowStep:
    callback_id: Union[str, Pattern]
    """The Callback ID of the workflow step"""
    edit: Listener
    """`edit` listener, which displays a modal in Workflow Builder"""
    save: Listener
    """`save` listener, which accepts workflow creator's data submission in Workflow Builder"""
    execute: Listener
    """`execute` listener, which processes workflow step execution"""

    def __init__(
        self,
        *,
        callback_id: Union[str, Pattern],
        edit: Union[Callable[..., Optional[BoltResponse]], Listener, Sequence[Callable]],
        save: Union[Callable[..., Optional[BoltResponse]], Listener, Sequence[Callable]],
        execute: Union[Callable[..., Optional[BoltResponse]], Listener, Sequence[Callable]],
        app_name: Optional[str] = None,
        base_logger: Optional[Logger] = None,
    ):
        """
        Args:
            callback_id: The callback_id for this workflow step
            edit: Either a single function or a list of functions for opening a modal in the builder UI
                When it's a list, the first one is responsible for ack() while the rest are lazy listeners.
            save: Either a single function or a list of functions for handling modal interactions in the builder UI
                When it's a list, the first one is responsible for ack() while the rest are lazy listeners.
            execute: Either a single function or a list of functions for handling workflow step executions
                When it's a list, the first one is responsible for ack() while the rest are lazy listeners.
            app_name: The app name that can be mainly used for logging
            base_logger: The logger instance that can be used as a template when creating this step's logger
        """
        self.callback_id = callback_id
        app_name = app_name or __name__
        self.edit = self.build_listener(
            callback_id=callback_id,
            app_name=app_name,
            listener_or_functions=edit,
            name="edit",
            base_logger=base_logger,
        )
        self.save = self.build_listener(
            callback_id=callback_id,
            app_name=app_name,
            listener_or_functions=save,
            name="save",
            base_logger=base_logger,
        )
        self.execute = self.build_listener(
            callback_id=callback_id,
            app_name=app_name,
            listener_or_functions=execute,
            name="execute",
            base_logger=base_logger,
        )

    @classmethod
    def builder(cls, callback_id: Union[str, Pattern], base_logger: Optional[Logger] = None) -> WorkflowStepBuilder:
        return WorkflowStepBuilder(
            callback_id,
            base_logger=base_logger,
        )

    @classmethod
    def build_listener(
        cls,
        callback_id: Union[str, Pattern],
        app_name: str,
        listener_or_functions: Union[Listener, Callable, List[Callable]],
        name: str,
        matchers: Optional[List[ListenerMatcher]] = None,
        middleware: Optional[List[Middleware]] = None,
        base_logger: Optional[Logger] = None,
    ) -> Listener:
        if listener_or_functions is None:
            raise BoltError(f"{name} listener is required (callback_id: {callback_id})")

        if isinstance(listener_or_functions, Callable):
            listener_or_functions = [listener_or_functions]

        if isinstance(listener_or_functions, Listener):
            return listener_or_functions
        elif isinstance(listener_or_functions, list):
            matchers = matchers if matchers else []
            matchers.insert(
                0,
                cls._build_primary_matcher(
                    name,
                    callback_id,
                    base_logger=base_logger,
                ),
            )
            middleware = middleware if middleware else []
            middleware.insert(
                0,
                cls._build_single_middleware(
                    name,
                    callback_id,
                    base_logger=base_logger,
                ),
            )
            functions = listener_or_functions
            ack_function = functions.pop(0)
            return CustomListener(
                app_name=app_name,
                matchers=matchers,
                middleware=middleware,
                ack_function=ack_function,
                lazy_functions=functions,
                auto_acknowledgement=name == "execute",
                base_logger=base_logger,
            )
        else:
            raise BoltError(f"Invalid {name} listener: {type(listener_or_functions)} detected (callback_id: {callback_id})")

    @classmethod
    def _build_primary_matcher(
        cls,
        name: str,
        callback_id: Union[str, Pattern],
        base_logger: Optional[Logger] = None,
    ) -> ListenerMatcher:
        if name == "edit":
            return workflow_step_edit(callback_id, base_logger=base_logger)
        elif name == "save":
            return workflow_step_save(callback_id, base_logger=base_logger)
        elif name == "execute":
            return workflow_step_execute(callback_id, base_logger=base_logger)
        else:
            raise ValueError(f"Invalid name {name}")

    @classmethod
    def _build_single_middleware(
        cls,
        name: str,
        callback_id: Union[str, Pattern],
        base_logger: Optional[Logger] = None,
    ) -> Middleware:
        if name == "edit":
            return _build_edit_listener_middleware(callback_id, base_logger=base_logger)
        elif name == "save":
            return _build_save_listener_middleware(base_logger=base_logger)
        elif name == "execute":
            return _build_execute_listener_middleware(base_logger=base_logger)
        else:
            raise ValueError(f"Invalid name {name}")


#######################
# Edit
#######################


def _build_edit_listener_middleware(callback_id: str, base_logger: Optional[Logger] = None) -> Middleware:
    def edit_listener_middleware(
        context: BoltContext,
        client: WebClient,
        body: dict,
        next: Callable[[], BoltResponse],
    ):
        context["configure"] = Configure(
            callback_id=callback_id,
            client=client,
            body=body,
        )
        return next()

    return CustomMiddleware(
        app_name=__name__,
        func=edit_listener_middleware,
        base_logger=base_logger,
    )


#######################
# Save
#######################


def _build_save_listener_middleware(base_logger: Optional[Logger] = None) -> Middleware:
    def save_listener_middleware(
        context: BoltContext,
        client: WebClient,
        body: dict,
        next: Callable[[], BoltResponse],
    ):
        context["update"] = Update(
            client=client,
            body=body,
        )
        return next()

    return CustomMiddleware(
        app_name=__name__,
        func=save_listener_middleware,
        base_logger=base_logger,
    )


#######################
# Execute
#######################


def _build_execute_listener_middleware(
    base_logger: Optional[Logger] = None,
) -> Middleware:
    def execute_listener_middleware(
        context: BoltContext,
        client: WebClient,
        body: dict,
        next: Callable[[], BoltResponse],
    ):
        context["complete"] = Complete(
            client=client,
            body=body,
        )
        context["fail"] = Fail(
            client=client,
            body=body,
        )
        return next()

    return CustomMiddleware(
        app_name=__name__,
        func=execute_listener_middleware,
        base_logger=base_logger,
    )
