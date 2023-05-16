"""A listener matcher is a simplified version of listener middleware.
A listener matcher function returns bool value instead of `next()` method invocation inside.
This interface enables developers to utilize simple predicate functions for additional listener conditions.
"""
# Don't add async module imports here
from .custom_listener_matcher import CustomListenerMatcher
from .listener_matcher import ListenerMatcher

builtin_listener_matcher_classes = [
    CustomListenerMatcher,
]
for cls in builtin_listener_matcher_classes:
    ListenerMatcher.register(cls)

__all__ = [
    "CustomListenerMatcher",
    "ListenerMatcher",
    "builtin_listener_matcher_classes",
]
