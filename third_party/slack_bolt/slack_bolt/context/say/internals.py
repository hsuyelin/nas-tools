from typing import Optional, Any


def _can_say(self: Any, channel: Optional[str]) -> bool:
    return hasattr(self, "client") and self.client is not None and (channel or self.channel) is not None
