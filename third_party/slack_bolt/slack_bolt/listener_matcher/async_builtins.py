# pytype: skip-file
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse
from .async_listener_matcher import AsyncListenerMatcher
from .builtins import BuiltinListenerMatcher
from ..kwargs_injection.async_utils import build_async_required_kwargs


class AsyncBuiltinListenerMatcher(BuiltinListenerMatcher, AsyncListenerMatcher):
    async def async_matches(self, req: AsyncBoltRequest, resp: BoltResponse) -> bool:
        return await self.func(
            **build_async_required_kwargs(
                logger=self.logger,
                required_arg_names=self.arg_names,
                request=req,
                response=resp,
                this_func=self.func,
            )
        )
