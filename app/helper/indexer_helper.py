from os.path import join
import json
from base64 import b64decode
import threading

import log
from app.utils import StringUtils, ExceptionUtils
from app.utils.commons import singleton
from app.helper import DbHelper
from config import Config

@singleton
class IndexerHelper:

    _lock = None
    _builtiIndexers = None
    _custom_indexers = None
    _all_indexers = None
    _public_indexers = None

    def __init__(self):
        self._lock = threading.Lock()
        self.init_config()

    def stop_service(self):
        """
        清空缓存
        """
        self._builtiIndexers = None
        self._custom_indexers = None
        self._all_indexers = None
        self._public_indexers = None

    def init_config(self):
        """
        初始化相关配置
        """
        custom_indexers = self.get_custom_indexers()
        if isinstance(custom_indexers, list):
            self._custom_indexers = self.get_custom_indexers()
        elif isinstance(custom_indexers, dict):
            self._custom_indexers = [custom_indexers]
        else:
            self._custom_indexers = []

        if self._builtiIndexers:
            return

        builtiIndexers = self.get_builtin_indexers()
        if not isinstance(builtiIndexers, list):
            self._builtiIndexers = []
        elif isinstance(builtiIndexers, dict):
            self._builtiIndexers = [builtiIndexers]
        else:
            self._builtiIndexers = builtiIndexers

    def get_builtin_indexers(self):
        """
        获取所有内置站点
        """
        try:
            with open(join(Config().get_inner_config_path(), "sites.dat"), "r") as f:
                _indexers_json = b64decode(f.read())
                return json.loads(_indexers_json).get("indexer")
        except Exception as err:
            log.error(f"【Indexers】获取所有内置站点失败：{str(err)}")
            return []

    def get_custom_indexers(self):
        """
        获取自定义站点
        """
        try:
            for inexer in DbHelper().get_indexer_custom_site():
                _indexers_json = json.loads(inexer.INDEXER)
                return _indexers_json
        except Exception as err:
            log.error(f"【Indexers】获取自定义站点失败：{str(err)}")
            return []

    def init_all_indexers(self):
        """
        获取所有内置站点+自定义站点
        """
        with self._lock:
            self.init_config()
            self._all_indexers = self._builtiIndexers + self._custom_indexers

    def get_public_indexers(self):
        """
        获取公开站点(包含自定义站点)
        """
        with self._lock:
            self.init_config()
            self._public_indexers = []
            if self._builtiIndexers:
                self._public_indexers += self._builtiIndexers
            if self._custom_indexers:
                self._public_indexers += self._custom_indexers
            self._public_indexers = [item for item in self._public_indexers if item.get("public") is True]
        return self._public_indexers

    def get_indexer_info(self, url, public=False):
        """
        根据url获取指定indexer
        """
        self.init_all_indexers()
        for indexer in self._all_indexers:
            if StringUtils.url_equal(indexer.get("domain"), url):
                return indexer
        return None

    def get_indexer(self,
                    url,
                    siteid=None,
                    cookie=None,
                    name=None,
                    rule=None,
                    public=None,
                    proxy=False,
                    parser=None,
                    ua=None,
                    render=None,
                    language=None,
                    pri=None):
        if not url:
            return None
        self.init_all_indexers()
        if not self._all_indexers:
            return None
        for indexer in self._all_indexers:
            if not indexer.get("domain"):
                continue
            indexer_domain = indexer.get("domain")
            if StringUtils.url_equal(indexer.get("domain"), url):
                return IndexerConf(datas=indexer,
                                   siteid=siteid,
                                   cookie=cookie,
                                   name=name,
                                   rule=rule,
                                   public=public,
                                   proxy=proxy,
                                   parser=parser,
                                   ua=ua,
                                   render=render,
                                   builtin=True,
                                   language=language,
                                   pri=pri)
        return None


class IndexerConf(object):

    def __init__(self,
                 datas=None,
                 siteid=None,
                 cookie=None,
                 name=None,
                 rule=None,
                 public=None,
                 proxy=False,
                 parser=None,
                 ua=None,
                 render=None,
                 builtin=True,
                 language=None,
                 pri=None):
        if not datas:
            return
        # ID
        self.id = datas.get('id')
        # 站点ID
        self.siteid = siteid
        # 名称
        self.name = datas.get('name') if not name else name
        # 是否内置站点
        self.builtin = datas.get('builtin')
        # 域名
        self.domain = datas.get('domain')
        # 搜索
        self.search = datas.get('search', {})
        # 批量搜索，如果为空对象则表示不支持批量搜索
        self.batch = self.search.get("batch", {}) if builtin else {}
        # 解析器
        self.parser = parser if parser is not None else datas.get('parser')
        # 是否启用渲染
        self.render = render if render is not None else datas.get("render")
        # 浏览
        self.browse = datas.get('browse', {})
        # 种子过滤
        self.torrents = datas.get('torrents', {})
        # 分类
        self.category = datas.get('category', {})
        # Cookie
        self.cookie = cookie
        # User-Agent
        self.ua = ua
        # 过滤规则
        self.rule = rule
        # 是否公开站点
        self.public = datas.get('public') if not public else public
        # 是否使用代理
        self.proxy = datas.get('proxy') if not proxy else proxy
        # 仅支持的特定语种
        self.language = language
        # 索引器优先级
        self.pri = pri if pri else 0