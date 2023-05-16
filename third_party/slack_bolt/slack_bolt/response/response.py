import json
from http.cookies import SimpleCookie
from typing import Union, Dict, Optional, Sequence


class BoltResponse:
    status: int
    body: str
    headers: Dict[str, Sequence[str]]

    def __init__(
        self,
        *,
        status: int,
        body: Union[str, dict] = "",
        headers: Optional[Dict[str, Union[str, Sequence[str]]]] = None,
    ):
        """The response from a Bolt app.

        Args:
            status: HTTP status code
            body: The response body (dict and str are supported)
            headers: The response headers.
        """
        self.status: int = status
        self.body: str = json.dumps(body) if isinstance(body, dict) else body
        self.headers: Dict[str, Sequence[str]] = {}
        if headers is not None:
            for name, value in headers.items():
                if value is None:
                    continue
                if isinstance(value, list):
                    self.headers[name.lower()] = value
                elif isinstance(value, set):
                    self.headers[name.lower()] = list(value)
                else:
                    self.headers[name.lower()] = [str(value)]

        if "content-type" not in self.headers.keys():
            if self.body and self.body.startswith("{"):
                self.headers["content-type"] = ["application/json;charset=utf-8"]
            else:
                self.headers["content-type"] = ["text/plain;charset=utf-8"]

    def first_headers(self) -> Dict[str, str]:
        return {k: list(v)[0] for k, v in self.headers.items()}

    def first_headers_without_set_cookie(self) -> Dict[str, str]:
        return {k: list(v)[0] for k, v in self.headers.items() if k != "set-cookie"}

    def cookies(self) -> Sequence[SimpleCookie]:
        header_values = self.headers.get("set-cookie", [])
        return [self._to_simple_cookie(v) for v in header_values]

    @staticmethod
    def _to_simple_cookie(header_value: str) -> SimpleCookie:
        c = SimpleCookie()
        c.load(header_value)
        return c
