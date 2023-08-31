from datetime import datetime
from threading import Event

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.downloader import Downloader
from app.message import Message
from app.plugins.modules._base import _IPluginModule
from app.utils.types import DownloaderType
from config import Config


class TorrentMark(_IPluginModule):
    # 插件名称
    module_name = "种子标记"
    # 插件描述
    module_desc = "标记种子是否是PT。"
    # 插件图标
    module_icon = "tag.png"
    # 主题色
    module_color = "#4876b6"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "hsuyelin"
    # 作者主页
    author_url = "https://github.com/hsuyelin"
    # 插件配置项ID前缀
    module_config_prefix = "torrentmark_"
    # 加载顺序
    module_order = 10
    # 可使用的用户级别
    user_level = 1

    # 私有属性
    _scheduler = None
    downloader = None
    # 限速开关
    _enable = False
    _cron = None
    _onlyonce = False
    _downloaders = []
    _nolabels = None
    # 退出事件
    _event = Event()

    @staticmethod
    def get_fields():
        downloaders = {k: v for k, v in Downloader().get_downloader_conf_simple().items()
                       if v.get("type") in ["qbittorrent", "transmission"] and v.get("enabled")}
        return [
            # 同一板块
            {
                'type': 'div',
                'content': [
                    # 同一行
                    [
                        {
                            'title': '开启种子标记',
                            'required': "",
                            'tooltip': '开启后，自动监控下载器，对下载完成的任务根据执行周期标记。',
                            'type': 'switch',
                            'id': 'enable',
                        }
                    ],
                    [
                        {
                            'title': '执行周期',
                            'required': "required",
                            'tooltip': '标记任务执行的时间周期，支持5位cron表达式；应避免任务执行过于频繁',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'cron',
                                    'placeholder': '0 0 0 ? *',
                                }
                            ]
                        }
                    ]
                ]
            },
            {
                'type': 'details',
                'summary': '下载器',
                'tooltip': '只有选中的下载器才会执行标记',
                'content': [
                    # 同一行
                    [
                        {
                            'id': 'downloaders',
                            'type': 'form-selectgroup',
                            'content': downloaders
                        },
                    ]
                ]
            },
            {
                'type': 'div',
                'content': [
                    # 同一行
                    [
                        {
                            'title': '立即运行一次',
                            'required': "",
                            'tooltip': '打开后立即运行一次（点击此对话框的确定按钮后即会运行，周期未设置也会运行），关闭后将仅按照刮削周期运行（同时上次触发运行的任务如果在运行中也会停止）',
                            'type': 'switch',
                            'id': 'onlyonce',
                        }
                    ]
                ]
            }
        ]

    def init_config(self, config=None):
        self.downloader = Downloader()
        self.message = Message()
        # 读取配置
        if config:
            self._enable = config.get("enable")
            self._onlyonce = config.get("onlyonce")
            self._cron = config.get("cron")
            self._downloaders = config.get("downloaders")
        # 停止现有任务
        self.stop_service()

        # 启动定时任务 & 立即运行一次
        if self.get_state() or self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=Config().get_timezone())
            if self._cron:
                self.info(f"标记服务启动，周期：{self._cron}")
                self._scheduler.add_job(self.auto_mark,
                                        CronTrigger.from_crontab(self._cron))
            if self._onlyonce:
                self.info(f"标记服务启动，立即运行一次")
                self._scheduler.add_job(self.auto_mark, 'date',
                                        run_date=datetime.now(tz=pytz.timezone(Config().get_timezone())))
                # 关闭一次性开关
                self._onlyonce = False
                self.update_config({
                    "enable": self._enable,
                    "onlyonce": self._onlyonce,
                    "cron": self._cron,
                    "downloaders": self._downloaders
                })
            if self._cron or self._onlyonce:
                # 启动服务
                self._scheduler.print_jobs()
                self._scheduler.start()

    def get_state(self):
        return True if self._enable and self._cron and self._downloaders else False

    def auto_mark(self):
        """
        开始标记
        """
        if not self._enable or not self._downloaders:
            self.warn("标记服务未启用或未配置")
            return
        # 扫描下载器辅种
        for downloader in self._downloaders:
            self.info(f"开始扫描下载器：{downloader} ...")
            # 下载器类型
            downloader_type = self.downloader.get_downloader_type(downloader_id=downloader)
            # 获取下载器中已完成的种子
            torrents = self.downloader.get_completed_torrents(downloader_id=downloader)
            if torrents:
                self.info(f"下载器 {downloader} 已完成种子数：{len(torrents)}")
            else:
                self.info(f"下载器 {downloader} 没有已完成种子")
                continue
            for torrent in torrents:
                if self._event.is_set():
                    self.info(f"标记服务停止")
                    return
                # 获取种子hash
                hash_str = self.__get_hash(torrent, downloader_type)
                # 获取种子标签
                torrent_tags = set(self.__get_tag(torrent, downloader_type))
                pt_flag = self.__isPt(torrent, downloader_type)
                torrent_tags.discard("")
                if pt_flag is True:
                    torrent_tags.discard("BT")
                    torrent_tags.add("PT")
                    self.downloader.set_torrents_tag(downloader_id=downloader, ids=hash_str, tags=list(torrent_tags))
                else:
                    torrent_tags.add("BT")
                    torrent_tags.discard("PT")
                    self.downloader.set_torrents_tag(downloader_id=downloader, ids=hash_str, tags=list(torrent_tags))
        self.info("标记任务执行完成")

    @staticmethod
    def __get_hash(torrent, dl_type):
        """
        获取种子hash
        """
        try:
            return torrent.get("hash") if dl_type == DownloaderType.QB else torrent.hashString
        except Exception as e:
            print(str(e))
            return ""

    @staticmethod
    def __get_tag(torrent, dl_type):
        """
        获取种子标签
        """
        try:
            return list(map(lambda s: s.strip(), (torrent.get("tags") or "").split(","))) if dl_type == DownloaderType.QB else torrent.labels or []
        except Exception as e:
            print(str(e))
            return []

    @staticmethod
    def __isPt(torrent, dl_type):
        """
        获取种子标签
        """
        try:
            tracker_list = list()
            if dl_type == DownloaderType.QB and torrent.trackers_count == 1:
                for tracker in torrent.trackers.data:
                    if tracker['url'].find('http') != -1:
                        tracker_list.append(tracker['url'])
            elif dl_type == DownloaderType.TR:
                tracker_list = list(map(lambda s: s['announce'], torrent.trackers or []))
            if len(tracker_list) == 1:
                if tracker_list[0].find("secure=") != -1 \
                    or tracker_list[0].find("passkey=") != -1 \
                        or tracker_list[0].find("totheglory") != -1:
                    return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False

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