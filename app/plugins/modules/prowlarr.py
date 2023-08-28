import requests
from datetime import datetime, timedelta
from threading import Event
import xml.dom.minidom
from jinja2 import Template
import re

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.utils import RequestUtils
from app.indexer.indexerConf import IndexerConf
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
    module_version = "1.5"
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
    eventmanager = None
    _scheduler = None
    _enable = False
    _host = ""
    _api_key = ""
    _onlyonce = False
    _sites = None

    # 退出事件
    _event = Event()

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
                            'title': '更新周期',
                            'required': "",
                            'tooltip': '索引列表更新周期，支持5位cron表达式，默认每24小时运行一次',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'cron',
                                    'placeholder': '0 0 */24 * *',
                                }
                            ]
                        }
                    ],
                    [
                        {
                            'title': '立即运行一次',
                            'required': "",
                            'tooltip': '打开后立即运行一次获取索引器列表，否则需要等到预先设置的更新周期才会获取',
                            'type': 'switch',
                            'id': 'onlyonce',
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
        if not isinstance(self._sites, list) or len(self._sites) <= 0:
            return None, None, None
        template = """
          <div class="table-responsive table-modal-body">
            <table class="table table-vcenter card-table table-hover table-striped">
              <thead>
              {% if IndexersCount > 0 %}
              <tr>
                <th>id</th>
                <th>索引</th>
                <th>是否公开</th>
                <th></th>
              </tr>
              {% endif %}
              </thead>
              <tbody>
              {% if IndexersCount > 0 %}
                {% for Item in Indexers %}
                  <tr id="indexer_{{ Item.id }}">
                    <td>{{ Item.id }}</td>
                    <td>{{ Item.domain }}</td>
                    <td>{{ Item.public }}</td>
                  </tr>
                {% endfor %}
              {% endif %}
              </tbody>
            </table>
          </div>
        """
        return "索引列表", Template(template).render(IndexersCount=len(self._sites), Indexers=self._sites), None

    def init_config(self, config=None):
        self.info(f"初始化配置{config}")

        if config:
            self._host = config.get("host")
            if self._host:
                if not self._host.startswith('http'):
                    self._host = "http://" + self._host
                if self._host.endswith('/'):
                    self._host = self._host.rstrip('/')
            self._api_key = config.get("api_key")
            self._enable = self.get_status()
            self._onlyonce = config.get("onlyonce")
            self._cron = config.get("cron")
            if not StringUtils.is_string_and_not_empty(self._cron):
                self._cron = "0 0 */24 * *"


        # 停止现有任务
        self.stop_service()

        # 启动定时任务 & 立即运行一次
        if self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=Config().get_timezone())

            if self._cron:
                self.info(f"【{self.module_name}】 索引更新服务启动，周期：{self._cron}")
                self._scheduler.add_job(self.get_status, CronTrigger.from_crontab(self._cron))

            if self._onlyonce:
                self.info(f"【{self.module_name}】开始获取索引器状态")
                self._scheduler.add_job(self.get_status, 'date',
                                        run_date=datetime.now(tz=pytz.timezone(Config().get_timezone())) + timedelta(
                                            seconds=3))
                # 关闭一次性开关
                self._onlyonce = False
                self.__update_config()

            if self._cron or self._onlyonce:
                # 启动服务
                self._scheduler.print_jobs()
                self._scheduler.start()

    def get_status(self):
        """
        检查连通性
        :return: True、False
        """
        if not self._api_key or not self._host:
            return False
        self._sites = self.get_indexers()
        return True if isinstance(self._sites, list) and len(self._sites) > 0 else False

    def get_state(self):
        return self._enable

    def stop_service(self):
        """
        退出插件
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._event.set()
                    self._scheduler.shutdown()
                    self._event.clear()
                self._scheduler = None
        except Exception as e:
            self.error(f"【{self.module_name}】停止插件错误: {str(e)}")

    def __update_config(self):
        """
        更新优选插件配置
        """
        self.update_config({
            "onlyonce": False,
            "cron": self._cron,
            "host": self._host,
            "api_key": self._api_key
        })

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
            if not ret:
                return []
            if not RequestUtils.check_response_is_valid_json(ret):
                self.info(f"【{self.module_name}】参数设置不正确，请检查所有的参数是否填写正确")
                return []
            if not ret.json():
                return []
            ret_indexers = ret.json()["indexers"]
            if not ret or ret_indexers == [] or ret is None:
                return []

            indexers = [IndexerConf({"id": f'{v["indexerName"]}-prowlarr',
                                 "name": f'{v["indexerName"]}(Prowlarr)',
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
            if not ret:
                return []
            if not RequestUtils.check_response_is_valid_json(ret):
                self.info(f"【{self.module_name}】参数设置不正确，请检查所有的参数是否填写正确")
                return []
            if not ret.json():
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