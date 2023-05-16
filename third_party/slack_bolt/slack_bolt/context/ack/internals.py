from typing import Optional, Union, Any, Dict, Sequence

from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block, Option, OptionGroup
from slack_sdk.models.views import View

from slack_bolt.error import BoltError
from slack_bolt.response import BoltResponse
from slack_bolt.util.utils import convert_to_dict_list, convert_to_dict


def _set_response(
    self: Any,
    text_or_whole_response: Union[str, dict] = "",
    blocks: Optional[Sequence[Union[dict, Block]]] = None,
    attachments: Optional[Sequence[Union[dict, Attachment]]] = None,
    unfurl_links: Optional[bool] = None,
    unfurl_media: Optional[bool] = None,
    response_type: Optional[str] = None,  # in_channel / ephemeral
    # block_suggestion / dialog_suggestion
    options: Optional[Sequence[Union[dict, Option]]] = None,
    option_groups: Optional[Sequence[Union[dict, OptionGroup]]] = None,
    # view_submission
    response_action: Optional[str] = None,
    errors: Optional[Union[Dict[str, str], Sequence[Dict[str, str]]]] = None,
    view: Optional[Union[dict, View]] = None,
) -> BoltResponse:
    if isinstance(text_or_whole_response, str):
        text: str = text_or_whole_response
        body = {"text": text}
        if response_type:
            body["response_type"] = response_type
        if unfurl_links is not None:
            body["unfurl_links"] = unfurl_links
        if unfurl_media is not None:
            body["unfurl_media"] = unfurl_media
        if attachments and len(attachments) > 0:
            body.update({"text": text, "attachments": convert_to_dict_list(attachments)})
            self.response = BoltResponse(status=200, body=body)
        elif blocks and len(blocks) > 0:
            body.update({"text": text, "blocks": convert_to_dict_list(blocks)})
            self.response = BoltResponse(status=200, body=body)
        elif options is not None:
            body = {"options": convert_to_dict_list(options)}
            self.response = BoltResponse(status=200, body=body)
        elif option_groups is not None:
            body = {"option_groups": convert_to_dict_list(option_groups)}
            self.response = BoltResponse(status=200, body=body)
        elif response_action:
            # These patterns are in response to view_submission requests
            if response_action == "errors":
                if errors:
                    self.response = BoltResponse(
                        status=200,
                        body={
                            "response_action": response_action,
                            "errors": convert_to_dict(errors),
                        },
                    )
                else:
                    raise ValueError("errors field is required for response_action: errors")
            else:
                body = {"response_action": response_action}
                if view:
                    body["view"] = convert_to_dict(view)
                self.response = BoltResponse(status=200, body=body)
        elif errors:
            # dialogs: errors without response_action
            body = {"errors": convert_to_dict_list(errors)}
            self.response = BoltResponse(status=200, body=body)
        else:
            if len(body) == 1 and "text" in body:
                self.response = BoltResponse(status=200, body=body["text"])
            else:
                self.response = BoltResponse(status=200, body=body)
        return self.response
    elif isinstance(text_or_whole_response, dict):
        body = text_or_whole_response
        if "attachments" in body:
            body["attachments"] = convert_to_dict_list(body["attachments"])
        if "blocks" in body:
            body["blocks"] = convert_to_dict_list(body["blocks"])
        if "options" in body:
            body["options"] = convert_to_dict_list(body["options"])
        if "option_groups" in body:
            body["option_groups"] = convert_to_dict_list(body["option_groups"])
        if "errors" in body:
            if body.get("response_action", "") == "errors":
                # modal
                body["errors"] = convert_to_dict(body["errors"])
            else:
                # dialog
                body["errors"] = convert_to_dict_list(body["errors"])
        if "view" in body:
            body["view"] = convert_to_dict(body["view"])
        # no modification for response_type, response_action here

        self.response = BoltResponse(status=200, body=body)
        return self.response
    else:
        raise BoltError(f"{text_or_whole_response} (type: {type(text_or_whole_response)}) is unsupported")
