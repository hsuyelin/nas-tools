"""A middleware processes request data and calls `next()` method
if the execution chain should continue running the following middleware.

Middleware can be used globally before all listener executions.
It's also possible to run a middleware only for a particular listener.
"""

# Don't add async module imports here
from .authorization import (
    SingleTeamAuthorization,
    MultiTeamsAuthorization,
)
from .custom_middleware import CustomMiddleware
from .ignoring_self_events import IgnoringSelfEvents
from .middleware import Middleware
from .request_verification import RequestVerification
from .ssl_check import SslCheck
from .url_verification import UrlVerification

builtin_middleware_classes = [
    SslCheck,
    RequestVerification,
    SingleTeamAuthorization,
    MultiTeamsAuthorization,
    IgnoringSelfEvents,
    UrlVerification,
]
for cls in builtin_middleware_classes:
    Middleware.register(cls)

__all__ = [
    "SingleTeamAuthorization",
    "MultiTeamsAuthorization",
    "CustomMiddleware",
    "IgnoringSelfEvents",
    "Middleware",
    "RequestVerification",
    "SslCheck",
    "UrlVerification",
    "builtin_middleware_classes",
]
