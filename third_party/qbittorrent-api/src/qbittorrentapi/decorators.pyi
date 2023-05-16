from logging import Logger
from typing import Callable
from typing import Set
from typing import Text
from typing import Type
from typing import TypeVar

from qbittorrentapi.request import Request

logger: Logger

APIClassT = TypeVar("APIClassT", bound=Request)
APIReturnValueT = TypeVar("APIReturnValueT")

class alias:
    aliases: Set[Text]
    def __init__(self, *aliases: Text) -> None: ...
    def __call__(
        self, func: Callable[..., APIReturnValueT]
    ) -> Callable[..., APIReturnValueT]: ...

def aliased(aliased_class: Type[APIClassT]) -> Type[APIClassT]: ...
def login_required(
    func: Callable[..., APIReturnValueT]
) -> Callable[..., APIReturnValueT]: ...
def handle_hashes(
    func: Callable[..., APIReturnValueT]
) -> Callable[..., APIReturnValueT]: ...
def endpoint_introduced(
    version_introduced: Text,
    endpoint: Text,
) -> Callable[[Callable[..., APIReturnValueT]], Callable[..., APIReturnValueT]]: ...
def version_removed(
    version_obsoleted: Text,
    endpoint: Text,
) -> Callable[[Callable[..., APIReturnValueT]], Callable[..., APIReturnValueT]]: ...
def check_for_raise(client: Request, error_message: Text) -> None: ...
