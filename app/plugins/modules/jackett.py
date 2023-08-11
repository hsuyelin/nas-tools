import requests
import xml.dom.minidom
from jinja2 import Template

import log

from app.utils import RequestUtils
from app.helper import IndexerConf
from app.utils import ExceptionUtils, DomUtils

from app.plugins.modules._base import _IPluginModule
from config import Config

class Jackett(_IPluginModule):
    # 插件名称
    module_name = "Jackett"
    # 插件描述
    module_desc = "让内荐索引器支持检索Jackett站点资源"
    # 插件图标
    module_icon = "jackett.png"
    # 主题色
    module_color = "#141A21"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "mattoid"
    # 作者主页
    author_url = "https://github.com/Mattoids"
    # 插件配置项ID前缀
    module_config_prefix = "jackett_"
    # 加载顺序
    module_order = 15
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enable = False
    _host = ""
    _api_key = ""
    _password = ""
    _show_more_sites = False
    _sites = []

    @staticmethod
    def get_fields():
        return [
            # 同一板块
            {
                'type': 'div',
                'content': [
                    # 同一行
                    [
                        {
                            'title': 'Jackett地址',
                            'required': "required",
                            'tooltip': 'Jackett访问地址和端口，如为https需加https://前缀。注意需要先在Jackett中添加indexer，才能正常测试通过和使用',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'host',
                                    'placeholder': 'http://127.0.0.1:9117',
                                }
                            ]
                        },
                        {
                            'title': 'Api Key',
                            'required': "required",
                            'tooltip': 'Jackett管理界面右上角复制API Key',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'api_key',
                                    'placeholder': '',
                                }
                            ]
                        }
                    ],
                    [
                        {
                            'title': '密码',
                            'required': "required",
                            'tooltip': 'Jackett管理界面中配置的Admin password，如未配置可为空',
                            'type': 'password',
                            'content': [
                                {
                                    'id': 'password',
                                    'placeholder': '',
                                }
                            ]
                        }
                    ],
                    [
                        {
                            'title': '开启内建站点',
                            'required': "",
                            'tooltip': '开启后会在内建索引器展示内置的公开站点，不开启则只显示jackett的站点',
                            'type': 'switch',
                            'id': 'show_more_sites',
                            'default': True
                        }
                    ]
                ]
            },
        ]

    def get_page(self):
        """
        插件的额外页面，返回页面标题和页面内容
        :return: 标题，页面内容，确定按钮响应函数
        """
        indexers = self.get_indexers()
        template = """
          <div class="table-responsive table-modal-body">
            <table class="table table-vcenter card-table table-hover table-striped">
              <thead>
              {% if IndexersCount > 0 %}
              <tr>
                <th>id</th>
                <th>域名</th>
                <th>是否内置</th>
                <th>是否公开</th>
                <th></th>
              </tr>
              {% else %}
              <tr>
                <th align="center">Jackett测试失败</th>
              </tr>
              {% endif %}
              </thead>
              <tbody>
              {% if IndexersCount > 0 %}
                {% for Item in Indexers %}
                  <tr id="indexer_{{ Item.id }}">
                    <td>{{ Item.id }}</td>
                    <td>{{ Item.domain }}</td>
                    <td>{{ Item.builtin }}</td>
                    <td>{{ Item.public }}</td>
                  </tr>
                {% endfor %}
              {% else %}
                <tr id="indexer_None_1">
                  <td align="center">没有数据或者Jackett配置有误</td>
                </tr>
                <tr id="indexer_None_2">
                  <td align="center">注意：(请先点击确定添加后，再回来测试)</td>
                </tr>
              {% endif %}
              </tbody>
            </table>
          </div>
        """
        return "测试", Template(template).render(IndexersCount=len(indexers), Indexers=indexers), None

    def get_status(self):
        """
        检查连通性
        :return: True、False
        """
        if not self._api_key or not self._host:
            return False
        self._sites = self.get_indexers()
        return True if self._sites else False

    def init_config(self, config=None):
        self.info(f"初始化配置{config}")

        if not config:
            return

        if config:
            self._host = config.get("host")
            log.info(f"|>>>>>>>>>>>>>>> jackett - line172 - {self._host}")
            if self._host:
                if not self._host.startswith('http'):
                    self._host = "http://" + self._host
                    log.info(f"|>>>>>>>>>>>>>>> jackett - line172 - 没有以http开头: {self._host}")
                if self._host.endswith('/'):
                    self._host = self._host.rstrip('/')
                    log.info(f"|>>>>>>>>>>>>>>> jackett - line172 - 以/结尾: {self._host}")
            self._api_key = config.get("api_key")
            self._password = config.get("password")
            self._enable = self.get_status()
            self.__update_config(showMoreSites=config.get("show_more_sites"))

    def get_state(self):
        return self._enable

    def stop_service(self):
        """
        退出插件
        """
        pass

    def __update_config(self, showMoreSites = False):
        show_more_sites = Config().get_config("laboratory").get('show_more_sites')
        if show_more_sites != showMoreSites:
            cfg = Config().get_config()
            cfg["laboratory"]["show_more_sites"] = showMoreSites
            Config().save_config(cfg)

    def get_indexers(self):
        """
        获取配置的jackett indexer
        :return: indexer 信息 [(indexerId, indexerName, url)]
        """
        #获取Cookie
        cookie = None
        session = requests.session()
        res = RequestUtils(session=session).post_res(url=f"{self._host}/UI/Dashboard", data={"password": self._password},
                                                     params={"password": self._password})
        if res and session.cookies:
            cookie = session.cookies.get_dict()
        indexer_query_url = f"{self._host}/api/v2.0/indexers?configured=true"
        try:
            ret = RequestUtils().get_res(indexer_query_url)
            if not ret or not ret.json():
                return []
            indexers = [IndexerConf({"id": v["id"],
                                 "name": v["name"],
                                 "domain": f'{self._host}/api/v2.0/indexers/{v["id"]}/results/torznab/',
                                 "public": True if v['type'] == 'public' else False,
                                 "builtin": False,
                                 "proxy": True,
                                 "parser": self.module_name})
                    for v in ret.json()]
            for indexer in indexers:
                log.info(f"|>>>>>>>>>>>>>>>> jackett - line224 - {indexer.id} -- {indexer.name}")
            return indexers
        except Exception as e2:
            ExceptionUtils.exception_traceback(e2)
            return []

    def search(self, indexer,
               keyword,
               page):
        """
        根据关键字多线程检索
        """
        if not indexer or not keyword:
            return None
        self.info(f"【{self.module_name}】开始检索Indexer：{indexer.name} ...")
        # 特殊符号处理
        api_url = f"{indexer.domain}?apikey={self._api_key}&t=search&q={keyword}"

        result_array = self.__parse_torznabxml(api_url)

        if len(result_array) == 0:
            self.warn(f"【{self.module_name}】{indexer.name} 未检索到数据")
            return []
        else:
            self.warn(f"【{self.module_name}】{indexer.name} 返回数据：{len(result_array)}")
            return result_array

    @staticmethod
    def __parse_torznabxml(url):
        """
        从torznab xml中解析种子信息
        :param url: URL地址
        :return: 解析出来的种子信息列表
        """
        if not url:
            return []
        try:
            ret = RequestUtils(timeout=10).get_res(url)
        except Exception as e2:
            ExceptionUtils.exception_traceback(e2)
            return []
        if not ret:
            return []
        xmls = ret.text
        if not xmls:
            return []

        torrents = []
        try:
            # 解析XML
            dom_tree = xml.dom.minidom.parseString(xmls)
            root_node = dom_tree.documentElement
            items = root_node.getElementsByTagName("item")
            for item in items:
                try:
                    # indexer id
                    indexer_id = DomUtils.tag_value(item, "jackettindexer", "id",
                                                    default=DomUtils.tag_value(item, "jackettindexer", "id", ""))
                    # indexer
                    indexer = DomUtils.tag_value(item, "jackettindexer",
                                                 default=DomUtils.tag_value(item, "jackettindexer", default=""))

                    # 标题
                    title = DomUtils.tag_value(item, "title", default="")
                    if not title:
                        continue
                    # 种子链接
                    enclosure = DomUtils.tag_value(item, "enclosure", "url", default="")
                    if not enclosure:
                        continue
                    # 描述
                    description = DomUtils.tag_value(item, "description", default="")
                    # 种子大小
                    size = DomUtils.tag_value(item, "size", default=0)
                    # 种子页面
                    page_url = DomUtils.tag_value(item, "comments", default="")

                    # 做种数
                    seeders = 0
                    # 下载数
                    peers = 0
                    # 是否免费
                    freeleech = False
                    # 下载因子
                    downloadvolumefactor = 1.0
                    # 上传因子
                    uploadvolumefactor = 1.0
                    # imdbid
                    imdbid = ""

                    torznab_attrs = item.getElementsByTagName("torznab:attr")
                    for torznab_attr in torznab_attrs:
                        name = torznab_attr.getAttribute('name')
                        value = torznab_attr.getAttribute('value')
                        if name == "seeders":
                            seeders = value
                        if name == "peers":
                            peers = value
                        if name == "downloadvolumefactor":
                            downloadvolumefactor = value
                            if float(downloadvolumefactor) == 0:
                                freeleech = True
                        if name == "uploadvolumefactor":
                            uploadvolumefactor = value
                        if name == "imdbid":
                            imdbid = value

                    tmp_dict = {'indexer_id': indexer_id,
                                'indexer': indexer,
                                'title': title,
                                'enclosure': enclosure,
                                'description': description,
                                'size': size,
                                'seeders': seeders,
                                'peers': peers,
                                'freeleech': freeleech,
                                'downloadvolumefactor': downloadvolumefactor,
                                'uploadvolumefactor': uploadvolumefactor,
                                'page_url': page_url,
                                'imdbid': imdbid}
                    log.info(f"|>>>>>>>>>>>>>>>>>>>> jackett - line344 - temp_dict -> {tmp_dict}")
                    torrents.append(tmp_dict)
                except Exception as e:
                    ExceptionUtils.exception_traceback(e)
                    continue
        except Exception as e2:
            ExceptionUtils.exception_traceback(e2)
            pass

        return torrents