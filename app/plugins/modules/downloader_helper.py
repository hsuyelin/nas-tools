from app.plugins.modules._base import _IPluginModule
from app.downloader import Downloader
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime, timedelta
from threading import Event
from app.utils.types import DownloaderType
import urllib
import re
from app.sites import Sites
from app.plugins import EventHandler
from app.utils.types import EventType
import os
from jinja2 import Template

class DownloaderHelper(_IPluginModule):
    # 插件名称
    module_name = "下载器助手"
    # 插件描述
    module_desc = "定期将完成但未做种的种子设为做种，种子赋予站点标签，联动删种，自动删丢失文件坏种。"
    # 插件图标
    module_icon = "'); background-image: url('data:image/png;base64,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"
    # 主题色
    module_color = "#6c7a91"
    # 插件版本
    module_version = "1.4"
    # 插件作者
    module_author = "hotlcc"
    # 作者主页
    author_url = "https://gitee.com/hotlcc"
    # 插件配置项ID前缀
    module_config_prefix = "com.hotlcc.downloader-helper."
    # 加载顺序
    module_order = 21
    # 可使用的用户级别
    user_level = 2

    # 私有属性
    __timezone = None
    # 调度器
    __scheduler = None
    # 下载器
    __downloader = None
    # 退出事件
    __exit_event = Event()
    # 任务运行中状态
    __running_state = Event()

    # 配置对象
    __config_obj = None
    
    @staticmethod
    def get_fields():
        fields = [
            # 同一板块
            {
                'type': 'div',
                'content': [
                    # 同一行
                    [
                        {
                            'id': 'enable',
                            'type': 'switch',
                            'title': '启动插件',
                            'tooltip': '插件总开关',
                        },
                        {
                            'id': 'enable_notify',
                            'type': 'switch',
                            'title': '运行时通知',
                            'tooltip': '运行任务后会发送通知（需要打开插件消息通知）',
                        },
                        {
                            'id': 'run_once',
                            'type': 'switch',
                            'title': '立即运行一次',
                            'tooltip': '打开后立即运行一次（点击此对话框的确定按钮后即会运行，周期未设置也会运行），关闭后将仅按照周期运行（同时上次触发运行的任务如果在运行中也会停止）',
                        }
                    ]
                ]
            },
            {
                'type': 'div',
                'content': [
                    [
                        {
                            'id': 'listen_download_event',
                            'type': 'switch',
                            'title': '监听下载事件',
                            'tooltip': '监听下载添加事件。当在NAStool中添加下载任务时，会自动触发运行本插件任务进行自动做种。',
                        },
                        {
                            'id': 'listen_source_file_event',
                            'type': 'switch',
                            'title': '监听源文件事件',
                            'tooltip': '监听源文件事件。当在NAStool的“媒体整理/历史记录”中删除源文件时，会自动触发运行本插件任务进行自动删种。',
                        },
                        {
                            'id': 'use_site_config',
                            'type': 'switch',
                            'title': '使用站点配置',
                            'tooltip': '给种子添加站点标签时，是否优先以【站点配置】中配置的站点名称作为标签内容？',
                        },
                        {
                            'title': ' '
                        }
                    ],
                    [
                        {
                            'type': 'text',
                            'title': '定时执行周期',
                            'tooltip': '设置插件任务执行周期，支持5位cron表达式；应避免任务执行过于频繁',
                            'content': [
                                {
                                    'id': 'cron',
                                    'placeholder': '0/30 * * * *',
                                }
                            ]
                        },
                        {
                            'type': 'text',
                            'title': '排除种子标签',
                            'tooltip': '下载器中的种子有以下标签时不进行任何操作，多个标签使用英文,分割',
                            'content': [
                                {
                                    'id': 'exclude_tags'
                                }
                            ]
                        }
                    ]
                ]
            }
        ]
        # 过滤出有效的下载器
        downloaders = {k: v for k, v in Downloader().get_downloader_conf_simple().items()
                       if v.get("type") in ["qbittorrent", "transmission"] and v.get("enabled")}
        # 遍历下载器
        for downloader_id, downloader in downloaders.items():
            downloader_id = downloader.get('id')
            downloader_id_str = str(downloader_id)
            downloader_name = downloader.get('name')
            fields.append({
                'type': 'details',
                'summary': '任务：' + downloader_name,
                'content': [
                    [
                        {
                            'id': 'downloader.' + downloader_id_str + '.enable',
                            'type': 'switch',
                            'title': '任务开关',
                        },
                        {
                            'id': 'downloader.' + downloader_id_str + '.enable_seeding',
                            'type': 'switch',
                            'title': '自动做种',
                            'tooltip': '设置“' + downloader_name + '”下载器是否开启自动做种，开启后将会定期把完成但未做种的种子设为做种',
                        },
                        {
                            'id': 'downloader.' + downloader_id_str + '.enable_tagging',
                            'type': 'switch',
                            'title': '站点标签',
                            'tooltip': '设置“' + downloader_name + '”下载器是否开启自动添加站点标签，开启后将会定期完善种子的站点标签',
                        }
                    ],
                    [
                        {
                            'id': 'downloader.' + downloader_id_str + '.enable_delete',
                            'type': 'switch',
                            'title': '自动删种',
                            'tooltip': '设置“' + downloader_name + '”下载器是否开启自动删种，开启后以下功能将生效：1、定期删除丢失文件的坏种；2、通过NAStool删除媒体源文件时，同步删除下载器中的关联种子（需开启【监听源文件事件】）。',
                        }
                    ]
                ]
            })
        return fields
    
    def get_page(self):
        """
        左下角按钮页面
        """
        template = """
            <div class="modal-body" style="max-height: 545px;">
                <p>本插件仅支持qBittorrent和Transmission两种下载器。</p>
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title">
                                    <strong>全局配置</strong>
                                </h3>
                            </div>
                            <div class="card-body">
                                <table class="table table-vcenter card-table table-hover table-striped">
                                    <thead>
                                        <tr>
                                            <th>配置项</th>
                                            <th>说明</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>启动插件</td>
                                            <td>插件任务总开关，关闭后插件将不会在后台运行，即定时任务和事件监听不会生效，但不影响“立即运行一次”。</td>
                                        </tr>
                                        <tr>
                                            <td>运行时通知</td>
                                            <td>插件运行后，以通知方式汇报运行结果。</td>
                                        </tr>
                                        <tr>
                                            <td>立即运行一次</td>
                                            <td>开关打开并保存插件配置后会立即运行一次插件任务，该功能不受“启动插件”的管控，也不受事件监听和定时周期的影响，只要存在有效的任务配置就能够生效。</td>
                                        </tr>
                                        <tr>
                                            <td>监听下载事件</td>
                                            <td>打开此监听后，通过NAStool向下载器中添加种子时会触发插件任务执行打标，下载、刷流、订阅、转种、辅种等场景均有效。单独在下载器中直接添加时不会生效，但当定时任务扫描时也会生效。</td>
                                        </tr>
                                        <tr>
                                            <td>监听源文件事件</td>
                                            <td>打开此监听后，在“媒体整理/历史记录”中删除源文件（或源及媒体文件）时，是否允许联动删除下载器中的对应种子，需要配合任务中的“自动删种”进行使用。该功能比NAStool作者开发的“下载任务联动删除”插件更加强大。</td>
                                        </tr>
                                        <tr>
                                            <td>使用站点配置</td>
                                            <td>打开后，在给种子添加站点标签时，会优先采用“站点配置”中配置的站点名称作为标签内容，否则使用域名关键字。</td>
                                        </tr>
                                        <tr>
                                            <td>定时执行周期</td>
                                            <td>插件定时执行的周期，仅支持5位cron表达式，即格式“分 时 日 月 周”。</td>
                                        </tr>
                                        <tr>
                                            <td>排除种子标签</td>
                                            <td>插件在执行任务时，带有相关标签的种子将被忽略。支持配置多个标签，多个用英文逗号分隔。</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title">
                                    <strong>任务配置</strong>
                                </h3>
                            </div>
                            <div class="card-body">
                                <p>当NAStool中有配置下载器时，插件配置界面会展示这些下载器对应的任务配置栏。</p>
                                <table class="table table-vcenter card-table table-hover table-striped">
                                    <thead>
                                        <tr>
                                            <th>配置项</th>
                                            <th>说明</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>任务开关</td>
                                            <td>是否启用当前下载器的任务。</td>
                                        </tr>
                                        <tr>
                                            <td>自动做种</td>
                                            <td>插件运行时，会将已经下载完成但不是做种状态的种子设为做种状态。转种、辅种场景有时候校验完成后不会自动做种，可以通过该功能解决。</td>
                                        </tr>
                                        <tr>
                                            <td>站点标签</td>
                                            <td>插件运行时，会给没有站点标签的种子添加站点标签，方便根据站点统计种子数量。</td>
                                        </tr>
                                        <tr>
                                            <td>自动删种</td>
                                            <td>自动删种有两个方面的功能：一方面独立生效，插件运行时会检测并删除丢文件的坏种；另一方面需要配合“监听源文件事件”使用，联动删除种子。</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="card">
                            <div class="card-header">
                                <h3 class="card-title">
                                    <strong>关于</strong>
                                </h3>
                            </div>
                            <div class="card-body">
                                <p>开发者：<a href="{{ module_info.author_url }}">{{ module_info.module_author }}</a></p>
                                <p>开源仓库：<a href="{{ module_info.author_url }}/nastool-plugin">{{ module_info.author_url }}/nastool-plugin</a></p>
                                <p>当前版本：v{{ module_info.module_version }}</p>
                            </div>
                        </div>
            </div>
        """
        return '使用帮助', Template(template).render(module_info = self), "DownloaderHelper.goBack()"

    @staticmethod
    def get_script():
        """
        页面JS脚本
        """
        return """
            (function() {
                var DownloaderHelper = {
                    id: "DownloaderHelper"
                }
                window.DownloaderHelper = DownloaderHelper;
                
                var goBack = function() {
                    $("#modal-plugin-page").modal('hide');
                    $("#modal-plugin-" + DownloaderHelper.id).modal('show');
                };
                DownloaderHelper.goBack = goBack;
            })();
        """

    def __parse_config(self, config = None):
        """
        解析配置
        """
        config_obj = {}
        if (not config):
            self.debug(f"解析配置: config = {config}, config_obj = {config_obj}")
            return config_obj
        
        config_obj['enable'] = config.get('enable')
        config_obj['enable_notify'] = config.get('enable_notify')
        config_obj['run_once'] = config.get('run_once')
        config_obj['cron'] = config.get('cron')
        config_obj['exclude_tags'] = config.get('exclude_tags')
        config_obj['use_site_config'] = config.get('use_site_config')
        config_obj['listen_download_event'] = config.get('listen_download_event')
        config_obj['listen_source_file_event'] = config.get('listen_source_file_event')
        config_obj['downloader'] = {}
        for config_key, config_value in config.items():
            if (config_key.startswith('downloader.')):
                downloader = config_obj.get('downloader')
                
                config_key_array = config_key.split('.')
                downloader_id = int(config_key_array[1])
                downloader_config_key = config_key_array[2]
                
                downloader_info = downloader.get(downloader_id)
                if (not downloader_info):
                    downloader_info = {}
                    downloader[downloader_id] = downloader_info
                
                downloader_info[downloader_config_key] = config_value
        self.debug(f"解析配置: config = {config}, config_obj = {config_obj}")
        return config_obj
    
    def __un_parse_config(self, config_obj = None):
        """
        反解析配置
        """
        config = {}
        if (not config_obj):
            self.debug(f"反解析配置: config_obj = {config_obj}, config = {config}")
            return config
        
        config['enable'] = config_obj.get('enable')
        config['enable_notify'] = config_obj.get('enable_notify')
        config['run_once'] = config_obj.get('run_once')
        config['cron'] = config_obj.get('cron')
        config['exclude_tags'] = config_obj.get('exclude_tags')
        config['use_site_config'] = config_obj.get('use_site_config')
        config['listen_download_event'] = config_obj.get('listen_download_event')
        config['listen_source_file_event'] = config_obj.get('listen_source_file_event')
        downloader = config_obj.get('downloader')
        for downloader_id, downloader_info in downloader.items():
            for downloader_config_key, config_value in downloader_info.items():
                config_key = 'downloader.' + str(downloader_id) + '.' + downloader_config_key
                config[config_key] = config_value
        self.debug(f"反解析配置: config_obj = {config_obj}, config = {config}")
        return config

    def __init_scheduler(self, timezone = None):
        """
        初始化调度器
        """
        if (self.__scheduler):
            return
        if (not timezone):
            timezone = Config().get_timezone()
        self.__scheduler = BackgroundScheduler(timezone = timezone)
        self.debug(f"服务调度器初始化完成")

    def init_config(self, config = None):
        self.debug(f"初始化配置")
        timezone = Config().get_timezone()
        self.__timezone = timezone
        self.__downloader = Downloader()

        # 读取配置
        if config:
            self.__config_obj = self.__parse_config(config)
        
        # 停止现有任务
        self.stop_service()
        self.debug(f"停止现有服务成功")

        # 启动插件服务
        if (self.get_state()):
            self.__init_scheduler(timezone)
            cron = self.__config_obj.get('cron')
            if (cron):
                self.__scheduler.add_job(self.__do_task, CronTrigger.from_crontab(cron))
                self.info(f"定时任务已启动，周期: cron = {cron}")
        else:
            self.warn(f"插件配置无效，服务未启动")

        # 如果需要立即运行一次
        if (self.__config_obj.get('run_once')):
            if (self.__check_has_enabled_task()):
                self.__init_scheduler(timezone)
                self.__scheduler.add_job(self.__do_task, 'date', run_date = datetime.now(tz = pytz.timezone(timezone)) + timedelta(seconds = 3))
                self.info(f"立即运行一次成功")
            else:
                self.warn(f"任务配置无效，立即运行一次未成功")
            # 关闭一次性开关
            self.__config_obj['run_once'] = False
            self.update_config(self.__un_parse_config(self.__config_obj))

        # 启动服务调度器
        if (self.__scheduler):
            self.__scheduler.print_jobs()
            self.__scheduler.start()
            self.debug(f"服务调度器初启动成功")

    def __check_has_enabled_sub_task(self, downloader_info = None):
        """
        判断单个任务中是否有生效的子任务
        """
        if (not downloader_info):
            return False
        return True if downloader_info.get('enable_seeding') \
                       or downloader_info.get('enable_tagging') \
                       or downloader_info.get('enable_delete') else False

    def __check_has_enabled_task(self, downloader = None):
        """
        判断任务列表中是否有生效的任务
        """
        if (not downloader):
            downloader = self.__config_obj.get('downloader')
        if (not downloader):
            return False
        for downloader_info in downloader.values():
            enable = downloader_info.get('enable')
            if (enable and self.__check_has_enabled_sub_task(downloader_info)):
                return True
        return False
    
    def get_state(self):
        """
        插件生效状态
        """
        state = True if self.__config_obj \
                       and self.__config_obj.get('enable') \
                       and (self.__config_obj.get('cron') or self.__config_obj.get("listen_download_event") or self.__config_obj.get("listen_source_file_event")) \
                       and self.__check_has_enabled_task() else False
        self.debug(f"插件状态: {state}")
        return state

    def stop_service(self):
        """
        退出插件
        """
        try:
            if self.__scheduler:
                self.__scheduler.remove_all_jobs()
                if self.__scheduler.running:
                    self.__exit_event.set()
                    self.__scheduler.shutdown()
                    self.__exit_event.clear()
                self.__scheduler = None
            self.debug(f"插件服务停止成功")
        except Exception as e:
            self.error(f"插件服务停止异常: {str(e)}")

    @staticmethod
    def __split_tags(tags = None):
        """
        分割标签tags为数组
        """
        return re.split("\s*,\s*", tags.strip()) if tags else []
    
    def __get_exclude_tag_array(self):
        """
        获取排除的标签数组
        """
        exclude_tags = self.__config_obj.get("exclude_tags")
        return self.__split_tags(exclude_tags)

    def __exists_exclude_tag(self, tags = None):
        """
        判断多个标签中是否存在被排除的标签
        """
        if (not tags):
            return False
        tags_type = type(tags)
        if (tags_type == str):
            return self.__exists_exclude_tag(self.__split_tags(tags))
        elif (tags_type == list):
            exclude_tag_array = self.__get_exclude_tag_array()
            if (not exclude_tag_array):
                return False
            for tag in tags:
                if (tag in exclude_tag_array):
                    return True
            return False
        else:
            return False

    @staticmethod
    def __check_need_seeding(torrent, downloader_type):
        """
        检查是否需要做种
        """
        if (downloader_type == DownloaderType.QB):
            return torrent.state_enum.is_complete and torrent.state_enum.is_paused
        elif (downloader_type == DownloaderType.TR):
            return torrent.progress == 100 and torrent.stopped and torrent.error == 0
        else:
            return False
    
    @staticmethod
    def __get_torrent_hash(torrent, downloader_type):
        """
        获取种子的hash
        """
        if (downloader_type == DownloaderType.QB):
            return torrent.get('hash')
        elif (downloader_type == DownloaderType.TR):
            return torrent.hashString
        else:
            None
    
    @staticmethod
    def __get_torrent_name(torrent, downloader_type):
        """
        获取种子的名称
        """
        if (downloader_type == DownloaderType.QB):
            return torrent.get('name')
        elif (downloader_type == DownloaderType.TR):
            return torrent.get('name')
        else:
            None

    def __seeding_one_for_qb(self, torrent):
        """
        qb单个做种
        """
        # 判断种子中是否存在排除的标签
        torrent_tags = self.__split_tags(torrent.get('tags'))
        if (self.__exists_exclude_tag(torrent_tags)):
            return False
        downloader_type = DownloaderType.QB
        if (not self.__check_need_seeding(torrent, downloader_type)):
            return False
        torrent.resume()
        hash = self.__get_torrent_hash(torrent, downloader_type)
        name = self.__get_torrent_name(torrent, downloader_type)
        self.info(f'[QB]单个做种完成: hash = {hash}, name = {name}')
        return True
    
    def __seeding_one_for_tr(self, torrent, downloader):
        """
        tr单个做种
        """
        # 判断种子中是否存在排除的标签
        torrent_tags = torrent.get('labels')
        if (self.__exists_exclude_tag(torrent_tags)):
            return False
        downloader_type = DownloaderType.TR
        if (not self.__check_need_seeding(torrent, downloader_type)):
            return False
        downloader.start_torrents(torrent.id)
        hash = self.__get_torrent_hash(torrent, downloader_type)
        name = self.__get_torrent_name(torrent, downloader_type)
        self.info(f'[TR]单个做种完成: hash = {hash}, name = {name}')
        return True
    
    def __seeding_batch_for_qb(self, torrents):
        """
        qb批量做种
        """
        self.info('[QB]批量做种开始...')
        count = 0
        for torrent in torrents:
            if (self.__exit_event.is_set()):
                return count
            if(self.__seeding_one_for_qb(torrent)):
                count += 1
        self.info('[QB]批量做种结束')
        return count

    def __seeding_batch_for_tr(self, downloader, torrents = None):
        """
        tr批量做种
        """
        self.info('[TR]批量做种开始...')
        if (not torrents):
            torrents = self.__get_torrents(downloader)
        count = 0
        for torrent in torrents:
            if (self.__exit_event.is_set()):
                return count
            if(self.__seeding_one_for_tr(torrent, downloader)):
                count += 1
        self.info('[TR]批量做种结束')
        return count
    
    def __seeding_batch(self, downloader, torrents = None):
        """
        批量做种
        """
        downloader_type = downloader.get_type()
        if (not torrents):
            torrents = self.__get_torrents(downloader)
        if (downloader_type == DownloaderType.QB):
            return self.__seeding_batch_for_qb(torrents)
        elif (downloader_type == DownloaderType.TR):
            return self.__seeding_batch_for_tr(downloader, torrents)
        return 0
    
    @staticmethod
    def __parse_url_query(query = None):
        """
        解析url
        :param query 字典
        """
        if (not query or len(query) <= 0):
            return {}
        return urllib.parse.parse_qs(query)

    @classmethod
    def __parse_tracker_for_qb(cls, torrent = None):
        """
        qb解析 tracker
        """
        if (not torrent):
            return None
        tracker = torrent.get('tracker')
        if (tracker and len(tracker) > 0):
            return tracker
        magnet_uri = torrent.get('magnet_uri')
        if (not magnet_uri or len(magnet_uri) <= 0):
            return None
        magnet_uri_obj = urllib.parse.urlparse(magnet_uri)
        query = cls.__parse_url_query(magnet_uri_obj.query)
        tr = query['tr']
        if (not tr or len(tr) <= 0):
            return None
        return tr[0]

    @staticmethod
    def __parse_tracker_for_tr(torrent = None):
        """
        tr解析 tracker
        """
        if (not torrent):
            return None
        trackers = torrent.trackers
        if (not trackers or len(trackers) <= 0):
            return None
        tracker = trackers[0]
        return tracker.get('announce')

    @classmethod
    def __parse_tracker(cls, torrent, downloader_type):
        """
        解析 tracker
        """
        if (downloader_type == DownloaderType.QB):
            return cls.__parse_tracker_for_qb(torrent)
        elif (downloader_type == DownloaderType.TR):
            return cls.__parse_tracker_for_tr(torrent)
        else:
            return None
    
    @staticmethod
    def __parse_hostname_from_url(url = None):
        """
        从url中解析域名
        """
        if (not url):
            return None
        url_obj = urllib.parse.urlparse(url)
        if (not url_obj):
            return None
        return url_obj.hostname

    @staticmethod
    def __parse_keyword_from_hostname(hostname = None):
        """
        从域名中解析关键字
        """
        if (not hostname):
            return None
        hostname_array = hostname.split('.')
        hostname_array_len = len(hostname_array)
        if (hostname_array_len >= 2):
            return hostname_array[-2]
        elif (hostname_array >= 1):
            return hostname_array[-1]
        else:
            return None

    @classmethod
    def __parse_keyword_from_url(cls, url = None):
        """
        从url中解析域名关键字
        """
        return cls.__parse_keyword_from_hostname(cls.__parse_hostname_from_url(url))

    @staticmethod
    def __build_site_tag_by_hostname_keyword(keyword = None):
        """
        根据域名关键字构造站点标签
        """
        if (not keyword):
            return None
        return f'站点/{keyword}'

    def __tagging_one_for_qb(self, torrent, site_dict = {}):
        """
        qb单个打标签
        """
        # 判断种子中是否存在排除的标签
        torrent_tags = self.__split_tags(torrent.get('tags'))
        if (self.__exists_exclude_tag(torrent_tags)):
            return False

        downloader_type = DownloaderType.QB
        tracker = self.__parse_tracker(torrent, downloader_type)
        keyword = self.__parse_keyword_from_url(tracker)
        if (not keyword):
            return False
        use_site_config = self.__config_obj.get("use_site_config")
        site_tag = self.__build_site_tag_by_hostname_keyword(keyword)
        site_name_tag = self.__build_site_tag_by_hostname_keyword(site_dict.get(keyword)) if site_dict else None
        result = False
        if (use_site_config and site_name_tag):
            if (site_name_tag not in torrent_tags):
                torrent.add_tags(site_name_tag)
                result = True
            if (site_tag in torrent_tags):
                torrent.remove_tags(site_tag)
                result = True
        else:
            if (site_tag not in torrent_tags):
                torrent.add_tags(site_tag)
                result = True
            if (site_name_tag in torrent_tags):
                torrent.remove_tags(site_name_tag)
                result = True
        if (not result):
            return False
        hash = self.__get_torrent_hash(torrent, downloader_type)
        name = self.__get_torrent_name(torrent, downloader_type)
        self.info(f'[QB]单个打标成功: hash = {hash}, name = {name}')
        return True

    def __tagging_one_for_tr(self, torrent, downloader, site_dict = {}):
        """
        tr单个打标签
        """
        # 判断种子中是否存在排除的标签
        torrent_tags = torrent.get('labels')
        if (self.__exists_exclude_tag(torrent_tags)):
            return False

        if (not torrent_tags):
            torrent_tags = []
        torrent_tags_copy = torrent_tags.copy()

        downloader_type = DownloaderType.TR
        tracker = self.__parse_tracker(torrent, downloader_type)
        keyword = self.__parse_keyword_from_url(tracker)
        if (not keyword):
            return False
        use_site_config = self.__config_obj.get("use_site_config")
        site_tag = self.__build_site_tag_by_hostname_keyword(keyword)
        site_name_tag = self.__build_site_tag_by_hostname_keyword(site_dict.get(keyword)) if site_dict else None
        if (use_site_config and site_name_tag):
            if (site_name_tag not in torrent_tags_copy):
                torrent_tags_copy.append(site_name_tag)
            if (site_tag in torrent_tags_copy):
                torrent_tags_copy.remove(site_tag)
        else:
            if (site_tag not in torrent_tags_copy):
                torrent_tags_copy.append(site_tag)
            if (site_name_tag in torrent_tags_copy):
                torrent_tags_copy.remove(site_name_tag)
        if (torrent_tags_copy == torrent_tags):
            return False
        downloader.set_torrent_tag(torrent.id, torrent_tags_copy)
        hash = self.__get_torrent_hash(torrent, downloader_type)
        name = self.__get_torrent_name(torrent, downloader_type)
        self.info(f'[TR]单个打标成功: hash = {hash}, name = {name}')
        return True
    
    def __tagging_batch_for_qb(self, torrents, site_dict = {}):
        """
        qb批量打标签
        """
        self.info('[QB]批量打标开始...')
        count = 0
        for torrent in torrents:
            if (self.__exit_event.is_set()):
                return count
            if (self.__tagging_one_for_qb(torrent, site_dict)):
                count += 1
        self.info('[QB]批量打标结束')
        return count
    
    def __tagging_batch_for_tr(self, downloader, torrents = None, site_dict = {}):
        """
        tr批量打标签
        """
        self.info('[TR]批量打标开始...')
        if (not torrents):
            torrents = self.__get_torrents(downloader)
        count = 0
        for torrent in torrents:
            if (self.__exit_event.is_set()):
                return count
            if (self.__tagging_one_for_tr(torrent, downloader, site_dict)):
                count += 1
        self.info('[TR]批量打标结束')
        return count

    def __tagging_batch(self, downloader, torrents = None, site_dict = {}):
        """
        批量打标签
        """
        downloader_type = downloader.get_type()
        if (not torrents):
            torrents = self.__get_torrents(downloader)
        if (downloader_type == DownloaderType.QB):
            return self.__tagging_batch_for_qb(torrents, site_dict)
        elif (downloader_type == DownloaderType.TR):
            return self.__tagging_batch_for_tr(downloader, torrents, site_dict)
        return 0
    
    @staticmethod
    def __check_is_missing_files(torrent, downloader_type):
        """
        检查种子是否丢失文件
        """
        if (downloader_type == DownloaderType.QB):
            return torrent.get('state') == 'missingFiles'
        elif (downloader_type == DownloaderType.TR):
            return torrent.error == 3 \
               and torrent.error_string != None \
               and 'No data found' in torrent.error_string
        else:
            return False

    @classmethod
    def __get_torrent_data_filename(cls, torrent, downloader_type):
        """
        获取种子数据文件(夹)名，通常和种子名称相同
        """
        return cls.__get_torrent_name(torrent=torrent, downloader_type=downloader_type);

    @classmethod
    def __check_file_match_torrent(cls, path, filename, torrent, downloader_type):
        """
        检查文件和种子是否匹配
        :return is_match 是否匹配
        :return torrent_data_path 匹配的种子数据路径
        """
        if (not path or not filename or not torrent or not downloader_type):
            return False, None
        # 种子数据文件名
        torrent_filename = cls.__get_torrent_data_filename(torrent=torrent, downloader_type=downloader_type)
        if (not torrent_filename):
            return False, None
        filepath = os.path.join(path, filename)
        if (filename == torrent_filename):
            return True, filepath
        torrent_filename_wrap1 = os.path.sep + torrent_filename
        if (path.endswith(torrent_filename_wrap1)):
            return True, path
        torrent_filename_wrap2 = torrent_filename_wrap1 + os.path.sep
        index = filepath.find(torrent_filename_wrap2)
        if (index >= 0):
            return True, filepath[0, index] + torrent_filename_wrap1
        return False, None

    @classmethod
    def __check_need_delete(cls, torrent, downloader_type, deleted_source_file=None):
        """
        检查是否需要删种
        """
        if (cls.__check_is_missing_files(torrent, downloader_type)):
            return True
        if (not deleted_source_file):
            return False
        source_path = deleted_source_file.get("path")
        source_filename = deleted_source_file.get("filename")
        is_match, torrent_data_path = cls.__check_file_match_torrent(source_path, source_filename, torrent, downloader_type)
        if (not is_match):
            return False
        # 如果匹配的种子数据路径不存在，说明数据文件已经被删除了，那么就允许删种
        return not os.path.exists(torrent_data_path)
    
    def __delete_one_for_qb(self, torrent, downloader, deleted_source_file=None):
        """
        qb单个删种
        """
        # 判断种子中是否存在排除的标签
        torrent_tags = self.__split_tags(torrent.get('tags'))
        if (self.__exists_exclude_tag(torrent_tags)):
            return False
        downloader_type = DownloaderType.QB
        if (not self.__check_need_delete(torrent=torrent, downloader_type=downloader_type, deleted_source_file=deleted_source_file)):
            return False
        hash = self.__get_torrent_hash(torrent, downloader_type)
        name = self.__get_torrent_name(torrent, downloader_type)
        downloader.delete_torrents(True, hash)
        self.info(f'[QB]单个删种完成: hash = {hash}, name = {name}')
        return True

    def __delete_one_for_tr(self, torrent, downloader, deleted_source_file=None):
        """
        tr单个删种
        """
        # 判断种子中是否存在排除的标签
        torrent_tags = torrent.get('labels')
        if (self.__exists_exclude_tag(torrent_tags)):
            return False
        downloader_type = DownloaderType.TR
        if (not self.__check_need_delete(torrent=torrent, downloader_type=downloader_type, deleted_source_file=deleted_source_file)):
            return False
        hash = self.__get_torrent_hash(torrent, downloader_type)
        name = self.__get_torrent_name(torrent, downloader_type)
        downloader.delete_torrents(True, torrent.id)
        self.info(f'[TR]单个删种完成: hash = {hash}, name = {name}')
        return True
    
    def __delete_batch_for_qb(self, downloader, torrents, deleted_source_file=None):
        """
        qb批量删种
        """
        self.info('[QB]批量删种开始...')
        if (not torrents):
            torrents = self.__get_torrents(downloader)
        count = 0
        for torrent in torrents:
            if (self.__exit_event.is_set()):
                return count
            if (self.__delete_one_for_qb(torrent=torrent, downloader=downloader, deleted_source_file=deleted_source_file)):
                count += 1
        self.info('[QB]批量删种结束')
        return count
    
    def __delete_batch_for_tr(self, downloader, torrents, deleted_source_file=None):
        """
        tr批量删种
        """
        self.info('[TR]批量删种开始...')
        if (not torrents):
            torrents = self.__get_torrents(downloader)
        count = 0
        for torrent in torrents:
            if (self.__exit_event.is_set()):
                return count
            if (self.__delete_one_for_tr(torrent=torrent, downloader=downloader, deleted_source_file=deleted_source_file)):
                count += 1
        self.info('[TR]批量删种结束')
        return count
    
    def __delete_batch(self, downloader, torrents=None, deleted_source_file=None):
        """
        批量删种
        """
        downloader_type = downloader.get_type()
        if (not torrents):
            torrents = self.__get_torrents(downloader)
        if (downloader_type == DownloaderType.QB):
            return self.__delete_batch_for_qb(downloader=downloader, torrents=torrents, deleted_source_file=deleted_source_file)
        elif (downloader_type == DownloaderType.TR):
            return self.__delete_batch_for_tr(downloader=downloader, torrents=torrents, deleted_source_file=deleted_source_file)
        return 0

    @staticmethod
    def __get_torrents(downloader = None):
        """
        从下载器中获取全部种子
        """
        if (not downloader):
            return None
        return downloader.get_torrents()[0]

    def __do_task(self):
        """
        执行任务
        """
        if (self.__running_state.is_set()):
            self.debug('已有进行中的任务，本次不执行')
            return
        try:
            self.__running_state.set()
            self.__do_task_for_all_downloader()
        finally:
            self.__running_state.clear()

    def __do_task_for_all_downloader(self, sub_task_control=None, deleted_source_file=None):
        """
        针对所有下载器执行任务
        :param sub_task_control 子任务控制
        :param deleted_source_file 删除的源文件，仅针对根据源文件删除事件同步删种场景有效
        """
        # 站点词典
        site_dict = self.__get_site_dict()
        # 任务执行统计结果
        results = []
        # 下载器任务配置
        downloader_configs = self.__config_obj.get('downloader')
        for downloader_id, downloader_config in downloader_configs.items():
            result = self.__do_task_for_single_downloader(downloader_id=downloader_id, downloader_config=downloader_config, site_dict=site_dict, sub_task_control=sub_task_control, deleted_source_file=deleted_source_file)
            if (result):
                results.append(result)
        # 发送通知
        self.__send_notify(results)

    def __do_task_for_single_downloader(self, downloader_id=None, downloader_config=None, site_dict=None, sub_task_control=None, deleted_source_file=None):
        """
        针对单个下载器执行任务
        """
        if (self.__exit_event.is_set()):
            self.warn(f'任务中止')
            return None
        if (not downloader_id):
            return None
        if (not downloader_config):
            # 下载器任务配置
            downloader_configs = self.__config_obj.get('downloader')
            downloader_config = downloader_configs.get(downloader_id)
        if (not downloader_config):
            return None
        if (not site_dict):
            # 站点词典
            site_dict = self.__get_site_dict()
        if (not downloader_config.get('enable')):
            return None
        # 子任务开关处理
        enable_seeding = downloader_config.get('enable_seeding') == True and (sub_task_control == None or sub_task_control.get('enable_seeding') != False)
        enable_tagging = downloader_config.get('enable_tagging') == True and (sub_task_control == None or sub_task_control.get('enable_tagging') != False)
        enable_delete = downloader_config.get('enable_delete') == True and (sub_task_control == None or sub_task_control.get('enable_delete') != False)
        if (not enable_seeding and not enable_tagging and not enable_delete):
            return None
        downloader = self.__downloader.get_downloader(downloader_id = downloader_id)
        if (not downloader):
            self.warn(f'下载器不存在: id = {downloader_id}')
            return None
        downloader_type = downloader.get_type()
        downloader_name = downloader.name
        self.info(f'下载器[{downloader_name}]任务执行开始...')
        self.info(f'子任务执行状态: 自动做种={enable_seeding}, 自动打标={enable_tagging}, 自动删种={enable_delete}')
        if (downloader_type not in [DownloaderType.QB, DownloaderType.TR]):
            self.warn(f'下载器[{downloader_name}]类型不受支持: type = {downloader_type}')
            return None
        if (not downloader.get_status()):
            self.warn(f'下载器[{downloader_name}]状态无效')
            return None
        torrents = self.__get_torrents(downloader)
        if (not torrents or len(torrents) <= 0):
            self.warn(f'下载器[{downloader_name}]中没有种子')
            return None
        torrents_count = len(torrents)

        result = {
            'downloader_name': downloader_name,
            'total': torrents_count
        }
        # 批量做种
        if (enable_seeding):
            result['seeding'] = self.__seeding_batch(downloader=downloader, torrents=torrents)
            if (self.__exit_event.is_set()):
                return result
        # 批量打标签
        if (enable_tagging):
            result['tagging'] = self.__tagging_batch(downloader=downloader, torrents=torrents, site_dict=site_dict)
            if (self.__exit_event.is_set()):
                return result
        # 批量删种
        if (enable_delete):
            result['delete'] = self.__delete_batch(downloader=downloader, torrents=torrents, deleted_source_file=deleted_source_file)
            if (self.__exit_event.is_set()):
                return result
        self.info(f'下载器[{downloader_name}]任务执行结束')
        return result

    def __send_notify(self, results = None):
        """
        发送通知
        """
        if (self.__config_obj.get('enable_notify') and results):
            text = ''
            for result in results:
                seeding = result.get('seeding')
                tagging = result.get('tagging')
                delete = result.get('delete')
                if ((seeding and seeding > 0) or (tagging and tagging > 0) or (delete and delete > 0)):
                    downloader_name = result.get('downloader_name')
                    total = result.get('total')
                    text += f'【任务：{downloader_name}】\n'
                    text += f'种子总数：{total}\n'
                    if (seeding):
                        text += f'做种数：{seeding}\n'
                    if (tagging):
                        text += f'打标数：{tagging}\n'
                    if (delete):
                        text += f'删种数：{delete}\n'
                    text += '\n'
                    text += '————————————\n'
            if (text):
                self.send_message(
                    title = f"{self.module_name}任务执行结果",
                    text = text
                )

    def __get_site_dict(self):
        """
        获取站点词典
        """
        site_infos = Sites().get_sites()
        if (site_infos):
            return {self.__parse_keyword_from_url(site_info.get("signurl")): site_info.get("name") for site_info in site_infos}
        return {}

    @EventHandler.register(EventType.DownloadAdd)
    def listen_download_add_event(self, event):
        """
        监听下载添加事件
        """
        if (not event or not event.event_data):
            return
        if (not self.get_state() or not self.__config_obj.get("listen_download_event")):
            return
        if (not self.__scheduler or not self.__scheduler.running):
            return
        if (self.__exit_event.is_set()):
            return
        downloader_id = event.event_data.get('downloader_id')
        sub_task_control = {
            'enable_seeding': False,
            'enable_tagging': True,
            'enable_delete': False
        }
        def __do_task():
            if (downloader_id):
                self.__do_task_for_single_downloader(downloader_id=downloader_id, sub_task_control=sub_task_control)
            else:
                self.__do_task_for_all_downloader(sub_task_control=sub_task_control)
        timezone = Config().get_timezone()
        self.__scheduler.add_job(__do_task, 'date', run_date = datetime.now(tz = pytz.timezone(timezone)) + timedelta(seconds = 3))
        self.info('监听到下载添加事件，触发插件任务')

    @EventHandler.register(EventType.SourceFileDeleted)
    def listen_source_file_deleted_event(self, event):
        """
        监听源文件删除事件，同步删种
        """
        # 检查事件数据，如果不满足执行条件就抛弃事件
        if (not event or not event.event_data):
            return
        source_path = event.event_data.get("path")
        source_filename = event.event_data.get("filename")
        if (not source_path or not source_filename):
            return
        # 检查插件配置及状态
        if (not self.get_state() or not self.__config_obj.get("listen_source_file_event")):
            return
        if (not self.__scheduler or not self.__scheduler.running):
            return
        if (self.__exit_event.is_set()):
            return
        # 针对全部下载器处理
        sub_task_control = {
            'enable_seeding': False,
            'enable_tagging': False,
            'enable_delete': True
        }
        def __do_task():
            self.__do_task_for_all_downloader(sub_task_control=sub_task_control, deleted_source_file=event.event_data)
        timezone = Config().get_timezone()
        self.__scheduler.add_job(__do_task, 'date', run_date = datetime.now(tz = pytz.timezone(timezone)) + timedelta(seconds = 3))
        self.info('监听到源文件删除事件，触发插件任务')
