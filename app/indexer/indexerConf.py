import json

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
                 apikey=None,
                 render=None,
                 builtin=True,
                 language=None,
                 pri=None):
        if not datas:
            return None
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
        # Api-Key
        self.apikey = apikey
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

    def to_dict(self):
        return {
            "id": self.id or "",
            "siteid": self.siteid or "",
            "name": self.name or "",
            "builtin": self.builtin or True,
            "domain": self.domain or "",
            "search": self.search or "",
            "batch": self.batch or {},
            "parser": self.parser or "",
            "render": self.render or False,
            "browse": self.browse or {},
            "torrents": self.torrents or {},
            "category": self.category or {},
            "cookie": self.cookie or "",
            "ua": self.ua or "",
            "apikey": self.apikey or "",
            "rule": self.rule or "",
            "public": self.public or False,
            "proxy": self.proxy or "",
            "pri": self.pri or 0
        }

    def to_dict_str(self, ensure_ascii=False, formatted=True):
        if formatted:
            return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=4)
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)
