from functools import wraps
from logging import getLogger

from qbittorrentapi._version_support import v
from qbittorrentapi.exceptions import HTTP403Error

logger = getLogger(__name__)


class alias(object):
    """
    Alias class that can be used as a decorator for making methods callable
    through other names (or "aliases").
    Note: This decorator must be used inside an @aliased -decorated class.
    For example, if you want to make the method shout() be also callable as
    yell() and scream(), you can use alias like this:

        @alias('yell', 'scream')
        def shout(message):
            # ....
    """

    def __init__(self, *aliases):
        self.aliases = set(aliases)

    def __call__(self, func):
        """
        Method call wrapper.

        As this decorator has arguments, this method will only be called
        once as a part of the decoration process, receiving only one
        argument: the decorated function ('f'). As a result of this kind
        of decorator, this method must return the callable that will
        wrap the decorated function.
        """
        func._aliases = self.aliases
        return func


def aliased(aliased_class):
    """
    Decorator function that *must* be used in combination with @alias decorator. This
    class will make the magic happen!

    @aliased classes will have their aliased method (via @alias) actually aliased.
    This method simply iterates over the member attributes of 'aliased_class'
    seeking for those which have an '_aliases' attribute and then defines new
    members in the class using those aliases as mere pointer functions to the
    original ones.

    Usage:
        @aliased
        class MyClass(object):
            @alias('coolMethod', 'myKinkyMethod')
            def boring_method():
                # ...

        i = MyClass()
        i.coolMethod() # equivalent to i.myKinkyMethod() and i.boring_method()
    """
    original_methods = aliased_class.__dict__.copy()
    for method in original_methods.values():
        if hasattr(method, "_aliases"):
            # Add the aliases for 'method', but don't override any
            # previously-defined attribute of 'aliased_class'
            # noinspection PyProtectedMember
            for method_alias in method._aliases - set(original_methods):
                setattr(aliased_class, method_alias, method)
    return aliased_class


def login_required(func):
    """Ensure client is logged in when calling API methods."""

    def get_requests_kwargs(**kwargs):
        """Extract kwargs for performing transparent qBittorrent login."""
        return {
            "requests_args": kwargs.get("requests_args"),
            "requests_params": kwargs.get("requests_params"),
            "headers": kwargs.get("headers"),
        }

    @wraps(func)
    def wrapper(client, *args, **kwargs):
        """
        Attempt API call; 403 is returned if the login is expired or the user is banned.

        Attempt a login and if successful try the API call a final time.
        """
        try:
            return func(client, *args, **kwargs)
        except HTTP403Error:
            logger.debug("Login may have expired...attempting new login")
            client.auth_log_in(**get_requests_kwargs(**kwargs))
            return func(client, *args, **kwargs)

    return wrapper


def handle_hashes(func):
    """
    Normalize torrent hash arguments.

    Initial implementations of this client used 'hash' and 'hashes' as function
    arguments for torrent hashes. Since 'hash' collides with an internal python name,
    all arguments were updated to 'torrent_hash' or 'torrent_hashes'. Since both
    versions of argument names remain respected, this decorator normalizes torrent hash
    arguments into either 'torrent_hash' or 'torrent_hashes'.
    """

    @wraps(func)
    def wrapper(client, *args, **kwargs):
        if "torrent_hash" not in kwargs and "hash" in kwargs:
            kwargs["torrent_hash"] = kwargs.pop("hash")
        elif "torrent_hashes" not in kwargs and "hashes" in kwargs:
            kwargs["torrent_hashes"] = kwargs.pop("hashes")
        return func(client, *args, **kwargs)

    return wrapper


def check_for_raise(client, error_message):
    """For any nonexistent endpoint, log the error and conditionally raise an
    exception."""
    logger.debug(error_message)
    if client._RAISE_UNIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS:
        raise NotImplementedError(error_message)


def endpoint_introduced(version_introduced, endpoint):
    """
    Prevent hitting an endpoint if the connected qBittorrent version doesn't support it.

    :param version_introduced: version endpoint was made available
    :param endpoint: API endpoint (e.g. /torrents/categories)
    """

    def _inner(func):
        @wraps(func)
        def wrapper(client, *args, **kwargs):
            # if the endpoint doesn't exist, return None or log an error / raise an Exception
            if v(client.app_web_api_version()) < v(version_introduced):
                error_message = (
                    "ERROR: Endpoint '%s' is Not Implemented in this version of qBittorrent. "
                    "This endpoint is available starting in Web API v%s."
                    % (endpoint, version_introduced)
                )
                check_for_raise(client=client, error_message=error_message)
                return None

            # send request to endpoint
            return func(client, *args, **kwargs)

        return wrapper

    return _inner


def version_removed(version_obsoleted, endpoint):
    """
    Prevent hitting an endpoint that was removed in a version older than the connected
    qBittorrent.

    :param version_obsoleted: the Web API version the endpoint was removed
    :param endpoint: name of the removed endpoint
    """

    def _inner(func):
        @wraps(func)
        def wrapper(client, *args, **kwargs):
            # if the endpoint doesn't exist, return None or log an error / raise an Exception
            if v(client.app_web_api_version()) >= v(version_obsoleted):
                error_message = (
                    "ERROR: Endpoint '%s' is Not Implemented. "
                    "This endpoint was removed in Web API v%s."
                    % (endpoint, version_obsoleted)
                )
                check_for_raise(client=client, error_message=error_message)
                return None

            # send request to endpoint
            return func(client, *args, **kwargs)

        return wrapper

    return _inner
