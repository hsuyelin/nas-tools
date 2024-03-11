import os
from app.plugins.modules._base import _IPluginModule
from threading import Event
from app.utils import SystemUtils
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime, timedelta
from app.mediaserver import MediaServer
import functools
from jinja2 import Template
from app.utils import StringUtils
import re

def ResponseBody(func):
    """
    rest api 结果包装
    """
    def wrapper(*args, **kwargs):
        try:
            data = func(*args, **kwargs)
            return {'code': 0, 'data': data}
        except Exception as e:
            return {'code': 1, 'msg': str(e)}
    return wrapper

class MediaLibraryArchive(_IPluginModule):
    # 插件名称
    module_name = "媒体库归档"
    # 插件描述
    module_desc = "定期归档媒体库，留存记录以备查验。"
    # 插件图标
    module_icon = "'); background-image: url('data:image/png;base64,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eIv3aBefQhH1Z4cOxq+HX/u8PHI8Dp8arJ+tn5qCuHfOaIu5MzpifktX/dbIItxvaVsUPW2ubTM6EYcLUER9XceS+ueNjtVOxuGRgdeiXivCPnD652AcGhmIwRipn1EXgS5C/fq/7or5LZ31/z5cCEcMTJE5MzpiTltH9JhQGshFNYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDE2ixe87vttk9VfQqAMTgTB0hMxAESE3GAxEQcIDERb5BFi+ZXYpxwoRYsmGvOJkHEG2TNmisqMU64UKtW9ZizSRDxBnGgwuhWrVo+6t/n/Ih4g6xYcVklxgkXauVKEZ8MEW+Q9evXxerVzsbhbNddtzZuueUd5mQSRLxBuru7YsOGuyoxVjhfGzbcHe3tHhyfDBFvoLVrr4yNG++uzHhhPF/4wsZYtmzJOL+C8yHiDXb77e+tH7xQZcXJzA03XOsYmAIzarVaLf0oEtqzZ39s2vRAbN26repTQYUU3wsVlxWL/ytlaoj4NBoaGo4tWx6L3t7dsXNn8dkVhw4drex8UD7FQ27FMxLFLbbFHVrFF/zF90NMHREHSMw1cYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYDERBwgMREHSEzEARITcYCsIuJ/ABNC/3gAaOENAAAAAElFTkSuQmCC"
    # 主题色
    module_color = "#1592a6"
    # 插件版本
    module_version = "1.1"
    # 插件作者
    module_author = "hotlcc"
    # 作者主页
    author_url = "https://gitee.com/hotlcc"
    # 插件配置项ID前缀
    module_config_prefix = "com.hotlcc.media-library-archive."
    # 加载顺序
    module_order = 22
    # 可使用的用户级别
    user_level = 2

    # 私有属性
    __timezone = None
    # 调度器
    __scheduler = None
    # 退出事件
    __exit_event = Event()
    # 任务运行中状态
    __running_state = Event()

    # 配置对象
    __config_obj = None

    @classmethod
    def get_fields(cls):
        default_archive_path = cls.__get_default_archive_path()
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
                            'type': 'text',
                            'title': '归档周期',
                            'required': 'required',
                            'tooltip': '设置自动归档执行周期，支持5位cron表达式；应避免任务执行过于频繁',
                            'content': [
                                {
                                    'id': 'cron',
                                    'placeholder': '0 0 * * *',
                                }
                            ]
                        },
                        {
                            'type': 'text',
                            'title': '最大保留归档数',
                            'tooltip': '最大保留归档数量，优先删除较早归档（缺省时为10）。',
                            'content': [
                                {
                                    'id': 'max_count',
                                    'placeholder': '10',
                                }
                            ]
                        },
                        {
                            'title': '自定义归档路径',
                            'tooltip': f'自定义归档路径（缺省时为：{default_archive_path}）',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'archive_path',
                                    'placeholder': default_archive_path,
                                }
                            ]
                        } if not SystemUtils.is_docker() else {}
                    ]
                ]
            }
        ]
        return fields

    @classmethod
    def __get_default_archive_path(cls):
        """
        获取默认归档路径
        """
        return os.path.join(Config().get_config_path(), 'archive_file', 'media_library')

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

    def __check_config(self, config):
        """
        检查配置
        """
        if (not config):
            return True
        max_count = config.get('max_count')
        if (max_count):
            try:
                int(max_count)
            except Exception as e:
                self.error('最大保留归档数必须为数字')
                return False
        return True

    def init_config(self, config = None):
        self.debug(f"初始化配置")
        self.__timezone = Config().get_timezone()
        self.__config_obj = config or {}

        # 停止现有任务
        self.stop_service()
        self.debug(f"停止现有服务成功")

        # 检查配置
        check_result = self.__check_config(config)
        if (not check_result):
            self.error('插件配置有误')
            return

        # 启动插件服务
        if (self.get_state()):
            self.__init_scheduler(self.__timezone)
            cron = self.__config_obj.get('cron')
            self.__scheduler.add_job(self.__do_task, CronTrigger.from_crontab(cron))
            self.info(f"定时任务已启动，周期: cron = {cron}")
        else:
            self.warn(f"插件配置无效，服务未启动")

        # 如果需要立即运行一次
        if (self.__config_obj.get('run_once')):
            self.__init_scheduler(self.__timezone)
            self.__scheduler.add_job(self.__do_task, 'date', run_date = datetime.now(tz = pytz.timezone(self.__timezone)) + timedelta(seconds = 3))
            self.info(f"立即运行一次成功")
            # 关闭一次性开关
            self.__config_obj['run_once'] = False
            self.update_config(self.__config_obj)

        # 启动服务调度器
        if (self.__scheduler):
            self.__scheduler.print_jobs()
            self.__scheduler.start()
            self.debug(f"服务调度器初启动成功")

    def get_state(self):
        """
        插件生效状态
        """
        state = True if self.__config_obj \
                        and self.__config_obj.get('enable') \
                        and self.__config_obj.get('cron') else False
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

    def __do_task(self):
        """
        执行任务
        """
        if (self.__running_state.is_set()):
            self.debug('已有进行中的任务，本次不执行')
            return
        try:
            self.info('执行任务开始')
            self.__running_state.set()
            archive_file = self.__do_archive()
            if (not archive_file):
                return
            clear_count = self.__do_clear()
            self.__send_notify(archive_file, clear_count)
        finally:
            self.__running_state.clear()
            self.info('执行任务结束')

    def __do_archive(self):
        """
        执行归档
        :return 归档文件路径
        """
        media_server = MediaServer()
        if (not media_server or not media_server.server):
            self.warn('媒体服务器不存在，请配置')
            return None
        media_trees = self.__build_media_trees(media_server)
        if (not media_trees):
            self.warn('媒体服务器中不存在媒体库，无需归档')
            return None
        self.info('从媒体服务器获取数据完成')
        archive_file = self.__save_archive_file(media_trees)
        self.info(f'归档文件生成完成: {archive_file}')
        return archive_file

    def __build_media_trees(self, media_server: MediaServer):
        """
        构造媒体树
        """
        if (not media_server or not media_server.server):
            return None
        libraries = media_server.get_libraries()
        if (not libraries):
            return None
        media_trees = []
        for library in libraries:
            if (not library):
                continue
            id = library.get('id')
            name = library.get('name')
            if (not id or not name):
                continue
            media_trees.append({
                'name': name,
                'children': self.__get_media_items(parent = id, media_server = media_server)
            })
        return media_trees

    def __cmp_obj(self, obj1, obj2):
        """
        比较对象
        """
        if (not obj1):
            return 1
        if (not obj2):
            return -1
        return 0

    def __get_media_items(self, parent, media_server: MediaServer):
        """
        级联获取媒体库中全部items
        """
        if (not parent or not media_server):
            return None
        items = media_server.get_items(parent)
        items = list(items)
        # 按照年份排序
        def cmp_item(item1, item2):
            cmp = self.__cmp_obj(item1, item2)
            if (cmp == 0):
                year1 = item1.get('year')
                year2 = item2.get('year')
                cmp = self.__cmp_obj(year1, year2)
                if (cmp == 0 and year1 != year2):
                    cmp = 1 if year1 > year2 else -1
            if (cmp == 0):
                title1 = item1.get('title')
                title2 = item2.get('title')
                cmp = self.__cmp_obj(title1, title2)
                if (cmp == 0 and title1 != title2):
                    cmp = 1 if title1 > title2 else -1
            return cmp
        items.sort(key = functools.cmp_to_key(cmp_item))
        media_items = []
        for item in items:
            if (not item):
                continue
            id = item.get('id')
            name = self.__build_item_name(item)
            if (not id or not name):
                continue
            """
            media_items.append({
                'name': name,
                'children': self.__get_media_items(parent = id, media_server = media_server)
            })
            """
            media_items.append({
                'name': name
            })
        return media_items

    def __build_item_name(self, item = None):
        """
        构造item名称
        """
        if (not item):
            return None
        title = item.get('title')
        if (not title):
            return None
        name = title
        year = item.get('year')
        if (year):
            name += f' ({year})'
        tmdbid = item.get('tmdbid')
        if (tmdbid):
            name += f' [TMDB:{tmdbid}]'
        imdbid = item.get('imdbid')
        if (imdbid):
            name += f' [IMDB:{imdbid}]'
        return name

    def __get_archive_path(self):
        """
        获取归档目录
        """
        if (SystemUtils.is_docker()):
            return self.__get_default_archive_path()
        else:
            archive_path = self.__config_obj.get('archive_path')
            if (archive_path):
                return archive_path
            else:
                return self.__get_default_archive_path()
    
    def __get_or_create_archive_path(self):
        """
        获取归档目录，不存在时创建
        """
        archive_path = self.__get_archive_path()
        if (not os.path.exists(archive_path)):
            os.makedirs(archive_path, exist_ok=True)
        return archive_path

    def __save_archive_file(self, media_trees = None):
        """
        保存归档文件
        :return archive_file
        """
        markdown_content = self.__build_markdown_content(media_trees)
        if (not markdown_content):
            return None
        archive_path = self.__get_or_create_archive_path()
        datetime_str = datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = f"归档_{datetime_str}.md"
        file_path = os.path.join(archive_path, file_name)
        with open(file_path, 'w', encoding = 'utf8') as file:
            file.write(markdown_content)
        return file_path

    def __build_markdown_content(self, media_trees, prefix = None):
        """
        构建md内容
        """
        if (not media_trees):
            return None
        if (not prefix):
            prefix = '- '
        content = ''
        for tree in media_trees:
            if (not tree):
                continue
            name = tree.get('name')
            if (not name):
                continue
            content += prefix + name + '\n'
            children = tree.get('children')
            if (not children):
                continue
            content += self.__build_markdown_content(children, '  ' + prefix)
        return content

    def __send_notify(self, archive_file, clear_count):
        """
        发送通知
        """
        if (self.__config_obj.get('enable_notify')):
            text = f'归档文件: {archive_file}\n' \
                 + f'清理数量: {clear_count}'
            self.send_message(
                title = f"{self.module_name}任务执行完成",
                text = text
            )

    def get_page(self):
        """
        归档记录页面
        """
        archive_files = self.__get_archive_files() or []
        template = """
            <div class="modal-body">
                <table class="table table-vcenter card-table table-hover table-striped">
                <thead>
                    <tr>
                        <th>归档名称</th>
                        <th>归档大小</th>
                        <th>归档时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for archive_file in archive_files %}
                    <tr title="{{ archive_file.path }}">
                        <td>{{ archive_file.name }}</td>
                        <td>{{ archive_file.size }}</td>
                        <td>{{ archive_file.createTime }}</td>
                        <td>
                            <a data-name="{{ archive_file.name }}" href="javascript:void(0);" onclick="MediaLibraryArchive.remove(this)">删除</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
                </table>
            </div>
        """
        return '归档记录', Template(template).render(archive_files = archive_files), "MediaLibraryArchive.goBack()"

    @staticmethod
    def get_script():
        """
        页面JS脚本
        """
        return """
            (function() {
                var MediaLibraryArchive = {
                    id: "MediaLibraryArchive"
                }
                window.MediaLibraryArchive = MediaLibraryArchive;
                
                var goBack = function() {
                    $("#modal-plugin-page").modal('hide');
                    $("#modal-plugin-" + MediaLibraryArchive.id).modal('show');
                };
                MediaLibraryArchive.goBack = goBack;
                
                var remove = function(elem) {
                    var $elem = $(elem),
                        file_name = $elem.attr("data-name"),
                        $tr = $elem.parent().parent();
                    ajax_post("run_plugin_method", {"plugin_id": MediaLibraryArchive.id, 'method': 'remove_archive_file_for_api', "file_name": file_name}, function (ret) {
                        if (ret.result.code === 0) {
                            $tr.remove();
                            show_success_modal("归档删除成功！");
                        } else {
                            show_fail_modal(ret.result.msg);
                        }
                    });
                };
                MediaLibraryArchive.remove = remove;
            })();
        """

    def __get_archive_files(self):
        """
        获取归档的文件信息
        """
        archive_path = self.__get_or_create_archive_path()
        file_names = os.listdir(archive_path)
        if (not file_names):
            return None
        archive_files = []
        for file_name in file_names:
            if (not file_name):
                continue
            file_path = os.path.join(archive_path, file_name)
            if (os.path.exists(file_path) and os.path.isfile(file_path) and re.fullmatch('归档_\\d{14}\.md', file_name)):
                size = os.path.getsize(file_path)
                datetime_str = file_name.replace('归档_', '').replace('.md', '')
                archive_files.append({
                    'name': file_name,
                    'path': file_path,
                    'size': StringUtils.str_filesize(size),
                    'cmp_value': int(datetime_str),
                    'createTime': datetime.strftime(datetime.strptime(datetime_str,'%Y%m%d%H%M%S'), '%Y-%m-%d %H:%M:%S')
                })
        archive_files.sort(key = lambda archive_file: archive_file.get('cmp_value'), reverse = True)
        return archive_files

    def __remove_archive_file(self, file_name):
        """
        移除归档文件
        :param file_name: 归档文件名
        """
        if (not file_name):
            return False
        archive_path = self.__get_or_create_archive_path()
        file_path = os.path.join(archive_path, file_name)
        if (os.path.exists(file_path) and os.path.isfile(file_path) and re.fullmatch('归档_\\d{14}\.md', file_name)):
            os.remove(file_path)
            self.info(f'归档文件[{file_name}]移除成功')
            return True
        else:
            self.warn(f'归档文件[{file_name}]不存在，无需移除')
            return False

    @ResponseBody
    def remove_archive_file_for_api(self, file_name):
        """
        提供给接口 移除归档文件
        """
        return self.__remove_archive_file(file_name)

    def __get_max_count(self):
        """
        获取最大归档限制数量
        """
        max_count = self.__config_obj.get('max_count')
        if (not max_count):
            return 10
        if (type(max_count) != int):
            max_count = int(max_count)
        return max_count

    def __do_clear(self):
        """
        清理超出数量的归档文件
        """
        max_count = self.__get_max_count()
        archive_files = self.__get_archive_files()
        if (not archive_files):
            return 0
        archive_path = self.__get_or_create_archive_path()
        index = 0
        clear_count = 0
        for archive_file in archive_files:
            index += 1
            if (index <= max_count):
                continue
            file_path = os.path.join(archive_path, archive_file.get('name'))
            try:
                os.remove(file_path)
                clear_count += 1
            except Exception as e:
                self.error(f'清理超出数量的归档文件发生异常: {str(e)}')
        self.info(f'清理超出数量的归档记录完成，清理数量：{clear_count}')
        return clear_count
