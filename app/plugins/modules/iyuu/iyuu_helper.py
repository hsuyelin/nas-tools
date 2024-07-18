import hashlib
import json
import time

from app.utils import RequestUtils
from app.utils.commons import singleton


@singleton
class IyuuHelper(object):
    _version = "8.2.0"
    _api_base = "https://dev.iyuu.cn"
    _sites = {}
    _token = None
    _sid_sha1 = None

    def __init__(self, token):
        self._token = token
        if self._token:
            self.init_config()

    def init_config(self):
        pass

    def __request_iyuu(self, url, method="get", params=None):
        """
        向IYUUApi发送请求
        """
        # 开始请求
        if method == "get":
            ret = RequestUtils(
                accept_type="application/json",
                headers={'token': self._token}
            ).get_res(f"{self._api_base + url}", params=params)
        else:
            ret = RequestUtils(
                accept_type="application/json",
                headers={'token': self._token}
            ).post_res(f"{self._api_base + url}", json=params)
        if ret:
            result = ret.json()
            if result.get('code') == 0:
                return result.get('data'), ""
            else:
                return None, f"请求IYUU失败，状态码：{result.get('ret')}，返回信息：{result.get('msg')}"
        elif ret is not None:
            return None, f"请求IYUU失败，状态码：{ret.status_code}，错误原因：{ret.reason}"
        else:
            return None, f"请求IYUU失败，未获取到返回信息"

    def get_torrent_url(self, sid):
        if not sid:
            return None, None
        if not self._sites:
            self._sites = self.__get_sites()
        if not self._sites.get(sid):
            return None, None
        site = self._sites.get(sid)
        return site.get('base_url'), site.get('download_page')

    def __get_sites(self):
        """
        返回支持辅种的全部站点
        :return: 站点列表、错误信息
        {
            "code": 0,
            "data": {
                "count": 85,
                "sites": [
                    {
                        "id": 1,
                        "site": "xxx",
                        "nickname": "朋友",
                        "base_url": "www.xxx.com",
                        "download_page": "download.php?id={}&passkey={passkey}",
                        "details_page": "details.php?id={}",
                        "reseed_check": "passkey",
                        "is_https": 2,
                        "cookie_required": 0
                    }
                ]
            },
            "msg": "ok"
        }
        """
        result, msg = self.__request_iyuu(url='/reseed/sites/index')
        if result:
            ret_sites = {}
            sites = result.get('sites') or []
            for site in sites:
                ret_sites[site.get('id')] = site
            return ret_sites
        else:
            print(msg)
            return {}

    def __report_existing(self):
        """
        汇报辅种的站点
        :return:
        """
        if not self._sites:
            self._sites = self.__get_sites()
        sid_list = list(self._sites.keys())
        result, msg = self.__request_iyuu(url='/reseed/sites/reportExisting',
                                          method='post',
                                          params={'sid_list': sid_list})
        if result:
            return result.get('sid_sha1')
        return None

    def get_seed_info(self, info_hashs: list):
        """
        返回info_hash对应的站点id、种子id
        {
            "code": 0,
            "data": {
                "7866fdafbcc5ad504c7750f2d4626dc03954c50a": {
                    "torrent": [
                        {
                            "sid": 32,
                            "torrent_id": 19537,
                            "info_hash": "93665ee3f41f1845c6628b105b2d236cc08b9826"
                        },
                        {
                            "sid": 14,
                            "torrent_id": 413945,
                            "info_hash": "9e2e41fba99d135db84585419703906ec710e241"
                        }
                    ]
                }
            },
            "msg": "ok"
        }
        """
        if not self._sid_sha1:
            self._sid_sha1 = self.__report_existing()
        info_hashs.sort()
        json_data = json.dumps(info_hashs, separators=(',', ':'), ensure_ascii=False)
        sha1 = self.get_sha1(json_data)
        result, msg = self.__request_iyuu(url='/reseed/index/index',
                                          method="post",
                                          params={
                                            'hash': json_data,
                                            'sha1': sha1,
                                            'sid_sha1': self._sid_sha1,
                                            'timestamp': int(time.time()),
                                            'version': self._version
                                        })
        return result, msg

    @staticmethod
    def get_sha1(json_str) -> str:
        return hashlib.sha1(json_str.encode('utf-8')).hexdigest()

    def get_auth_sites(self):
        """
        返回支持鉴权的站点列表
        [
			{
				"id": 2,
				"site": "pthome",
				"nickname": "铂金家",
				"bind_check": "passkey,uid",
				"reseed_check": "passkey"
			},

		]
        """
        result, msg = self.__request_iyuu(url='/reseed/sites/recommend')
        if result:
            return result.get('list') or []
        else:
            print(msg)
            return []

    def bind_site(self, site, passkey, uid):
        """
        绑定站点
        :param site: 站点名称
        :param passkey: passkey
        :param uid: 用户id
        :return: 状态码、错误信息
        """
        result, msg = self.__request_iyuu(url='/reseed/users/bind',
                                          method="post",
                                          params={
                                              "token": self._token,
                                              "site": site,
                                              "passkey": self.get_sha1(passkey),
                                              "id": uid
                                          })
        return result, msg
