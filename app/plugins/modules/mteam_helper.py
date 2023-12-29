from datetime import datetime, timedelta
from threading import Event, Lock

import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from jinja2 import Template

from app.brushtask import BrushTask
from app.downloader import Downloader
from app.message import Message
from app.plugins import EventHandler
from app.plugins.modules._base import _IPluginModule
from app.sites import Sites
from app.utils.types import EventType
from config import Config

lock = Lock()


class MTeamHelper(_IPluginModule):
    # 插件名称
    module_name = "馒头助手"
    # 插件描述
    module_desc = "监控馒头大包，自动添加订阅下载。"
    # 插件图标
    module_icon = "mteamhelper.png"
    # 主题色
    module_color = "#05C711"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "Flik"
    # 作者主页
    author_url = "https://github.com/Flik6"
    # 插件配置项ID前缀
    module_config_prefix = "mteamhelper_"
    # 加载顺序
    module_order = 17
    # 可使用的用户级别
    auth_level = 1

    _scheduler = None

    # 退出事件
    _event = Event()
    # 私有属性
    _enable = False
    _onlyonce = False
    _autodownload = False
    _interval = 0
    _torrent_quantity = 3
    _torrent_size = None
    _category = None
    _enable_message = False
    _MTeam_info = {}

    def init_config(self, config: dict = None):
        self.debug(f"初始化配置")

        if config:
            self._enable = config.get("enable")
            self._onlyonce = config.get("onlyonce")
            self._autodownload = config.get("autodownload")
            self._interval = int(config.get("interval"))
            self._torrent_size = config.get("torrent_size")
            self._torrent_quantity = config.get("torrent_quantity")
            self._category = config.get("category")
            self._enable_message = config.get("enable_message")

        # 停止现有任务
        self.stop_service()

        # 启动服务
        if self._enable or self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=Config().get_timezone())
            self.get_mteam_all_torrent()
            if self._interval:
                self.info(f"馒头助手服务启动，周期：{self._interval} 分钟")
                self._scheduler.add_job(self.get_latest_torrents, 'interval',
                                        minutes=self._interval)

            if self._onlyonce:
                self.info("馒头助手服务启动，立即运行一次")
                self._scheduler.add_job(self.get_latest_torrents, 'date',
                                        run_date=datetime.now(tz=pytz.timezone(Config().get_timezone())) + timedelta(
                                            seconds=3))

                # 关闭一次性开关
                self._onlyonce = False
                self.update_config({
                    "enable": self._enable,
                    "onlyonce": self._onlyonce,
                    "autodownload": self._autodownload,
                    "interval": self._interval,
                    "torrent_quantity": self._torrent_quantity,
                    "torrent_size": self._torrent_size,
                    "category": self._category,
                    "enable_message": self._enable_message
                })
            if self._scheduler.get_jobs():
                # 启动服务
                self._scheduler.print_jobs()
                self._scheduler.start()

    def get_state(self):
        return self._enable

    @staticmethod
    def get_fields():
        category = {0: {'id': 0, 'name': '成人'}, 1: {'id': 1, 'name': '综合'}}
        return [
            # 同一板块
            {
                'type': 'div',
                'content': [
                    # 同一行
                    [
                        {
                            'title': '开启馒头大包监控',
                            'required': "",
                            'tooltip': '开启后，定时监控MTeam网站大包，有新内容时发送消息通知',
                            'type': 'switch',
                            'id': 'enable',
                        },
                        {
                            'title': '立即运行一次',
                            'required': "",
                            'tooltip': '打开后立即运行一次（点击此对话框的确定按钮后即会运行，周期未设置也会运行）',
                            'type': 'switch',
                            'id': 'onlyonce',
                        }
                    ],
                    [
                        {
                            'title': '消息通知',
                            'required': "",
                            'tooltip': '当监控到大包更新后向您发送消息通知',
                            'type': 'switch',
                            'id': 'enable_message',
                        },
                        {
                            'title': '自动下载',
                            'required': "",
                            'tooltip': '当监控到更新后自动下载，遵循站点管理 - 刷流任务的配置项，支持自动删种。',
                            'type': 'switch',
                            'id': 'autodownload',
                        },
                    ],
                    [
                        {
                            'title': '大包大小',
                            'required': "",
                            'tooltip': '设置大小范围的种子才会下载，介于时使用英文逗号,分隔两个值，小于时填写单个数值，默认下载全部，单位为GB',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'torrent_size',
                                    'placeholder': '500,2000',
                                }
                            ]
                        },
                        {
                            'title': '间隔时间(单位：分钟)',
                            'required': "required",
                            'tooltip': '选择间隔多久去拉去馒头大包数据',
                            'type': 'select',
                            'content': [
                                {
                                    'id': 'interval',
                                    'options': {
                                        '1': '1',
                                        '2': '2',
                                        '3': '3',
                                        '4': '4',
                                        '5': '5',
                                    },
                                    'default': '3',
                                }
                            ]
                        }
                    ],
                ]
            },
            {
                'type': 'details',
                'summary': '监控分类',
                'tooltip': '只有选中的分类才会执行监控，不选则默认为全选',
                'content': [
                    # 同一行
                    [
                        {
                            'id': 'category',
                            'type': 'form-selectgroup',
                            'content': category
                        },
                    ]
                ]
            },
        ]

    @staticmethod
    def get_command():
        """
        定义远程控制命令
        :return: 命令关键字、事件、描述、附带数据
        """
        return {
            "cmd": "/mteam",
            "event": EventType.MTeamHelper,
            "desc": "馒头大包自动监控下载",
            "data": {}
        }

    def get_mteam_all_torrent(self):
        self.debug(f"加载全部馒头种子")
        res = requests.post(url="https://plus.92coco.cn:8443/api/torrent/getAllMTeamTop")
        if res is None or res.status_code != 200:
            self.error(f"获取馒头置顶种子失败，请检查网络链接！")
        json_result = res.json()
        torrents = json_result['data']
        if res.status_code == 200:
            torrents_md5 = [seed['md5'] for seed in torrents]
            self.__update_history(key="torrents_md5", value=torrents_md5)
            self.__update_history(key="torrents", value=torrents)
            self.info(f"获取馒头置顶种子成功，共获取到了{len(json_result['data'])}条")
            self.debug(torrents_md5)
        else:
            self.warn(f"获取馒头置顶种子时出现异常，异常信息: {json_result['msg']}")
        return torrents

    @EventHandler.register(EventType.MTeamHelper)
    def get_latest_torrents(self):
        self.debug(f"获取馒头最新种子状况")
        url = "https://plus.92coco.cn:8443/api/torrent/filterMTeamTop"
        if isinstance(self._torrent_size, str):
            temp_size = str(self._torrent_size).split(",")
        data = {
            "type": self._category[0] if len(self._category) == 1 else None,
            "min": None if "".__eq__(temp_size[0]) else temp_size[0] + "GB",
            "max": temp_size[1] + "GB" if temp_size == 2 else None,
            "md5": self.get_history("torrents_md5")
        }
        try:
            res = requests.post(url=url, json=data)
            resp_json = res.json()['data']
            rows = resp_json['rows']
            total = resp_json['total']
            md5s = resp_json['md5s']
        except:
            self.error(f"获取最新种子时出现异常。")
            return
        if total == 0:
            self.info(f"暂未获取到最新置顶种子")
            return

        self.info(f"获取到{total}个最新置顶种子")

        # 更新服务器最新的所有md5
        self.__update_history(key="torrents_md5", value=md5s)

        if self._enable_message:
            msg_title = f"【MTeamHelper 大包提醒】"
            msg_text = f"共获取到{total}个新增\n"
            for one in rows:
                msg_text += "--------------\n" \
                            f"类型:{one['type']}\n" \
                            f"主标题:{one['mainTitle']}\n" \
                            f"副标题:{one['subTitle']}\n" \
                            f"标签:{one['tag']}  大小:{one['readableSize']}\n" \
                            f"剩余免费时间:{one['remainingFreeTime']}\n" \
                            f"发布时间:{one['pubDate']}\n" \
                            f"做种数:{one['seederCount']} | 下载数:{one['downloaderCount']} | 完成数:{one['completedCount']}"
            self.send_message(msg_title, msg_text, rows[0]['imgHref'])
        if self._autodownload:
            self.info(f"已开启自动下载，开始执行下载任务")
            if self.get_brushtask_info()['id']:
                BrushTask().check_task_rss(self.get_brushtask_info()['id'], other_task=rows)

    def get_brushtask_info(self):
        sites = Sites().get_all_site()
        site_result = [site for site in sites if str(site['strict_url']).__contains__("m-team")]
        if len(site_result) == 0:
            self.error(f"请检查您是否在站点管理内添加了MTeam站点!")
            return

        brush_tasks = BrushTask().get_brushtask_info()
        result = [d for d in brush_tasks.values() if str(d['site_id']) == str(site_result[0]['id'])]
        if len(result) == 0:
            if self._autodownload:
                self.error("由于未在刷流任务内添加MTeam站点，暂无法为您提供自动下载服务！")
                self._autodownload = False
                self.__update_history("auto_download", False)
            return
        return result[0]

    def __update_history(self, key, value):
        if self.get_history(key):
            self.update_history(key=key, value=value)
        else:
            self.history(key=key, value=value)

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
            print(str(e))
