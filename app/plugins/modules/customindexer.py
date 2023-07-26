import re
import json

from app.plugins.modules._base import _IPluginModule
from app.helper import DbHelper
from app.utils import JsonUtils
from jinja2 import Template

from web.backend.user import User

class Customindexer(_IPluginModule):
    # 插件名称
    module_name = "自定义索引器"
    # 插件描述
    module_desc = "用于自定义索引器规则，可达到支持更多站点的效果。"
    # 插件图标
    module_icon = "customindexer.png"
    # 主题色
    module_color = "#00ADEF"
    # 插件版本
    module_version = "1.3"
    # 插件作者
    module_author = "mattoid"
    # 作者主页
    author_url = "https://github.com/Mattoids"
    # 插件配置项ID前缀
    module_config_prefix = "customindexer_"
    # 加载顺序
    module_order = 17
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _config = {}

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
                            'title': '站点域名',
                            'required': "required",
                            'tooltip': "请填写需要定义的站点域名",
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'site',
                                    'placeholder': '需要索引的站点域名！',
                                }
                            ]
                        },
                    ],
                    [
                        {
                            'title': '原始站点',
                            'required': "",
                            'tooltip': "复制原有站点的索引规则，为空则不复制规则且站点索引规则不允许为空",
                            'type': 'text',
                            'content': [
                                {
                                    'id': 'old_site',
                                    'placeholder': '要复制的站点域名',
                                }
                            ]
                        },
                    ],
                    [
                        {
                            'title': '站点索引规则',
                            'required': "填写索引器规则，若原始站点不为空，则该项允许不填写",
                            'tooltip': "设置自定义索引规则",
                            'type': 'textarea',
                            'content':
                                {
                                    'id': 'indexer',
                                    'placeholder': '',
                                }
                        },
                    ]
                ]
            }
        ]

    def get_page(self):
        """
        插件的额外页面，返回页面标题和页面内容
        :return: 标题，页面内容，确定按钮响应函数
        """
        results = []
        for inexer in DbHelper().get_indexer_custom_site():
            results.append({
                "id": inexer.ID,
                "site": inexer.SITE,
                "indexer": inexer.INDEXER,
                "date": inexer.DATE
            })

        template = """
          <div class="table-responsive table-modal-body">
            <table class="table table-vcenter card-table table-hover table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>站点</th>
                    <th>索引规则</th>
                    <th>添加时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                    {% if HistoryCount > 0 %}
                    {% for Item in IndexerHistory %}
                        <tr id="indexer_history_{{ Item.id }}">
                            <td class="w-5">
                                {{ Item.id }}
                            </td>
                            <td>
                                {{ Item.site }}
                            </td>
                            <td>
                                <div style="height:40px;overflow:hidden;text-overflow:ellipsis;">
                                    {{ Item.indexer }}
                                </div>
                            </td>
                            <td>
                                {{ Item.date or '' }}
                            </td>
                            <td>
                                <div class="dropdown">
                                <a href="#" class="btn-action" data-bs-toggle="dropdown"
                                   aria-expanded="false">
                                  <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-dots-vertical {{ class }}"
                                       width="24" height="24" viewBox="0 0 24 24"
                                       stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                                    <circle cx="12" cy="12" r="1"></circle>
                                    <circle cx="12" cy="19" r="1"></circle>
                                    <circle cx="12" cy="5" r="1"></circle>
                                  </svg>
                                </a>
                                <div class="dropdown-menu dropdown-menu-end">
                                  <a class="dropdown-item text-danger"
                                     href='javascript:delete_site_indexer("{{ Item.id }}")'>
                                    删除
                                  </a>
                                </div>
                              </div>
                            </td>
                        </tr>
                    {% endfor %}
                    {% else %}
                        <tr>
                          <td colspan="6" align="center">没有数据</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
          </div>
        """
        return "查看配置", Template(template).render(HistoryCount=len(results),
                                                     IndexerHistory=results), None

    @staticmethod
    def get_script():
        """
        返回插件额外的JS代码
        """
        return """
        function delete_site_indexer(id) {
            ajax_post("run_plugin_method", {"plugin_id": 'Customindexer', 'method': 'delete_site_indexer', 'id': id}, function (ret) {
              $("#indexer_history_" + id).remove();
            });
        }
        
        $(function(){
            $("#customindexer_site").blur(function() {
                var site = $(this).val();
                var old_site = $("#customindexer_old_site").val();
                if (site && old_site) {
                    ajax_post("run_plugin_method", {"plugin_id": 'Customindexer', 'method': 'get_oid_indexer', 'site': site, 'old_site': old_site}, function (ret) {
                      if (ret.code == 0) {
                        $("#customindexer_indexer").val(ret.result)
                      }
                    });
                }
            })
        
            $("#customindexer_old_site").blur(function() {
                var old_site = $(this).val();
                var site = $("#customindexer_site").val();
                if (site && old_site) {
                    ajax_post("run_plugin_method", {"plugin_id": 'Customindexer', 'method': 'get_oid_indexer', 'site': site, 'old_site': old_site}, function (ret) {
                      if (ret.code == 0) {
                        $("#customindexer_indexer").val(ret.result)
                      }
                    });
                }
            })
        });
        """

    def get_oid_indexer(self, old_site=None, site=None):
        indexer = User().get_indexer(url=old_site,
                                     public=False)
        pattern = re.compile(r'http[s]?://(.*?)\.')
        match_site = pattern.match(site)
        if match_site:
            site_id = match_site.group(1)
        else:
            site_id = match_site

        if indexer:
            indexer.id = site_id
            indexer.domain = site
            return json.dumps(JsonUtils.json_serializable(indexer))
        return ""



    def delete_site_indexer(self, id):
        return DbHelper().delete_indexer_custom_site(id)


    def init_config(self, config=None):
        self.info(f"初始化{config}")
        site = config.get("site")
        indexer = config.get("indexer")

        if indexer:
            DbHelper().insert_indexer_custom_site(site, indexer)

        self.update_config({
            "site": "",
            "old_site": "",
            "indexer": ""
        })

    def get_state(self):
        return True

    def stop_service(self):
        """
        退出插件
        """
        pass
