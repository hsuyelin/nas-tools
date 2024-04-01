import json
from threading import Lock

import requests

from app.message.client._base import _IMessageClient
from app.utils import ExceptionUtils
from config import Config

lock = Lock()


class Webhook(_IMessageClient):
    schema = "webhook"

    _client_config = {}
    _domain = None
    _url = None
    _method = None
    _query_params = None
    _json_body = None
    _token = None

    def __init__(self, config):
        self._config = Config()
        self._client_config = config
        self.init_config()
    
    @classmethod
    def __parse_json(cls, json_str, attr_name):
        json_str = json_str.strip()
        if not json_str:
            return None
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"{attr_name} Json解析失败：{json_str}") from e

    def init_config(self):
        if self._client_config:
            self._url = self._client_config.get("url")
            self._method = self._client_config.get("method")
            self._query_params = self.__parse_json(self._client_config.get("query_params"), 'query_params')
            self._json_body = self.__parse_json(self._client_config.get("json_body"), 'json_body')
            self._token = self._client_config.get("token")

    @classmethod
    def match(cls, ctype):
        return True if ctype == cls.schema else False

    def send_msg(self, title, text="", image="", url="", user_id=""):
        """
        发送web请求
        :param title: 消息标题
        :param text: 消息内容
        :param image: 消息图片地址
        :param url: 点击消息转转的URL
        :param user_id: 用户ID，如有则只发消息给该用户
        :user_id: 发送消息的目标用户ID，为空则发给管理员
        """
        if not title and not text:
            return False, "标题和内容不能同时为空"
        if not self._url:
            return False, "url参数未配置"
        if not self._method:
            return False, "method参数未配置"
        try:
            media_data = {
                'title': title,
                'text': text,
                'image': image,
                'url': url,
                'user_id': user_id
            }
            query_params = self._query_params.copy() if self._query_params else {}
            json_body = self._json_body.copy() if self._json_body else {}
            if self._method == 'GET':
                query_params.update(media_data)
            else:
                json_body.update(media_data)
            return self.__send_request(query_params, json_body)

        except Exception as msg_e:
            ExceptionUtils.exception_traceback(msg_e)
            return False, str(msg_e)

    def send_list_msg(self, medias: list, user_id="", title="", **kwargs):
        """
        发送列表类消息
        """
        if not title:
            return False, "title为空"
        if not medias or not isinstance(medias, list):
            return False, "medias错误"
        if not self._url:
            return False, "url参数未配置"
        if not self._method:
            return False, "method参数未配置"
        if self._method == 'GET':
            return False, "GET不支持发送发送列表类消息"
        try:
            medias_data = [{
                'title': media.get_title_string(),
                'url': media.get_detail_url(),
                'type': media.get_type_string(),
                'vote': media.get_vote_string()
            } for media in medias]

            query_params = self._query_params.copy() if self._query_params else {}
            json_body = self._json_body.copy() if self._json_body else {}
            json_body.update({
                'title': title,
                'user_id': title,
                'medias': medias_data,
            })
            return self.__send_request(query_params, json_body)
        except Exception as msg_e:
            ExceptionUtils.exception_traceback(msg_e)
            return False, str(msg_e)

    def __send_request(self, query_params, json_body):
        """
        发送消息请求
        """
        response = requests.request(self._method,
                                    self._url,
                                    params=query_params,
                                    json=json_body,
                                    headers=self.header)
        if not response:
            return False, "未获取到返回信息"
        if 200 <= response.status_code <= 299:
            return True, ""
        else:
            return False, f"请求失败：{response.status_code}"

    @property
    def header(self):
        r = {"Content-Type": "application/json"}
        if self._token:
            r['Authorization'] = self._token
        return r
