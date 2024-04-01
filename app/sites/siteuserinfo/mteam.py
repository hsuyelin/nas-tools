# -*- coding: utf-8 -*-
import json
import base64

from urllib.parse import urljoin

from app.sites.siteuserinfo._base import _ISiteUserInfo, SITE_BASE_ORDER
from app.utils import RequestUtils, JsonUtils
from app.utils.types import SiteSchema
from config import Config


class MteamUserInfo(_ISiteUserInfo):
    schema = SiteSchema.Mteam
    order = SITE_BASE_ORDER + 15

    @classmethod
    def match(cls, html_text):
        return "authorities" in html_text

    def parse(self):
        """
        解析站点信息
        :return:
        """
        self._parse_favicon(self._index_html)
        if not self._parse_logged_in(self._index_html):
            return

        self._parse_site_page(self._index_html)
        self._parse_user_base_info(self._index_html)
        self._pase_unread_msgs()
        self._parse_user_traffic_info(self._index_html)
        self._parse_user_detail_info(self._index_html)

        self._parse_seeding_pages()
        self.seeding_info = json.dumps(self.seeding_info)

    def _parse_favicon(self, html_text):
        """
        解析站点favicon,返回base64 fav图标
        :param html_text:
        :return:
        """
        self._favicon_url = urljoin(self._base_url, '/favicon.ico')

        res = RequestUtils(cookies=self._site_cookie, session=self._session, timeout=60, headers=self._ua).get_res(
            url=self._favicon_url)
        if res:
            self.site_favicon = base64.b64encode(res.content).decode()

    def _parse_user_base_info(self, html_text):
        if not JsonUtils.is_valid_json(html_text):
            return

        json_data = json.loads(html_text)

        user_profile = self._get_page_content(self._base_url + '/api/member/profile', params={})
        user_profile = json.loads(user_profile)
        if user_profile.get('message') == 'SUCCESS' and json_data.get('data') is not None:
            userid = user_profile.get('data').get('id') or ''
            self.username = json_data.get('data').get('username') or ''
            self.bonus = json_data.get('data').get('memberCount').get('bonus') or ''
            self._torrent_seeding_page = '/api/member/getUserTorrentList'
            self._torrent_seeding_params = {"userid": userid, "type": "SEEDING", "pageNumber": 1, "pageSize": 25}

    def _parse_site_page(self, html_text):
        pass

    def _parse_user_detail_info(self, html_text):
        """
        解析用户额外信息，加入时间，等级
        :param html_text:
        :return:
        """
        role_dict = {
            '1': '小卒/User',
            '2': '捕頭/Power User',
            '3': '知縣/Elite User',
            '4': '通判/Crazy User',
            '5': '知州/Insane User',
            '6': '府丞/Veteran User',
            '7': '府尹/Extreme User',
            '8': '總督/Ultimate User',
            '9': '大臣/mTorrent Master'
        }
        if not JsonUtils.is_valid_json(html_text):
            return
        json_data = json.loads(html_text)
        if json_data.get('data') is not None:
            # 用户等级
            role = json_data.get('data').get('role') or ''
            self.user_level = role_dict.get(role, '其他')

            # 加入日期
            self.join_at = json_data.get('data').get('createdDate')

    def _parse_user_traffic_info(self, html_text):
        json_data = json.loads(html_text)
        if json_data.get('data') is not None:
            self.upload = int(json_data.get('data').get('memberCount').get('uploaded'))

            self.download = int(json_data.get('data').get('memberCount').get('downloaded'))

            self.ratio = json_data.get('data').get('memberCount').get('shareRate')

    def _parse_user_torrent_seeding_info(self, html_text, multi_page=False):

        if not JsonUtils.is_valid_json(html_text):
            return None

        json_data = json.loads(html_text)

        page_seeding = 0
        page_seeding_size = 0
        page_seeding_info = []
        next_page = None

        if json_data.get('data') is not None:
            page_seeding = len(json_data.get('data').get('data'))
            for data in json_data.get('data').get('data'):
                size = int(data.get('torrent').get('size'))
                seeders = data.get('torrent').get('status').get('seeders')

                page_seeding_size += size
                page_seeding_info.append([seeders, size])

            self.seeding += page_seeding
            self.seeding_size += page_seeding_size
            self.seeding_info.extend(page_seeding_info)

            page_num = int(json_data.get('data').get('pageNumber'))
            total_pages = int(json_data.get('data').get('totalPages'))

            next_page = page_num + 1
            self._torrent_seeding_params['pageNumber'] = next_page
            if next_page > total_pages:
                return None
        return next_page

    def _get_page_content(self, url, params=None, headers=None):
        """
        :param url: 网页地址
        :param params: post参数
        :param headers: 额外的请求头
        :return:
        """
        req_headers = None
        proxies = Config().get_proxies() if self._proxy else None
        if self._ua or headers or self._addition_headers:
            req_headers = {}
            if headers:
                req_headers.update(headers)

            if isinstance(self._ua, str):
                req_headers.update({
                    "User-Agent": f"{self._ua}"
                })
            else:
                req_headers.update(self._ua)

            if self._addition_headers:
                req_headers.update(self._addition_headers)

        params = json.dumps(params, separators=(',', ':'))
        res = RequestUtils(cookies=self._site_cookie,
                            session=self._session,
                            proxies=proxies,
                            headers=req_headers).post_res(url=url, data=params)
        if res is not None and res.status_code in (200, 500, 403):
            if "charset=utf-8" in res.text or "charset=UTF-8" in res.text:
                res.encoding = "UTF-8"
            else:
                res.encoding = res.apparent_encoding
            return res.text

        return ""

    def _parse_seeding_pages(self):
        if self._torrent_seeding_page:
            # 第一页
            next_page = self._parse_user_torrent_seeding_info(
                self._get_page_content(urljoin(self._base_url, self._torrent_seeding_page),
                                       self._torrent_seeding_params,
                                       self._torrent_seeding_headers))

            # 其他页处理
            while next_page:
                next_page = self._parse_user_torrent_seeding_info(
                    self._get_page_content(urljoin(self._base_url, self._torrent_seeding_page),
                                           self._torrent_seeding_params,
                                           self._torrent_seeding_headers),
                    multi_page=True)

    def _parse_message_unread_links(self, html_text, msg_links):
        return None

    def _parse_message_content(self, html_text):
        return None, None, None
