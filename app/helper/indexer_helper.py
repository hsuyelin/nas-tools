from os.path import join
import json
from base64 import b64decode

import log
from app.utils import StringUtils, ExceptionUtils
from app.utils.commons import singleton
from app.helper import DbHelper
from config import Config

@singleton
class IndexerHelper:

    _private_indexers = []
    _indexers = []

    def __init__(self):
        self.init_config()

    def init_config(self):
        try:
            with open(join(Config().get_inner_config_path(), "sites.dat"), "r") as f:
                _indexers_json = b64decode(f.read())
                self._private_indexers = json.loads(_indexers_json).get("indexer")
        except Exception as err:
            ExceptionUtils.exception_traceback(err)

        try:
            for inexer in DbHelper().get_indexer_custom_site():
                self._indexers.append(json.loads(inexer.INDEXER))
        except Exception as err:
            ExceptionUtils.exception_traceback(err)

    def get_all_indexers(self):
        self.init_config()
        return self._indexers

    def get_public_indexers(self):
        """
        获取内置公开站点
        """
        try:
            with open(join(Config().get_inner_config_path(), "sites.dat"), "r") as f:
                _indexers_json = b64decode(f.read())
                _indexer_list = json.loads(_indexers_json).get("indexer")
                return [item for item in _indexer_list if item['public'] is True]
        except Exception as err:
            return []

    def get_indexer_info(self, url, public=False):
        """
        根据url获取指定indexer
        """
        for indexer in self._indexers:
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
        self.init_config()
        if not url:
            return None
        _all_indexers = self._indexers + self._private_indexers
        for indexer in _all_indexers:
            indexer_domain = indexer.get("domain")
            if not indexer.get("domain"):
                continue
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