import re
import json
import log
from app.utils import RequestUtils, StringUtils
from config import Config
from app.apis import MTeamApi

# 全局配置
mt_category_list = []

class MTSpider(object):
    _indexerid = None
    _domain = None
    _name = ""
    _proxy = None
    _cookie = None
    _ua = None
    _apikey = None
    _token = None
    _size = 100
    _searchurl = "%s/api/torrent/search"
    _detailurl = "%s/detail/%d"
    _categoryurl = "%s/api/torrent/categoryList"

    def __init__(self, indexer):
        self._indexerid = indexer.id
        self._domain = indexer.domain
        self._searchurl = self._searchurl % MTeamApi.parse_api_domain(self._domain)
        self._categoryurl = self._categoryurl % MTeamApi.parse_api_domain(self._domain)
        self._name = indexer.name
        if indexer.proxy:
            self._proxy = Config().get_proxies()
        self._ua = indexer.ua
        self._apikey = indexer.apikey
        self.init_config()
        # self.check_category_list()

    def init_config(self):
        self._size = Config().get_config('pt').get('site_search_result_num') or 100

    def check_category_list(self):
        global mt_category_list
        if len(mt_category_list) > 0:
            return
        if not self._apikey:
            log.warn(f"【INDEXER】{self._name} 未设置站点Api-Key，无法拉取分类")
            return
        res = RequestUtils(
            headers={
                'x-api-key': self._apikey,
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": f"{self._ua}",
                "Accept": "application/json"
            },
            proxies=self._proxy,
            timeout=30
        ).post_res(url=self._categoryurl)
        if res and res.status_code == 200:
            msg = res.json().get('message')
            if msg != "SUCCESS":
                log.warn(f"【INDEXER】{self._name} 拉取分类失败：{msg}")
                return
            results = res.json().get('data', {}).get("list") or []
            for result in results:
                mt_category_list.append(result.get('id'))
            log.info("【INDEXER】%s 拉取分类成功，获取分类：%d项" % (self._name, len(mt_category_list)))
        elif res is not None:
            log.warn(f"【INDEXER】{self._name} 拉取分类失败，错误码：{res.status_code}")
        else:
            log.warn(f"【INDEXER】{self._name} 拉取分类失败，无法连接 {self._categoryurl}")

    def search(self, keyword, page=0):
        if not self._apikey:
            log.warn(f"【INDEXER】{self._name} 未设置站点Api-Key，无法搜索")
            return True, []
        params = {
            "pageNumber": int(page) + 1,
            "pageSize": self._size,
            "keyword": keyword or "",
            "categories": [],
            "sources": [],
            "standards": [],
            "visible": 1,
            "mode": "normal"
        }
        res = RequestUtils(
            headers={
                'x-api-key': self._apikey,
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": self._ua,
                "Accept": "application/json"
            },
            proxies=self._proxy,
            timeout=30
        ).post_res(url=self._searchurl, json=params)
        torrents = []
        if res and res.status_code == 200:
            results = res.json().get('data', {}).get("data") or []
            for result in results:
                torrentid = int(result.get('id'))
                status = result.get('status')
                torrent = {
                    'indexer': self._indexerid,
                    'title': result.get('name'),
                    'description': result.get('smallDescr'),
                    'enclosure': "",  # 为了减少接口调用，种子连接在下载的时候查询
                    'pubdate': StringUtils.timestamp_to_date(result.get('lastModifiedDate')),
                    'size': result.get('size'),
                    'seeders': status.get('seeders'),
                    'peers': status.get('leechers'),
                    'grabs': status.get('timesCompleted'),
                    'downloadvolumefactor': 1.0,
                    'uploadvolumefactor': 1.0,
                    'page_url': self._detailurl % (StringUtils.get_base_url(self._domain), torrentid),  # 种子详情页
                    'imdbid': result.get('imdb')
                }
                discount = status.get('discount')

                """
                NORMAL:上传下载都1倍
                _2X_FREE:上傳乘以二倍，下載不計算流量。
                _2X_PERCENT_50:上傳乘以二倍，下載計算一半流量。
                _2X:上傳乘以二倍，下載計算正常流量。
                PERCENT_50:上傳計算正常流量，下載計算一半流量。
                PERCENT_30:上傳計算正常流量，下載計算該種子流量的30%。
                FREE:上傳計算正常流量，下載不計算流量。
                """
                if discount == "_2X_FREE":
                    torrent["downloadvolumefactor"] = 0.0
                    torrent["uploadvolumefactor"] = 2.0
                elif discount == "_2X_PERCENT_50":
                    torrent["downloadvolumefactor"] = 0.5
                    torrent["uploadvolumefactor"] = 2.0
                elif discount == "_2X":
                    torrent["downloadvolumefactor"] = 1.0
                    torrent["uploadvolumefactor"] = 2.0
                elif discount == "PERCENT_50":
                    torrent["downloadvolumefactor"] = 0.5
                    torrent["uploadvolumefactor"] = 1.0
                elif discount == "PERCENT_30":
                    torrent["downloadvolumefactor"] = 0.3
                    torrent["uploadvolumefactor"] = 1.0
                elif discount == "FREE":
                    torrent["downloadvolumefactor"] = 0
                    torrent["uploadvolumefactor"] = 1.0
                torrents.append(torrent)
        elif res is not None:
            log.warn(f"【INDEXER】{self._name} 搜索失败，错误码：{res.status_code}")
            return True, []
        else:
            log.warn(f"【INDEXER】{self._name} 搜索失败，无法连接 {self._searchurl}")
            return True, []
        return False, torrents
