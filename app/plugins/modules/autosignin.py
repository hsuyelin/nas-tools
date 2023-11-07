import re
import time
from datetime import datetime, timedelta
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.pool import ThreadPool
from threading import Event

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as es
from selenium.webdriver.support.wait import WebDriverWait

from app.helper import ChromeHelper, SubmoduleHelper, SiteHelper
from app.helper.cloudflare_helper import under_challenge
from app.message import Message
from app.plugins import EventHandler, EventManager
from app.plugins.modules._base import _IPluginModule
from app.sites.siteconf import SiteConf
from app.sites.sites import Sites
from app.utils import RequestUtils, ExceptionUtils, StringUtils, SchedulerUtils
from app.utils.types import EventType
from config import Config
from jinja2 import Template
import random


class AutoSignIn(_IPluginModule):
    # 插件名称
    module_name = "站点自动签到"
    # 插件描述
    module_desc = "站点自动签到保号，支持重试。"
    # 插件图标
    module_icon = "signin.png"
    # 主题色
    module_color = "#4179F4"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "thsrite"
    # 作者主页
    author_url = "https://github.com/thsrite"
    # 插件配置项ID前缀
    module_config_prefix = "autosignin_"
    # 加载顺序
    module_order = 0
    # 可使用的用户级别
    auth_level = 2

    # 上次运行结果属性
    _last_run_results_list = []

    # 私有属性
    eventmanager = None
    siteconf = None
    _scheduler = None

    # 设置开关
    _enabled = False
    # 任务执行间隔
    _site_schema = []
    _cron = None
    _sign_sites = None
    _queue_cnt = None
    _retry_keyword = None
    _special_sites = None
    _onlyonce = False
    _notify = False
    _clean = False
    _auto_cf = None
    _missed_detection = False
    _missed_schedule = None
    # 退出事件
    _event = Event()

    @staticmethod
    def get_fields():
        sites = {site.get("id"): site for site in Sites().get_site_dict()}
        return [
            {
                'type': 'div',
                'content': [
                    # 同一行
                    [
                        {
                            'title': '开启定时签到',
                            'required': "",
                            'tooltip': '开启后会根据周期定时签到指定站点。',
                            'type': 'switch',
                            'id': 'enabled',
                        },
                        {
                            'title': '漏签检测',
                            'required': "",
                            'tooltip': '开启后会在指定时段内对未签到站点进行补签（每小时一次，时间随机）。',
                            'type': 'switch',
                            'id': 'missed_detection',
                        },
                        {
                            'title': '运行时通知',
                            'required': "",
                            'tooltip': '运行签到任务后会发送通知（需要打开插件消息通知）',
                            'type': 'switch',
                            'id': 'notify',
                        },
                        {
                            'title': '立即运行一次',
                            'required': "",
                            'tooltip': '打开后立即运行一次',
                            'type': 'switch',
                            'id': 'onlyonce',
                        },
                        {
                            'title': '清理缓存',
                            'required': "",
                            'tooltip': '清理本日已签到（开启后全部站点将会签到一次)',
                            'type': 'switch',
                            'id': 'clean',
                        }
                    ]
                ]
            },
            {
                'type': 'div',
                'content': [
                    # 同一行
                    [
                        {
                            'title': '签到周期',
                            'required': "",
                            'tooltip': '自动签到时间，四种配置方法：1、配置间隔，单位小时，比如23.5；2、配置固定时间，如08:00；3、配置时间范围，如08:00-09:00，表示在该时间范围内随机执行一次；4、配置5位cron表达式，如：0 */6 * * *；配置为空则不启用自动签到功能。',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'cron',
                                    'placeholder': '0 0 0 ? *',
                                }
                            ]
                        },
                        {
                            'title': '漏签检测时段',
                            'required': "",
                            'tooltip': '配置时间范围，如08:00-23:59（每小时执行一次，执行时间随机）',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'missed_schedule',
                                    'placeholder': '08:00-23:59',
                                    'default': '08:00-23:59'
                                }
                            ]
                        },
                        {
                            'title': '签到队列',
                            'required': "",
                            'tooltip': '同时并行签到的站点数量，默认10（根据机器性能，缩小队列数量会延长签到时间，但可以提升成功率）',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'queue_cnt',
                                    'placeholder': '10',
                                }
                            ]
                        },
                        {
                            'title': '重试关键词',
                            'required': "",
                            'tooltip': '重新签到关键词，支持正则表达式；每天首次全签，后续如果设置了重试词则只签到命中重试词的站点，否则全签。',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'retry_keyword',
                                    'placeholder': '失败|错误',
                                }
                            ]
                        },
                        {
                            'title': '自动优选',
                            'required': "",
                            'tooltip': '命中重试词数量达到设置数量后，自动优化IP（0为不开启，需要正确配置自定义Hosts插件和优选IP插件）',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'auto_cf',
                                    'placeholder': '0',
                                }
                            ]
                        },
                    ]
                ]
            },
            {
                'type': 'details',
                'summary': '签到站点',
                'tooltip': '只有选中的站点才会执行签到任务，不选则默认为全选',
                'content': [
                    # 同一行
                    [
                        {
                            'id': 'sign_sites',
                            'type': 'form-selectgroup',
                            'content': sites
                        },
                    ]
                ]
            },
            {
                'type': 'details',
                'summary': '特殊站点',
                'tooltip': '选中的站点无论是否匹配重试关键词都会进行重签（如无需要可不设置）',
                'content': [
                    # 同一行
                    [
                        {
                            'id': 'special_sites',
                            'type': 'form-selectgroup',
                            'content': sites
                        },
                    ]
                ]
            },
        ]

    def get_page(self):
        """
        插件的额外页面，返回页面标题和页面内容
        :return: 标题，页面内容，确定按钮响应函数
        """

        template = """
          <div class="table-responsive table-modal-body">
            <table class="table table-vcenter card-table table-hover table-striped">
              <thead>
              {% if ResultsCount > 0 %}
              <tr>
                <th>签到时间</th>
                <th>签到站点</th>
                <th>站点地址</th>
                <th>签到结果</th>
              </tr>
              {% endif %}
              </thead>
              <tbody>
              {% if ResultsCount > 0 %}
                {% for Item in Results %}
                  <tr id="indexer_{{ Item["id"] }}">
                    <td>{{ Item["date"] }}</td>
                    <td>{{ Item["name"] }}</td>
                    <td>{{ Item["signurl"] }}</td>
                    <td>{{ Item["result"] }}</td>
                  </tr>
                {% endfor %}
              {% endif %}
              </tbody>
            </table>
          </div>
        """
        return "签到记录", Template(template).render(ResultsCount=len(self._last_run_results_list), Results=self._last_run_results_list), None

    def init_config(self, config=None):
        self.siteconf = SiteConf()
        self.eventmanager = EventManager()

        # 读取配置
        if config:
            self._enabled = config.get("enabled")
            self._cron = config.get("cron")
            self._retry_keyword = config.get("retry_keyword")
            self._sign_sites = config.get("sign_sites")
            self._special_sites = config.get("special_sites") or []
            self._notify = config.get("notify")
            self._queue_cnt = config.get("queue_cnt")
            self._onlyonce = config.get("onlyonce")
            self._clean = config.get("clean")
            self._auto_cf = config.get("auto_cf")
            self._missed_detection = config.get("missed_detection")
            self._missed_schedule = config.get("missed_schedule")

        if self.is_valid_time_range(self._missed_schedule):
            self._missed_schedule = re.sub(r'\s', '', str(self._missed_schedule)).replace('24:00', '23:59')
        else:
            self._missed_detection = False
            self._missed_schedule = None

        # 遍历列表并删除日期超过7天的字典项
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)

        for item in self._last_run_results_list[:]:
            date_str = item.get("date")
            if date_str:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                if date_obj < seven_days_ago:
                    self._last_run_results_list.remove(item)

        # 停止现有任务
        self.stop_service()

        # 启动服务
        if self._enabled or self._onlyonce:
            # 加载模块
            self._site_schema = SubmoduleHelper.import_submodules('app.plugins.modules._autosignin',
                                                                  filter_func=lambda _, obj: hasattr(obj, 'match'))
            self.debug(f"加载站点签到：{self._site_schema}")

            # 定时服务
            self._scheduler = BackgroundScheduler(timezone=Config().get_timezone())

            # 清理缓存即今日历史
            if self._clean:
                self.delete_history(key=datetime.today().strftime('%Y-%m-%d'))

            # 运行一次
            if self._onlyonce:
                self.info(f"签到服务启动，立即运行一次")
                self._scheduler.add_job(self.sign_in, 'date',
                                        run_date=datetime.now(tz=pytz.timezone(Config().get_timezone())) + timedelta(
                                            seconds=3))
            # 漏签检测服务
            if self._missed_detection and self.is_valid_time_range(self._missed_schedule):
                self.info(f"漏签检测服务启动，检测时段：{self._missed_schedule}")
                self.check_missed_signs()

            if self._onlyonce or self._clean:
                # 关闭一次性开关|清理缓存开关
                self._clean = False
                self._onlyonce = False
                    
                self.update_config({
                    "enabled": self._enabled,
                    "cron": self._cron,
                    "retry_keyword": self._retry_keyword,
                    "sign_sites": self._sign_sites,
                    "special_sites": self._special_sites,
                    "notify": self._notify,
                    "onlyonce": self._onlyonce,
                    "queue_cnt": self._queue_cnt,
                    "clean": self._clean,
                    "auto_cf": self._auto_cf,
                    "missed_detection": self._missed_detection,
                    "missed_schedule": self._missed_schedule,
                })

            # 周期运行
            if self._cron:
                self.info(f"定时签到服务启动，周期：{self._cron}")
                SchedulerUtils.start_job(scheduler=self._scheduler,
                                         func=self.sign_in,
                                         func_desc="自动签到",
                                         cron=str(self._cron))

            # 启动任务
            if self._scheduler.get_jobs():
                self._scheduler.print_jobs()
                self._scheduler.start()

    @staticmethod
    def get_command():
        """
        定义远程控制命令
        :return: 命令关键字、事件、描述、附带数据
        """
        return {
            "cmd": "/pts",
            "event": EventType.SiteSignin,
            "desc": "站点签到",
            "data": {}
        }

    @staticmethod
    def is_valid_time_range(input_str):
        input_str = re.sub(r'\s', '', input_str).replace('24:00', '23:59')

        pattern = r'^\d{2}:\d{2}-\d{2}:\d{2}$'

        # 验证时间范围是否合理
        if re.match(pattern, input_str):
            start_time, end_time = input_str.split('-')
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            if (0 <= start_hour <= 23 and 0 <= start_minute <= 59 and
                0 <= end_hour <= 23 and 0 <= end_minute <= 59 and
                (start_hour < end_hour or (start_hour == end_hour and start_minute < end_minute))):
                return True
        return False

    @staticmethod
    def calculate_time_range(time_range, current_time):
        # 解析时间范围字符串
        start_str, end_str = time_range.split('-')
        start_str = start_str.strip()
        end_str = end_str.strip()
        
        # 解析开始时间和结束时间
        start_hour, start_minute = map(int, start_str.split(':'))
        end_hour, end_minute = map(int, end_str.split(':'))

        start_time = datetime(current_time.year, current_time.month, current_time.day, start_hour, start_minute, 0)
        end_time = datetime(current_time.year, current_time.month, current_time.day, end_hour, end_minute, 59)

        if not isinstance(current_time, datetime):
            current_time = datetime.now()

        # 计算时间
        if  start_time <= current_time < end_time: # 时间段内
            start_time = current_time.replace(minute=0, second=0) + timedelta(hours=1)
            if start_time > end_time:
                start_time = datetime(current_time.year, current_time.month, current_time.day + 1, start_hour, start_minute, 0)
                end_time = datetime(current_time.year, current_time.month, current_time.day + 1, start_hour, 59, 59)
                return '时段内', start_time, end_time
            if start_time + timedelta(minutes=59, seconds=59) < end_time:
                end_time = start_time + timedelta(minutes=59, seconds=59)
            return '时段内', start_time, end_time
        elif current_time >= end_time:  # 时间段后
            start_time = datetime(current_time.year, current_time.month, current_time.day + 1, start_hour, start_minute, 0)
            end_time = datetime(current_time.year, current_time.month, current_time.day + 1, start_hour, 59, 59)
            return '时段后', start_time, end_time
        elif current_time < start_time:  # 时间段前
            start_time = datetime(current_time.year, current_time.month, current_time.day, start_hour, start_minute, 0)
            end_time = datetime(current_time.year, current_time.month, current_time.day, start_hour, 59, 59)
            return '时段前', start_time, end_time
        else:
            return None, None, None

    @EventHandler.register(EventType.SiteSignin)
    # 漏签检测服务
    def check_missed_signs(self):
        # 日期
        today = datetime.today()
        # 查看今天有没有签到历史
        today = today.strftime('%Y-%m-%d')
        today_history = self.get_history(key=today)
        # 今日没数据
        if not today_history:
            sign_sites = self._sign_sites
        else:
            # 今天已签到需要重签站点
            retry_sites = today_history['retry']
            # 今天已签到站点
            already_sign_sites = today_history['sign']
            # 今日未签站点
            no_sign_sites = [site_id for site_id in self._sign_sites if site_id not in already_sign_sites]
            # 签到站点 = 需要重签+今日未签
            sign_sites = list(set(retry_sites + no_sign_sites))
        
        if len(sign_sites) > 0:
            status, start_time, end_time = self.calculate_time_range(self._missed_schedule, datetime.now())
            if status == '时段内' and not self._onlyonce:
                self.info(f"漏签检测服务启动，即将进行补签！")
                self._scheduler.add_job(self.sign_in, 'date',
                                        run_date=datetime.now(tz=pytz.timezone(Config().get_timezone())) + timedelta(
                                            seconds=3))
            random_minute = random.randint(start_time.minute, end_time.minute)
            random_second = random.randint(0, 59)
            run_time = start_time.replace(minute=random_minute, second=random_second)
            self.info(f"下一次检测时间：{run_time.strftime('%H:%M:%S')}")
            self._scheduler.add_job(self.check_missed_signs, DateTrigger(run_date = run_time))
        else:
            status, start_time, end_time = self.calculate_time_range(self._missed_schedule, 
                                                                     datetime.now().replace(hour=0, minute=0, second=0) 
                                                                     + timedelta(days=1))
            random_minute = random.randint(start_time.minute, end_time.minute)
            random_second = random.randint(0, 59)
            run_time = start_time.replace(minute=random_minute, second=random_second)
            self.info(f"下一次检测时间：{run_time.strftime('%H:%M:%S')}")
            self._scheduler.add_job(self.check_missed_signs, DateTrigger(run_date = run_time))


    @EventHandler.register(EventType.SiteSignin)
    def sign_in(self, event=None):
        """
        自动签到
        """
        # 日期
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        # 删除昨天历史
        self.delete_history(yesterday_str)

        # 查看今天有没有签到历史
        today = today.strftime('%Y-%m-%d')
        today_history = self.get_history(key=today)
        # 今日没数据
        if not today_history:
            sign_sites = self._sign_sites
            self.info(f"今日 {today} 未签到，开始签到已选站点")
        else:
            # 今天已签到需要重签站点
            retry_sites = today_history['retry']
            # 今天已签到站点
            already_sign_sites = today_history['sign']
            # 今日未签站点
            no_sign_sites = [site_id for site_id in self._sign_sites if site_id not in already_sign_sites]
            # 签到站点 = 需要重签+今日未签+特殊站点
            sign_sites = list(set(retry_sites + no_sign_sites + self._special_sites))
            if sign_sites:
                self.info(f"今日 {today} 已签到，开始重签重试站点、特殊站点、未签站点")
            else:
                self.info(f"今日 {today} 已签到，无重新签到站点，本次任务结束")
                return

        # 查询签到站点
        sign_sites = Sites().get_sites(siteids=sign_sites)
        if not sign_sites:
            self.info("没有可签到站点，停止运行")
            return

        # 执行签到
        self.info("开始执行签到任务")
        with ThreadPool(min(len(sign_sites), int(self._queue_cnt) if self._queue_cnt else 10)) as p:
            status = p.map(self.signin_site, sign_sites)

        if status:
            self.info("站点签到任务完成！")

            # 命中重试词的站点id
            retry_sites = []
            # 命中重试词的站点签到msg
            retry_msg = []
            # 登录成功
            login_success_msg = []
            # 签到成功
            sign_success_msg = []
            # 已签到
            already_sign_msg = []
            # 仿真签到成功
            fz_sign_msg = []
            # 失败｜错误
            failed_msg = []

            sites = {site.get('name'): site.get("id") for site in Sites().get_site_dict()}
            for s in status:
                site_names = re.findall(r'【(.*?)】', s[0])
                site_id = sites.get(site_names[0], None) if site_names else None
                # 记录本次命中重试关键词的站点
                if self._retry_keyword:
                    match = re.search(self._retry_keyword, s[0])
                    if match and site_id:
                        self.debug(f"站点 {site_names[0]} 命中重试关键词 {self._retry_keyword}")
                        retry_sites.append(str(site_id))
                        # 命中的站点
                        retry_msg.append(s[0])
                        continue

                if "登录成功" in s[0]:
                    login_success_msg.append(s[0])
                elif "仿真签到成功" in s[0]:
                    fz_sign_msg.append(s[0])
                elif "签到成功" in s[0]:
                    sign_success_msg.append(s[0])
                elif "已签到" in s[0]:
                    already_sign_msg.append(s[0])
                else:
                    failed_msg.append(s[0])
                    retry_sites.append(str(site_id))

                if site_id:
                    status = re.search(r'【.*】(.*)', s[0]).group(1) or None
                    _result = {'id': site_id, 'date': s[1], 'name': site_names[0], 'signurl': s[2], 'result': status }
                    self._last_run_results_list.insert(0, _result)

            if not self._retry_keyword:
                # 没设置重试关键词则重试已选站点
                retry_sites = self._sign_sites
            self.debug(f"下次签到重试站点 {retry_sites}")

            # 存入历史
            if not today_history:
                self.history(key=today,
                             value={
                                 "sign": self._sign_sites,
                                 "retry": retry_sites
                             })
            else:
                self.update_history(key=today,
                                    value={
                                        "sign": self._sign_sites,
                                        "retry": retry_sites
                                    })

            # 触发CF优选
            if self._auto_cf and len(retry_sites) >= (int(self._auto_cf) or 0) > 0:
                # 获取自定义Hosts插件、CF优选插件，判断是否触发优选
                customHosts = self.get_config("CustomHosts")
                cloudflarespeedtest = self.get_config("CloudflareSpeedTest")
                if customHosts and customHosts.get("enable") and cloudflarespeedtest and cloudflarespeedtest.get(
                        "cf_ip"):
                    self.info(f"命中重试数量 {len(retry_sites)}，开始触发优选IP插件")
                    self.eventmanager.send_event(EventType.PluginReload,
                                                 {
                                                     "plugin_id": "CloudflareSpeedTest"
                                                 })
                else:
                    self.info(f"命中重试数量 {len(retry_sites)}，优选IP插件未正确配置，停止触发优选IP")
            # 发送通知
            if self._notify:
                # 签到详细信息 登录成功、签到成功、已签到、仿真签到成功、失败--命中重试
                signin_message = login_success_msg + sign_success_msg + already_sign_msg + fz_sign_msg + failed_msg
                if len(retry_msg) > 0:
                    signin_message.append("——————命中重试—————")
                    signin_message += retry_msg
                Message().send_site_signin_message(signin_message)

                next_run_time = self._scheduler.get_jobs()[0].next_run_time.strftime('%Y-%m-%d %H:%M:%S')
                # 签到汇总信息
                self.send_message(title="【自动签到任务完成】",
                                  text=f"本次签到数量: {len(sign_sites)} \n"
                                       f"命中重试数量: {len(retry_sites) if self._retry_keyword else 0} \n"
                                       f"强制签到数量: {len(self._special_sites)} \n"
                                       f"下次签到数量: {len(set(retry_sites + self._special_sites))} \n"
                                       f"下次签到时间: {next_run_time} \n"
                                       f"详见签到消息")
        else:
            self.error("站点签到任务失败！")

    def __build_class(self, url):
        for site_schema in self._site_schema:
            try:
                if site_schema.match(url):
                    return site_schema
            except Exception as e:
                ExceptionUtils.exception_traceback(e)
        return None

    def signin_site(self, site_info):
        """
        签到一个站点
        """
        signurl = site_info.get("signurl")
        site_module = self.__build_class(signurl)
        home_url = StringUtils.get_base_url(signurl)
        signinTime = datetime.now(tz=pytz.timezone(Config().get_timezone())).strftime('%Y-%m-%d %H:%M:%S')
        if site_module and hasattr(site_module, "signin"):
            try:
                status, msg = site_module().signin(site_info)
                # 特殊站点直接返回签到信息，防止仿真签到、模拟登陆有歧义
                return msg, signinTime, home_url
            except Exception as e:
                return f"【{site_info.get('name')}】签到失败：{str(e)}", signinTime, home_url
        else:
            return self.__signin_base(site_info), signinTime, home_url

    def __signin_base(self, site_info):
        """
        通用签到处理
        :param site_info: 站点信息
        :return: 签到结果信息
        """
        if not site_info:
            return ""
        site = site_info.get("name")
        try:
            site_url = site_info.get("signurl")
            site_cookie = site_info.get("cookie")
            ua = site_info.get("ua")
            if not site_url or not site_cookie:
                self.warn("未配置 %s 的站点地址或Cookie，无法签到" % str(site))
                return ""
            chrome = ChromeHelper()
            if site_info.get("chrome") and chrome.get_status():
                # 首页
                self.info("开始站点仿真签到：%s" % site)
                home_url = StringUtils.get_base_url(site_url)
                if "1ptba" in home_url:
                    home_url = f"{home_url}/index.php"
                if not chrome.visit(url=home_url, ua=ua, cookie=site_cookie, proxy=site_info.get("proxy")):
                    self.warn("%s 无法打开网站" % site)
                    return f"【{site}】仿真签到失败，无法打开网站！"
                # 循环检测是否过cf
                cloudflare = chrome.pass_cloudflare()
                if not cloudflare:
                    self.warn("%s 跳转站点失败" % site)
                    return f"【{site}】仿真签到失败，跳转站点失败！"
                # 判断是否已签到
                html_text = chrome.get_html()
                if not html_text:
                    self.warn("%s 获取站点源码失败" % site)
                    return f"【{site}】仿真签到失败，获取站点源码失败！"
                # 查找签到按钮
                html = etree.HTML(html_text)
                xpath_str = None
                for xpath in self.siteconf.get_checkin_conf():
                    if html.xpath(xpath):
                        xpath_str = xpath
                        break
                if re.search(r'已签|签到已得', html_text, re.IGNORECASE):
                    self.info("%s 今日已签到" % site)
                    return f"【{site}】今日已签到"
                if not xpath_str:
                    if SiteHelper.is_logged_in(html_text):
                        self.warn("%s 未找到签到按钮，模拟登录成功" % site)
                        return f"【{site}】模拟登录成功，已签到或无需签到"
                    else:
                        self.info("%s 未找到签到按钮，且模拟登录失败" % site)
                        return f"【{site}】模拟登录失败！"
                # 开始仿真
                try:
                    checkin_obj = WebDriverWait(driver=chrome.browser, timeout=6).until(
                        es.element_to_be_clickable((By.XPATH, xpath_str)))
                    if checkin_obj:
                        checkin_obj.click()
                        # 检测是否过cf
                        time.sleep(3)
                        if under_challenge(chrome.get_html()):
                            cloudflare = chrome.pass_cloudflare()
                            if not cloudflare:
                                self.info("%s 仿真签到失败，无法通过Cloudflare" % site)
                                return f"【{site}】仿真签到失败，无法通过Cloudflare！"

                        # 判断是否已签到   [签到已得125, 补签卡: 0]
                        if re.search(r'已签|签到已得', chrome.get_html(), re.IGNORECASE):
                            return f"【{site}】签到成功"
                        self.info("%s 仿真签到成功" % site)
                        return f"【{site}】仿真签到成功"
                except Exception as e:
                    ExceptionUtils.exception_traceback(e)
                    self.warn("%s 仿真签到失败：%s" % (site, str(e)))
                    return f"【{site}】签到失败！"
            # 模拟登录
            else:
                if site_url.find("attendance.php") != -1:
                    checkin_text = "签到"
                else:
                    checkin_text = "模拟登录"
                self.info(f"开始站点{checkin_text}：{site}")
                # 访问链接
                res = RequestUtils(cookies=site_cookie,
                                   headers=ua,
                                   proxies=Config().get_proxies() if site_info.get("proxy") else None
                                   ).get_res(url=site_url)
                if res and res.status_code in [200, 500, 403]:
                    if not SiteHelper.is_logged_in(res.text):
                        if under_challenge(res.text):
                            msg = "站点被Cloudflare防护，请开启浏览器仿真"
                        elif res.status_code == 200:
                            msg = "Cookie已失效"
                        else:
                            msg = f"状态码：{res.status_code}"
                        self.warn(f"{site} {checkin_text}失败，{msg}")
                        return f"【{site}】{checkin_text}失败，{msg}！"
                    else:
                        self.info(f"{site} {checkin_text}成功")
                        return f"【{site}】{checkin_text}成功"
                elif res is not None:
                    self.warn(f"{site} {checkin_text}失败，状态码：{res.status_code}")
                    return f"【{site}】{checkin_text}失败，状态码：{res.status_code}！"
                else:
                    self.warn(f"{site} {checkin_text}失败，无法打开网站")
                    return f"【{site}】{checkin_text}失败，无法打开网站！"
        except Exception as e:
            ExceptionUtils.exception_traceback(e)
            self.warn("%s 签到失败：%s" % (site, str(e)))
            return f"【{site}】签到失败：{str(e)}！"

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

    def get_state(self):
        return self._enabled and self._cron
