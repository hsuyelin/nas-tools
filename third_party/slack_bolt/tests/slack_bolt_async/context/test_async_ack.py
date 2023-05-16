import pytest
from slack_sdk.models.blocks import PlainTextObject, DividerBlock
from slack_sdk.models.views import View

from slack_bolt import BoltResponse
from slack_bolt.context.ack.async_ack import AsyncAck


class TestAsyncAsyncAck:
    @pytest.mark.asyncio
    async def test_text(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(text="foo")
        assert (response.status, response.body) == (200, "foo")

    @pytest.mark.asyncio
    async def test_blocks(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(text="foo", blocks=[{"type": "divider"}])
        assert (response.status, response.body) == (
            200,
            '{"text": "foo", "blocks": [{"type": "divider"}]}',
        )

    @pytest.mark.asyncio
    async def test_unfurl_options(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(
            text="foo",
            blocks=[{"type": "divider"}],
            unfurl_links=True,
            unfurl_media=True,
        )
        assert (response.status, response.body) == (
            200,
            '{"text": "foo", "unfurl_links": true, "unfurl_media": true, "blocks": [{"type": "divider"}]}',
        )

    sample_attachments = [
        {
            "fallback": "Plain-text summary of the attachment.",
            "color": "#2eb886",
            "pretext": "Optional text that appears above the attachment block",
            "author_name": "Bobby Tables",
            "author_link": "http://flickr.com/bobby/",
            "author_icon": "http://flickr.com/icons/bobby.jpg",
            "title": "Slack API Documentation",
            "title_link": "https://api.slack.com/",
            "text": "Optional text that appears within the attachment",
            "fields": [{"title": "Priority", "value": "High", "short": False}],
            "image_url": "http://my-website.com/path/to/image.jpg",
            "thumb_url": "http://example.com/path/to/thumb.png",
            "footer": "Slack API",
            "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
            "ts": 123456789,
        }
    ]

    @pytest.mark.asyncio
    async def test_attachments(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(text="foo", attachments=self.sample_attachments)
        assert (response.status, response.body) == (
            200,
            '{"text": "foo", '
            '"attachments": [{"fallback": "Plain-text summary of the attachment.", "color": "#2eb886", "pretext": "Optional text that appears above the attachment block", "author_name": "Bobby Tables", "author_link": "http://flickr.com/bobby/", "author_icon": "http://flickr.com/icons/bobby.jpg", "title": "Slack API Documentation", "title_link": "https://api.slack.com/", "text": "Optional text that appears within the attachment", "fields": [{"title": "Priority", "value": "High", "short": false}], "image_url": "http://my-website.com/path/to/image.jpg", "thumb_url": "http://example.com/path/to/thumb.png", "footer": "Slack API", "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png", "ts": 123456789}]'
            "}",
        )

    sample_options = [{"text": {"type": "plain_text", "text": "Maru"}, "value": "maru"}]

    @pytest.mark.asyncio
    async def test_options(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(text="foo", options=self.sample_options)
        assert response.status == 200
        assert response.body == '{"options": [{"text": {"type": "plain_text", "text": "Maru"}, "value": "maru"}]}'

    sample_option_groups = [
        {
            "label": {"type": "plain_text", "text": "Group 1"},
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "1-1"},
                {"text": {"type": "plain_text", "text": "Option 2"}, "value": "1-2"},
            ],
        },
        {
            "label": {"type": "plain_text", "text": "Group 2"},
            "options": [
                {"text": {"type": "plain_text", "text": "Option 1"}, "value": "2-1"},
            ],
        },
    ]

    @pytest.mark.asyncio
    async def test_option_groups(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(text="foo", option_groups=self.sample_option_groups)
        assert response.status == 200
        assert response.body.startswith('{"option_groups":')

    @pytest.mark.asyncio
    async def test_response_type(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(text="foo", response_type="in_channel")
        assert (response.status, response.body) == (
            200,
            '{"text": "foo", "response_type": "in_channel"}',
        )

    @pytest.mark.asyncio
    async def test_dialog_errors(self):
        expected_body = '{"errors": [{"name": "loc_origin", "error": "Pickup Location must be longer than 3 characters"}]}'
        errors = [
            {
                "name": "loc_origin",
                "error": "Pickup Location must be longer than 3 characters",
            }
        ]

        ack = AsyncAck()
        response: BoltResponse = await ack(errors=errors)
        assert (response.status, response.body) == (200, expected_body)
        response: BoltResponse = await ack({"errors": errors})
        assert (response.status, response.body) == (200, expected_body)

    @pytest.mark.asyncio
    async def test_view_errors(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(
            response_action="errors",
            errors={
                "block_title": "Title is required",
                "block_description": "Description must be longer than 10 characters",
            },
        )
        assert (response.status, response.body) == (
            200,
            '{"response_action": "errors", '
            '"errors": {'
            '"block_title": "Title is required", '
            '"block_description": "Description must be longer than 10 characters"'
            "}"
            "}",
        )

    @pytest.mark.asyncio
    async def test_view_update(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(
            response_action="update",
            view={
                "type": "modal",
                "callbAsyncAck_id": "view-id",
                "title": {
                    "type": "plain_text",
                    "text": "My App",
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel",
                },
                "blocks": [{"type": "divider", "block_id": "b"}],
            },
        )
        assert (response.status, response.body) == (
            200,
            '{"response_action": "update", '
            '"view": {'
            '"type": "modal", '
            '"callbAsyncAck_id": "view-id", '
            '"title": {"type": "plain_text", "text": "My App"}, '
            '"close": {"type": "plain_text", "text": "Cancel"}, '
            '"blocks": [{"type": "divider", "block_id": "b"}]'
            "}"
            "}",
        )

    @pytest.mark.asyncio
    async def test_view_update_2(self):
        ack = AsyncAck()
        response: BoltResponse = await ack(
            response_action="update",
            view=View(
                type="modal",
                callback_id="view-id",
                title=PlainTextObject(text="My App"),
                close=PlainTextObject(text="Cancel"),
                blocks=[DividerBlock(block_id="b")],
            ),
        )
        assert (response.status, response.body) == (
            200,
            ""
            '{"response_action": "update", '
            '"view": {'
            '"blocks": [{"block_id": "b", "type": "divider"}], '
            '"callback_id": "view-id", '
            '"close": {"text": "Cancel", "type": "plain_text"}, '
            '"title": {"text": "My App", "type": "plain_text"}, '
            '"type": "modal"'
            "}"
            "}",
        )
