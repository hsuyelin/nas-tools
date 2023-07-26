import importlib

from app.plugins.modules._base import _IPluginModule
from app.helper import SubmoduleHelper
from app.utils import ExceptionUtils


class Editsignin(_IPluginModule):
    # 插件名称
    module_name = "签到站点修改"
    # 插件描述
    module_desc = "用于解决特殊站点站点更换域名后无法签到的问题。"
    # 插件图标
    module_icon = "editsignin.png"
    # 主题色
    module_color = "bg-black"
    # 插件版本
    module_version = "1.1"
    # 插件作者
    module_author = "mattoid"
    # 作者主页
    author_url = "https://github.com/Mattoids"
    # 插件配置项ID前缀
    module_config_prefix = "editsignin_"
    # 加载顺序
    module_order = 18
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _config = {}
    _site_url = {}
    _site_schema = []
    _site_schema_map = {}

    @staticmethod
    def get_fields():
        return [
            # 同一板块
            {
                'type': 'div',
                'content': [
                    [
                        {
                            'title': '站点',
                            'required': "required",
                            'tooltip': '需要替换的站点',
                            'type': 'select',
                            'content': [
                                {
                                    'id': 'site',
                                    'options': Editsignin._site_url,
                                    'default': '52pt.site'
                                }
                            ]
                        },
                    ],
                    [
                        {
                            'title': '新站域名',
                            'required': "required",
                            'tooltip': '不要 http:// 和结尾的 / ，仅填写域名部分，具体参考站点信息；注意：重启后生效',
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'new_site',
                                    'placeholder': 'ptchdbits.co  #不要 http:// 和结尾的 /',
                                }
                            ]
                        }
                    ],
                    [
                        {
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'tip',
                                    'default': '当前插件修改完成后，需重启 NASTool 生效',
                                    'placeholder': '当前插件修改完成后，需重启 NASTool 以后生效'
                                }
                            ]
                        }
                    ]
                ]
            }
        ]

    @staticmethod
    def get_script():
        """
        返回插件额外的JS代码
        """
        return """
            $(function(){
                $("#editsignin_tip").css('color', 'red');
                $("#editsignin_tip").attr('readonly', true)
            })
        """

    def __build_class(self):
        for site_schema in self._site_schema:
            try:
                self._site_url[site_schema.site_url] = site_schema.site_url
                self._site_schema_map[site_schema.site_url] = site_schema
            except Exception as e:
                ExceptionUtils.exception_traceback(e)
        return None

    def init_config(self, config=None):
        site = config.get('site')
        new_site = config.get('new_site')

        self._site_schema = SubmoduleHelper.import_submodules('app.plugins.modules._autosignin',
                                                              filter_func=lambda _, obj: hasattr(obj, 'match'))

        self.__build_class()

        # 获取文件签到组件的文件名
        if site and new_site:
            filename = f"{self._site_schema_map[site].__module__.split('.')[-1]}.py"
            file = importlib.resources.files('app.plugins.modules._autosignin').joinpath(filename)

            # 临时存储的文件内容
            file_data = ""
            # 查找所在文件的位置
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.find(site) != -1:
                        line = line.replace(site, new_site)
                    file_data += line
            # 更新文件内容
            with open(file, "w", encoding="utf-8") as f:
                f.write(file_data)

        self.update_config({
            "site": "",
            "new_site": ""
        })




    def get_state(self):
        return False

    def stop_service(self):
        """
        退出插件
        """
        pass