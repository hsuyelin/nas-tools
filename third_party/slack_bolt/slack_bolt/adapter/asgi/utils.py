from typing import Iterable, Tuple, Union, Dict

ENCODING = "utf-8"  # should always be utf-8

scope_value_type = Union[str, bytes, Iterable[Tuple[bytes, bytes]]]

scope_type = Dict[str, scope_value_type]
