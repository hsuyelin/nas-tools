from typing import Optional, Union, Dict, Sequence

from slack_sdk.models.metadata import Metadata

from slack_bolt.context.say.internals import _can_say
from slack_bolt.util.utils import create_copy
from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse


class AsyncSay:
    client: Optional[AsyncWebClient]
    channel: Optional[str]

    def __init__(
        self,
        client: Optional[AsyncWebClient],
        channel: Optional[str],
    ):
        self.client = client
        self.channel = channel

    async def __call__(
        self,
        text: Union[str, dict] = "",
        blocks: Optional[Sequence[Union[Dict, Block]]] = None,
        attachments: Optional[Sequence[Union[Dict, Attachment]]] = None,
        channel: Optional[str] = None,
        as_user: Optional[bool] = None,
        thread_ts: Optional[str] = None,
        reply_broadcast: Optional[bool] = None,
        unfurl_links: Optional[bool] = None,
        unfurl_media: Optional[bool] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        username: Optional[str] = None,
        mrkdwn: Optional[bool] = None,
        link_names: Optional[bool] = None,
        parse: Optional[str] = None,  # none, full
        metadata: Optional[Union[Dict, Metadata]] = None,
        **kwargs,
    ) -> AsyncSlackResponse:
        if _can_say(self, channel):
            text_or_whole_response: Union[str, dict] = text
            if isinstance(text_or_whole_response, str):
                text = text_or_whole_response
                return await self.client.chat_postMessage(
                    channel=channel or self.channel,
                    text=text,
                    blocks=blocks,
                    attachments=attachments,
                    as_user=as_user,
                    thread_ts=thread_ts,
                    reply_broadcast=reply_broadcast,
                    unfurl_links=unfurl_links,
                    unfurl_media=unfurl_media,
                    icon_emoji=icon_emoji,
                    icon_url=icon_url,
                    username=username,
                    mrkdwn=mrkdwn,
                    link_names=link_names,
                    parse=parse,
                    metadata=metadata,
                    **kwargs,
                )
            elif isinstance(text_or_whole_response, dict):
                message: dict = create_copy(text_or_whole_response)
                if "channel" not in message:
                    message["channel"] = channel or self.channel
                return await self.client.chat_postMessage(**message)
            else:
                raise ValueError(f"The arg is unexpected type ({type(text_or_whole_response)})")
        else:
            raise ValueError("say without channel_id here is unsupported")
