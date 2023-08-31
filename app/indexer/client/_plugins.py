
from app.plugins import PluginManager
from config import Config

class PluginsSpider(object):

    # 私有方法
    _level = 99
    _plugin = {}
    _proxy = None
    _indexer = None

    def __int__(self, indexer):
        self._indexer = indexer
        if indexer.proxy:
            self._proxy = Config().get_proxies()
        self._plugin = PluginManager().get_plugin_apps(self._level).get(self._indexer.parser)

    def status(self, indexer):
        try:
            plugin = PluginManager().get_plugin_apps(self._level).get(indexer.parser)
            return True if plugin else False
        except Exception as e:
            return False

    def search(self, keyword, indexer, page=0):
        try:
            result_array = PluginManager().run_plugin_method(pid=indexer.parser, method='search', keyword=keyword, indexer=indexer, page=page)
            if not result_array:
                return False, []
            return True, result_array
        except Exception as e:
            return False, []

    def sites(self):
        result = []
        try:
            plugins = PluginManager().get_plugin_apps(self._level)
            for key in plugins:
                if plugins.get(key)['installed']:
                    result_array = PluginManager().run_plugin_method(pid=plugins.get(key)['id'], method='get_indexers')
                    if result_array:
                        result.extend(result_array)
        except Exception as e:
            pass
        return result