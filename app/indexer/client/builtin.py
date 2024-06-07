import copy
import datetime
import time

import log
from app.conf import SystemConfig
from app.helper import ProgressHelper, ChromeHelper, DbHelper
from app.indexer.client._base import _IIndexClient
from app.indexer.client._render_spider import RenderSpider
from app.indexer.client._spider import TorrentSpider
from app.indexer.client._tnode import TNodeSpider
from app.indexer.client._mt_spider import MTSpider
from app.indexer.client._torrentleech import TorrentLeech
from app.indexer.client._plugins import PluginsSpider
from app.sites import Sites
from app.utils import StringUtils
from app.utils.types import SearchType, IndexerType, ProgressKey, SystemConfigKey
from config import Config
from web.backend.pro_user import ProUser

class BuiltinIndexer(_IIndexClient):
    # 索引器ID
    client_id = "builtin"
    # 索引器类型
    client_type = IndexerType.BUILTIN
    # 索引器名称
    client_name = IndexerType.BUILTIN.value

    # 私有属性
    _client_config = {}
    _show_more_sites = False
    progress = None
    sites = None
    dbhelper = None
    user = None
    chromehelper = None
    systemconfig = None

    def __init__(self, config=None):
        super().__init__()
        self._client_config = config or {}
        self.init_config()

    def init_config(self):
        self.sites = Sites()
        self.progress = ProgressHelper()
        self.dbhelper = DbHelper()
        self.user = ProUser()
        self.chromehelper = ChromeHelper()
        self.systemconfig = SystemConfig()
        self._show_more_sites = Config().get_config("laboratory").get('show_more_sites')

    @classmethod
    def match(cls, ctype):
        return True if ctype in [cls.client_id, cls.client_type, cls.client_name] else False

    def get_type(self):
        return self.client_type

    def get_status(self):
        """
        检查连通性
        :return: True、False
        """
        return True

    def get_indexer(self, url):
        """
        获取单个索引器配置
        """
        # 检查浏览器状态
        chrome_ok = self.chromehelper.get_status()
        site = self.sites.get_sites(siteurl=url)
        if site:
            return self.user.get_indexer(url=url,
                                         siteid=site.get("id"),
                                         cookie=site.get("cookie"),
                                         ua=site.get("ua"),
                                         apikey=site.get("apikey"),
                                         name=site.get("name"),
                                         rule=site.get("rule"),
                                         pri=site.get('pri'),
                                         public=False,
                                         proxy=site.get("proxy"),
                                         render=False if not chrome_ok else site.get("chrome"))
        return None

    def get_indexers(self, check=True, public=True):
        ret_indexers = []
        _indexer_domains = []
        # 选中站点配置
        indexer_sites = self.systemconfig.get(SystemConfigKey.UserIndexerSites) or []
        # 检查浏览器状态
        chrome_ok = self.chromehelper.get_status()
        # 私有站点
        for site in self.sites.get_sites():
            url = site.get("signurl") or site.get("rssurl")
            cookie = site.get("cookie")
            apikey = site.get("apikey")
            if not url or (not apikey and not cookie):
                continue
            render = False if not chrome_ok else site.get("chrome")
            indexer = self.user.get_indexer(url=url,
                                            siteid=site.get("id"),
                                            cookie=cookie,
                                            ua=site.get("ua"),
                                            apikey=apikey,
                                            name=site.get("name"),
                                            rule=site.get("rule"),
                                            pri=site.get('pri'),
                                            public=False,
                                            proxy=site.get("proxy"),
                                            render=render)
            if indexer:
                if check and (not indexer_sites or indexer.id not in indexer_sites):
                    continue
                if indexer.domain not in _indexer_domains:
                    _indexer_domains.append(indexer.domain)
                    indexer.name = site.get("name")
                    ret_indexers.append(indexer)
        # 公开站点
        if public and self._show_more_sites:
            for site_url in self.user.get_public_sites():
                indexer = self.user.get_indexer(url=site_url)
                if indexer:
                    if check and (not indexer_sites or indexer.id not in indexer_sites):
                        continue
                    if indexer.domain not in _indexer_domains:
                        _indexer_domains.append(indexer.domain)
                        ret_indexers.append(indexer)
        # 获取插件站点
        if PluginsSpider().sites():
            for indexer in PluginsSpider().sites():
                if indexer:
                    if check and (not indexer_sites or indexer.id not in indexer_sites):
                        continue
                    if indexer.domain not in _indexer_domains:
                        _indexer_domains.append(indexer.domain)
                        ret_indexers.append(indexer)
        return ret_indexers

    def search(self, order_seq,
               indexer,
               key_word,
               filter_args: dict,
               match_media,
               in_from: SearchType):
        """
        根据关键字多线程搜索
        """
        if not indexer or not key_word:
            return None
        # 站点流控
        if self.sites.check_ratelimit(indexer.siteid):
            self.progress.update(ptype=ProgressKey.Search, text=f"{indexer.name} 触发站点流控，跳过 ...")
            return []
        # fix 共用同一个dict时会导致某个站点的更新全局全效
        if filter_args is None:
            _filter_args = {}
        else:
            _filter_args = copy.deepcopy(filter_args)
        # 不在设定搜索范围的站点过滤掉
        if _filter_args.get("site") and indexer.name not in _filter_args.get("site"):
            return []
        # 搜索条件没有过滤规则时，使用站点的过滤规则
        if not _filter_args.get("rule") and indexer.rule:
            _filter_args.update({"rule": indexer.rule})
        # 计算耗时
        start_time = datetime.datetime.now()

        log.info(f"【{self.client_name}】开始搜索Indexer：{indexer.name} ...")
        # 特殊符号处理
        search_word = StringUtils.handler_special_chars(text=key_word,
                                                        replace_word=" ",
                                                        allow_space=True)
        # 避免对英文站搜索中文
        if indexer.language == "en" and StringUtils.is_chinese(search_word):
            log.warn(f"【{self.client_name}】{indexer.name} 无法使用中文名搜索")
            return []
        # 开始索引
        result_array = []
        try:
            if 'm-team' in indexer.domain:
                error_flag, result_array = MTSpider(indexer).search(keyword=search_word)
            elif indexer.parser == "TNodeSpider":
                error_flag, result_array = TNodeSpider(indexer).search(keyword=search_word)
            elif indexer.parser == "RenderSpider":
                error_flag, result_array = RenderSpider(indexer).search(
                    keyword=search_word,
                    mtype=match_media.type if match_media and match_media.tmdb_info else None)
            elif indexer.parser == "TorrentLeech":
                error_flag, result_array = TorrentLeech(indexer).search(keyword=search_word)
            else:
                if PluginsSpider().status(indexer=indexer):
                    error_flag, result_array = PluginsSpider().search(keyword=search_word, indexer=indexer)
                else:
                    error_flag, result_array = self.__spider_search(
                        keyword=search_word,
                        indexer=indexer,
                        mtype=match_media.type if match_media and match_media.tmdb_info else None)
        except Exception as err:
            error_flag = True
            print(str(err))

        # 索引花费的时间
        seconds = round((datetime.datetime.now() - start_time).seconds, 1)
        # 索引统计
        self.dbhelper.insert_indexer_statistics(indexer=indexer.name,
                                                itype=self.client_id,
                                                seconds=seconds,
                                                result='N' if error_flag else 'Y')
        # 返回结果
        if len(result_array) == 0:
            log.warn(f"【{self.client_name}】{indexer.name} 未搜索到数据")
            # 更新进度
            self.progress.update(ptype=ProgressKey.Search, text=f"{indexer.name} 未搜索到数据")
            return []
        else:
            log.warn(f"【{self.client_name}】{indexer.name} 返回数据：{len(result_array)}")
            # 更新进度
            self.progress.update(ptype=ProgressKey.Search, text=f"{indexer.name} 返回 {len(result_array)} 条数据")
            # 过滤
            return self.filter_search_results(result_array=result_array,
                                              order_seq=order_seq,
                                              indexer=indexer,
                                              filter_args=_filter_args,
                                              match_media=match_media,
                                              start_time=start_time)

    def list(self, url, page=0, keyword=None):
        """
        根据站点ID搜索站点首页资源
        """
        if not url:
            return []
        indexer = self.get_indexer(url)
        if not indexer:
            return []

        # 计算耗时
        start_time = datetime.datetime.now()

        if 'm-team' in indexer.domain:
            error_flag, result_array = MTSpider(indexer).search(keyword=keyword, page=page)
        elif indexer.parser == "RenderSpider":
            error_flag, result_array = RenderSpider(indexer).search(keyword=keyword,
                                                                    page=page)
        elif indexer.parser == "TNodeSpider":
            error_flag, result_array = TNodeSpider(indexer).search(keyword=keyword,
                                                                   page=page)
        elif indexer.parser == "TorrentLeech":
            error_flag, result_array = TorrentLeech(indexer).search(keyword=keyword,
                                                                    page=page)
        else:   
            if PluginsSpider().status(indexer=indexer):
                error_flag, result_array = PluginsSpider().search(keyword=keyword, 
                                                                  indexer=indexer, 
                                                                  page=page)

            else:
                error_flag, result_array = self.__spider_search(indexer=indexer,
                                                                page=page,
                                                                keyword=keyword)
        # 索引花费的时间
        seconds = round((datetime.datetime.now() - start_time).seconds, 1)

        # 索引统计
        self.dbhelper.insert_indexer_statistics(indexer=indexer.name,
                                                itype=self.client_id,
                                                seconds=seconds,
                                                result='N' if error_flag else 'Y')
        return result_array

    @staticmethod
    def __spider_search(indexer, keyword=None, page=None, mtype=None, timeout=30):
        """
        根据关键字搜索单个站点
        :param: indexer: 站点配置
        :param: keyword: 关键字
        :param: page: 页码
        :param: mtype: 媒体类型
        :param: timeout: 超时时间
        :return: 是否发生错误, 种子列表
        """
        spider = TorrentSpider()
        spider.setparam(indexer=indexer,
                        keyword=keyword,
                        page=page,
                        mtype=mtype)
        spider.start()
        # 循环判断是否获取到数据
        sleep_count = 0
        while not spider.is_complete:
            sleep_count += 1
            time.sleep(1)
            if sleep_count > timeout:
                break
        # 是否发生错误
        result_flag = spider.is_error
        # 种子列表
        result_array = spider.torrents_info_array.copy()
        # 重置状态
        spider.torrents_info_array.clear()

        return result_flag, result_array
