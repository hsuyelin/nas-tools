import requests
import xml.dom.minidom
from jinja2 import Template
import re

import log

from app.utils import RequestUtils
from app.helper import IndexerConf
from app.utils import ExceptionUtils, StringUtils

from app.plugins.modules._base import _IPluginModule
from config import Config


class Prowlarr(_IPluginModule):
    # 插件名称
    module_name = "Prowlarr"
    # 插件描述
    module_desc = "让内荐索引器支持检索Prowlarr站点资源"
    # 插件图标
    module_icon = "prowlarr.png"
    # 主题色
    module_color = "#7F4A28"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "hsuyelin"
    # 作者主页
    author_url = "https://github.com/hsuyelin"
    # 插件配置项ID前缀
    module_config_prefix = "prowlarr"
    # 加载顺序
    module_order = 16
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enable = False
    _host = ""
    _api_key = ""
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
                            'title': 'Prowlarr地址',
                            'required': "required",
                            'tooltip': 'Prowlarr访问地址和端口，如为https需加https://前缀。注意需要先在Prowlarr中添加搜刮器，同时勾选所有搜刮器后搜索一次，才能正常测试通过和使用',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'host',
                                    'placeholder': 'http://127.0.0.1:9696',
                                }
                            ]
                        },
                        {
                            'title': 'Api Key',
                            'required': "required",
                            'tooltip': '在Prowlarr->Settings->General->Security-> API Key中获取',
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
                            'title': '开启内建站点',
                            'required': "",
                            'tooltip': '开启后会在内建索引器展示内置的公开站点，不开启则只显示prowlarr的站点',
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
                <th align="center">Prowlarr测试失败</th>
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
                  <td align="center">没有数据或者Prowlarr配置有误</td>
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
            if self._host:
                if not self._host.startswith('http'):
                    self._host = "http://" + self._host
                if self._host.endswith('/'):
                    self._host = self._host.rstrip('/')
            self._api_key = config.get("api_key")
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

    def get_indexers(self, check=True, indexer_id=None, public=True, plugins=True):
        """
        获取配置的prowlarr indexer
        :return: indexer 信息 [(indexerId, indexerName, url)]
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": Config().get_ua(),
            "X-Api-Key": self._api_key,
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }
        indexer_query_url = f"{self._host}/api/v1/indexerstats"
        try:
            ret = RequestUtils(headers=headers).get_res(indexer_query_url)
            if not ret or not ret.json():
                return []
            ret_indexers = ret.json()["indexers"]
            if not ret or ret_indexers == [] or ret is None:
                return []

            indexers = [IndexerConf({"id": f'{v["indexerName"]}-prowlarr',
                                 "name": v["indexerName"],
                                 "domain": f'{self._host}/api/v1/indexer/{v["indexerId"]}',
                                 "public": True,
                                 "builtin": False,
                                 "proxy": True,
                                 "parser": self.module_name})
                    for v in ret_indexers]
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

        # 获取indexerId
        indexerId_pattern = r"/indexer/([^/]+)"
        indexerId_match = re.search(indexerId_pattern, indexer.domain)
        indexerId = ""
        if indexerId_match:
            indexerId = indexerId_match.group(1)

        if not StringUtils.is_string_and_not_empty(indexerId):
            self.info(f"【{self.module_name}】{indexer.name} 索引id为空")
            return []

        try:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": Config().get_ua(),
                "X-Api-Key": self._api_key,
                "Accept": "application/json, text/javascript, */*; q=0.01"
            }
            api_url = f"{self._host}/api/v1/search?query={keyword}&indexerIds={indexerId}&type=search&limit=100&offset=0"
            ret = RequestUtils(headers=headers).get_res(api_url)
            if not ret or not ret.json():
                return []

            ret_indexers = ret.json()
            if not ret or ret_indexers == [] or ret is None:
                return []

            torrents = []
            for entry in ret_indexers:
                tmp_dict = {'indexer_id': entry["indexerId"],
                            'indexer': entry["indexer"],
                            'title': entry["title"],
                            'enclosure': entry["downloadUrl"],
                            'description': entry["sortTitle"],
                            'size': entry["size"],
                            'seeders': entry["seeders"],
                            'peers': None,
                            'freeleech': None,
                            'downloadvolumefactor': None,
                            'uploadvolumefactor': None,
                            'page_url': entry["guid"],
                            'imdbid': None}
                torrents.append(tmp_dict)
            return torrents
        except Exception as e2:
            ExceptionUtils.exception_traceback(e2)
            return []