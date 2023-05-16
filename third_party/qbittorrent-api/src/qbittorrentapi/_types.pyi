from typing import IO
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Sequence
from typing import Text
from typing import Tuple
from typing import Union

from qbittorrentapi.definitions import Dictionary

KwargsT = Any
# Type to define JSON
JsonValueT = Union[
    None,
    int,
    Text,
    bool,
    Sequence[JsonValueT],
    Mapping[Text, JsonValueT],
]
JsonDictionaryT = Dictionary[Text, JsonValueT]
# Type for inputs to build a Dictionary
DictInputT = Mapping[Text, JsonValueT]
# Type for inputs to build a List
ListInputT = Iterable[Mapping[Text, JsonValueT]]
# Type for `files` in requests.get()/post()
FilesToSendT = Mapping[Text, IO[bytes] | Tuple[Text, IO[bytes]]]
