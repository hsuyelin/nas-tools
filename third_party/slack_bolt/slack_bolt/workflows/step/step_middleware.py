from typing import Callable, Optional

from slack_bolt.listener import Listener
from slack_bolt.listener.thread_runner import ThreadListenerRunner
from slack_bolt.middleware import Middleware
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from slack_bolt.util.utils import get_name_for_callable
from slack_bolt.workflows.step.step import WorkflowStep


class WorkflowStepMiddleware(Middleware):  # type:ignore
    """Base middleware for workflow step specific ones"""

    def __init__(self, step: WorkflowStep, listener_runner: ThreadListenerRunner):
        self.step = step
        self.listener_runner = listener_runner

    def process(
        self,
        *,
        req: BoltRequest,
        resp: BoltResponse,
        # As this method is not supposed to be invoked by bolt-python users,
        # the naming conflict with the built-in one affects
        # only the internals of this method
        next: Callable[[], BoltResponse],
    ) -> Optional[BoltResponse]:

        if self.step.edit.matches(req=req, resp=resp):
            resp = self._run(self.step.edit, req, resp)
            if resp is not None:
                return resp
        elif self.step.save.matches(req=req, resp=resp):
            resp = self._run(self.step.save, req, resp)
            if resp is not None:
                return resp
        elif self.step.execute.matches(req=req, resp=resp):
            resp = self._run(self.step.execute, req, resp)
            if resp is not None:
                return resp

        return next()

    def _run(
        self,
        listener: Listener,
        req: BoltRequest,
        resp: BoltResponse,
    ) -> Optional[BoltResponse]:
        resp, next_was_not_called = listener.run_middleware(req=req, resp=resp)
        if next_was_not_called:
            return None

        return self.listener_runner.run(
            request=req,
            response=resp,
            listener_name=get_name_for_callable(listener.ack_function),
            listener=listener,
        )
