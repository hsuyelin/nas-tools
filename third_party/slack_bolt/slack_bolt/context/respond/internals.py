from typing import Optional, Dict, Union, Any, Sequence

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block

from slack_bolt.util.utils import convert_to_dict_list


def _build_message(
    text: str = "",
    blocks: Optional[Sequence[Union[dict, Block]]] = None,
    attachments: Optional[Sequence[Union[dict, Attachment]]] = None,
    response_type: Optional[str] = None,
    replace_original: Optional[bool] = None,
    delete_original: Optional[bool] = None,
    unfurl_links: Optional[bool] = None,
    unfurl_media: Optional[bool] = None,
    thread_ts: Optional[str] = None,
) -> Dict[str, Any]:
    message = {"text": text}
    if blocks is not None and len(blocks) > 0:
        message["blocks"] = convert_to_dict_list(blocks)
    if attachments is not None and len(attachments) > 0:
        message["attachments"] = convert_to_dict_list(attachments)
    if response_type is not None:
        message["response_type"] = response_type
    if replace_original is not None:
        message["replace_original"] = replace_original
    if delete_original is not None:
        message["delete_original"] = delete_original
    if unfurl_links is not None:
        message["unfurl_links"] = unfurl_links
    if unfurl_media is not None:
        message["unfurl_media"] = unfurl_media
    if thread_ts is not None:
        message["thread_ts"] = thread_ts
    return message
