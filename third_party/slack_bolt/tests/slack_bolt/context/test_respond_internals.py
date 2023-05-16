from slack_sdk.models.blocks import DividerBlock

from slack_bolt.context.respond.internals import _build_message


class TestRespondInternals:
    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_build_message_empty(self):
        message = _build_message()
        assert message is not None

    def test_build_message_text(self):
        message = _build_message(text="Hello!")
        assert message is not None

    def test_build_message_blocks(self):
        message = _build_message(blocks=[{"type": "divider"}])
        assert message is not None

    def test_build_message_blocks2(self):
        message = _build_message(blocks=[DividerBlock(block_id="foo")])
        assert message is not None
        assert isinstance(message["blocks"][0], dict)
        assert message["blocks"][0]["block_id"] == "foo"

    def test_build_message_attachments(self):
        message = _build_message(attachments=[{}])
        assert message is not None

    def test_build_message_response_type(self):
        message = _build_message(response_type="in_channel")
        assert message is not None

    def test_build_message_replace_original(self):
        message = _build_message(replace_original=True)
        assert message is not None

    def test_build_message_delete_original(self):
        message = _build_message(delete_original=True)
        assert message is not None

    def test_build_message_unfurl_options(self):
        message = _build_message(text="Hi there!", unfurl_links=True, unfurl_media=True)
        assert message is not None
        assert message.get("unfurl_links") is True
        assert message.get("unfurl_media") is True
