import asyncio

from pikpakapi import PikPakApi, DownloadStatus

import log
from app.downloader.client._base import _IDownloadClient
from app.utils.types import DownloaderType
from config import Config


class PikPak(_IDownloadClient):
    
    schema = "pikpak"
    # 下载器ID
    client_id = "pikpak"
    client_type = DownloaderType.PIKPAK
    client_name = DownloaderType.PIKPAK.value
    _client_config = {}

    _client = None
    username = None
    password = None
    proxy = None
    download_dir = []
    def __init__(self, config=None):
        if config:
            self._client_config = config
        self.init_config()
        self.connect()

    def init_config(self):
        if self._client_config:
            self.username = self._client_config.get("username")
            self.password = self._client_config.get("password")
            self.proxy = self._client_config.get("proxy")
            if self.proxy:
                if not self.proxy.startswith('http'):
                    self.proxy = "http://" + self.host
                if self.proxy.endswith('/'):
                    self.proxy = self.host[:-1]
            self.download_dir = self._client_config.get('download_dir') or []
            if self.username and self.password:
                self._client = PikPakApi(
                username=self.username,
                password=self.password,
                proxy=self.proxy,
            )

    @classmethod
    def match(cls, ctype):
        return True if ctype in [cls.client_id, cls.client_type, cls.client_name] else False

    def connect(self):
        try:
            asyncio.run(self._client.login())
        except Exception as err:
            print(str(err))
            return

    def get_status(self):
        if not self._client:
            return False
        try:
            asyncio.run(self._client.login())
            if self._client.user_id is None:
                log.info("PikPak 登录失败")
                return False
        except Exception as err:
            log.error("PikPak 登录出错：%s" % str(err))
            return False

        return True

    def get_torrents(self, ids=None, status=None, **kwargs):
        rv = []
        if self._client.user_id is None:
            if self.get_status():
                return [], False

        if ids is not None:
            for id in ids:
                status = asyncio.run(self._client.get_task_status(id, ''))
                if status == DownloadStatus.downloading:
                    rv.append({"id": id, "finish": False})
                if status == DownloadStatus.done:
                    rv.append({"id": id, "finish": True})
        return rv, True

    def get_completed_torrents(self, **kwargs):
        return []

    def get_downloading_torrents(self, **kwargs):
        if self._client.user_id is None:
            if self.get_status():
                return []
        try:
            offline_list = asyncio.run(self._client.offline_list())
            return offline_list['tasks']
        except Exception as err:
            print(str(err))
            return []

    def get_transfer_task(self, **kwargs):
        pass

    def get_remove_torrents(self, **kwargs):
        return []

    def add_torrent(self, content, download_dir=None, **kwargs):
        try:
            folder = asyncio.run(
                self._client.path_to_id(download_dir, True))
            count = len(folder)
            if count == 0:
                print("create parent folder failed")
                return None
            else:
                task = asyncio.run(self._client.offline_download(
                    content, folder[count - 1]["id"]
                ))
                return task["task"]["id"]
        except Exception as e:
            log.error("PikPak 添加离线下载任务失败: %s" % str(e))
            return None

    # 需要完成
    def delete_torrents(self, delete_file, ids):
        pass

    def start_torrents(self, ids):
        pass

    def stop_torrents(self, ids):
        pass

    # 需要完成
    def set_torrents_status(self, ids, **kwargs):
        pass

    def get_download_dirs(self):
        return []

    def change_torrent(self, **kwargs):
        pass

    # 需要完成
    def get_downloading_progress(self, **kwargs):
        """
        获取正在下载的种子进度
        """
        Torrents = self.get_downloading_torrents()
        DispTorrents = []
        for torrent in Torrents:
            DispTorrents.append({
                'id': torrent.get('id'),
                'file_id': torrent.get('file_id'),
                'name': torrent.get('file_name'),
                'nomenu': True,
                'noprogress': True
            })
        return DispTorrents

    def set_speed_limit(self, **kwargs):
        """
        设置速度限制
        """
        pass

    def get_type(self):
        return self.client_type