import sys
from typing import Set

import pytest
from slack_sdk.models import JsonObject

from slack_bolt.error import BoltError
from slack_bolt.util.utils import convert_to_dict, get_boot_message
from tests.utils import remove_os_env_temporarily, restore_os_env


class Data:
    def __init__(self, name: str):
        self.name = name


class SerializableData(JsonObject):
    @property
    def attributes(self) -> Set[str]:
        return {"name"}

    def __init__(self, name: str):
        self.name = name


class TestUtil:
    def setup_method(self):
        self.old_os_env = remove_os_env_temporarily()

    def teardown_method(self):
        restore_os_env(self.old_os_env)

    def test_convert_to_dict(self):
        assert convert_to_dict({"foo": "bar"}) == {"foo": "bar"}
        assert convert_to_dict(SerializableData("baz")) == {"name": "baz"}

    def test_convert_to_dict_errors(self):
        with pytest.raises(BoltError):
            convert_to_dict(None)
        with pytest.raises(BoltError):
            convert_to_dict(123)
        with pytest.raises(BoltError):
            convert_to_dict("test")
        with pytest.raises(BoltError):
            convert_to_dict(Data("baz"))

    def test_get_boot_message(self):
        assert get_boot_message() == "⚡️ Bolt app is running!"
        assert get_boot_message(development_server=True) == "⚡️ Bolt app is running! (development server)"

    def test_get_boot_message_win32(self):
        sys_platform_backup = sys.platform
        try:
            sys.platform = "win32"
            assert get_boot_message() == "Bolt app is running!"
        finally:
            sys.platform = sys_platform_backup
