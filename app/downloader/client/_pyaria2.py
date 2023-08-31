# -*- coding: utf-8 -*-

import json
import requests
import xmlrpc.client
from base64 import b64encode

import log
from app.utils import Torrent

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 6800
SERVER_URI_FORMAT = '%s:%s/jsonrpc'


class PyAria2(object):
    _secret = None
    _server_uri = None
    _headers = {}
    _id = None

    def __init__(self, secret=None, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """
        PyAria2 constructor.

        secret: aria2 secret token
        host: string, aria2 rpc host, default is 'localhost'
        port: integer, aria2 rpc port, default is 6800
        session: string, aria2 rpc session saving.
        """
        self._server_uri = SERVER_URI_FORMAT % (host, port)
        self._secret = "token:%s" % (secret or "")
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._secret}" if self._secret else None
        }
        self._id = 0

    def _send_request(self, method, params=None):
        self._id = (self._id + 1) % 9999
        if params is None:
            params = []
        if self._secret and self._secret not in params:
            params.insert(0, self._secret)
        payload = {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": method,
            "params": params or [],
        }
        response = requests.post(
            self._server_uri,
            data=json.dumps(payload),
            headers=self._headers,
            auth=(self._secret, ""),
        )
        response_data = response.json()
        if "error" in response_data:
            raise Exception(response_data["error"]["message"])
        return response_data.get("result")

    def addUri(self, uris, options=None, position=None):
        """
        This method adds new HTTP(S)/FTP/BitTorrent Magnet URI.

        uris: list, list of URIs
        options: dict, additional options
        position: integer, position in download queue

        return: This method returns GID of registered download.
        """
        return self._send_request("aria2.addUri", [uris, options or {}])

    def addTorrent(self, torrent, uris=None, options=None, position=None):
        """
        This method adds BitTorrent download by uploading ".torrent" file.

        torrent: bin, torrent file bin
        uris: list, list of webseed URIs
        options: dict, additional options
        position: integer, position in download queue

        return: This method returns GID of registered download.
        """
        magnet_link = Torrent.binary_data_to_magnet_link(torrent)
        return self._send_request("aria2.addUri", [[magnet_link], options or {}])

    def addMetalink(self, metalink, options=None, position=None):
        """
        This method adds Metalink download by uploading ".metalink" file.

        metalink: string, metalink file path
        options: dict, additional options
        position: integer, position in download queue

        return: This method returns list of GID of registered download.
        """
        return self._send_request("aria2.addMetalink", [metalink, options or {}, position])

    def remove(self, gid):
        """
        This method removes the download denoted by gid.

        gid: string, GID.

        return: This method returns GID of removed download.
        """
        return self._send_request("aria2.remove", [gid])

    def forceRemove(self, gid):
        """
        This method removes the download denoted by gid.

        gid: string, GID.

        return: This method returns GID of removed download.
        """
        return self._send_request("aria2.forceRemove", [gid])

    def pause(self, gid):
        """
        This method pauses the download denoted by gid.

        gid: string, GID.

        return: This method returns GID of paused download.
        """
        return self._send_request("aria2.pause", [gid])

    def pauseAll(self):
        """
        This method is equal to calling aria2.pause() for every active/waiting download.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.pauseAll")

    def forcePause(self, gid):
        """
        This method pauses the download denoted by gid.

        gid: string, GID.

        return: This method returns GID of paused download.
        """
        return self._send_request("aria2.forcePause", [gid])

    def forcePauseAll(self):
        """
        This method is equal to calling aria2.forcePause() for every active/waiting download.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.forcePauseAll")

    def unpause(self, gid):
        """
        This method changes the status of the download denoted by gid from paused to waiting.

        gid: string, GID.

        return: This method returns GID of unpaused download.
        """
        return self._send_request("aria2.unpause", [gid])

    def unpauseAll(self):
        """
        This method is equal to calling aria2.unpause() for every active/waiting download.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.unpauseAll")

    def tellStatus(self, gid, keys=None):
        """
        This method returns download progress of the download denoted by gid.

        gid: string, GID.
        keys: list, keys for method response.

        return: The method response is of type dict and it contains following keys.
        """
        params = [gid]
        if keys:
            params.append(keys)
        return self._send_request("aria2.tellStatus", params)

    def getUris(self, gid):
        """
        This method returns URIs used in the download denoted by gid.

        gid: string, GID.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        """
        params = [gid]
        return self._send_request("aria2.getUris", params)

    def getFiles(self, gid):
        """
        This method returns file list of the download denoted by gid.

        gid: string, GID.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        """
        params = [gid]
        return self._send_request("aria2.getFiles", params)

    def getPeers(self, gid):
        """
        This method returns peer list of the download denoted by gid.

        gid: string, GID.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        """
        params = [gid]
        return self._send_request("aria2.getPeers", params)


    def getServers(self, gid):
        """
        This method returns currently connected HTTP(S)/FTP servers of the download denoted by gid.

        gid: string, GID.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        """
        params = [gid]
        return self._send_request("aria2.getServers", params)

    def tellActive(self, keys=None):
        """
        This method returns the list of active downloads.

        keys: keys for method response.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        """
        params = []
        if keys:
            params.append(keys)
        return self._send_request("aria2.tellActive", params)

    def tellWaiting(self, offset, num, keys=None):
        """
        This method returns the list of waiting download, including paused downloads.

        offset: integer, the offset from the download waiting at the front.
        num: integer, the number of downloads to be returned.
        keys: keys for method response.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        """
        params = [offset, num]
        if keys:
            params.append(keys)
        return self._send_request("aria2.tellWaiting", params)

    def tellStopped(self, offset, num, keys=None):
        """
        This method returns the list of stopped download.

        offset: integer, the offset from the download waiting at the front.
        num: integer, the number of downloads to be returned.
        keys: keys for method response.

        return: The method response is of type list and its element is of type dict and it contains following keys.
        """
        params = [offset, num]
        if keys:
            params.append(keys)
        return self._send_request("aria2.tellStopped", params)

    def changePosition(self, gid, pos, how):
        """
        This method changes the position of the download denoted by gid.

        gid: string, GID.
        pos: integer, the position relative which to be changed.
        how: string.
             POS_SET, it moves the download to a position relative to the beginning of the queue.
             POS_CUR, it moves the download to a position relative to the current position.
             POS_END, it moves the download to a position relative to the end of the queue.

        return: The response is of type integer, and it is the destination position.
        """
        return self._send_request("aria2.changePosition", [gid, pos, how])

    def changeUri(self, gid, fileIndex, delUris, addUris, position=None):
        """
        This method removes URIs in delUris from and appends URIs in addUris to download denoted by gid.

        gid: string, GID.
        fileIndex: integer, file to affect (1-based)
        delUris: list, URIs to be removed
        addUris: list, URIs to be added
        position: integer, where URIs are inserted, after URIs have been removed

        return: This method returns a list which contains 2 integers. The first integer is the number of URIs deleted. The second integer is the number of URIs added.
        """
        params = [gid, fileIndex, delUris, addUris]
        if position is not None:
            params.append(position)
        return self._send_request("aria2.changeUri", params)

    def getOption(self, gid):
        """
        This method returns options of the download denoted by gid.

        gid: string, GID.

        return: The response is of type dict.
        """
        return self._send_request("aria2.getOption", [gid])

    def changeOption(self, gid, options):
        """
        This method changes options of the download denoted by gid dynamically.

        gid: string, GID.
        options: dict, the options.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.changeOption", [gid, options])

    def getGlobalOption(self):
        """
        This method returns global options.

        return: The method response is of type dict.
        """
        return self._send_request("aria2.getGlobalOption")

    def changeGlobalOption(self, options):
        """
        This method changes global options dynamically.

        options: dict, the options.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.changeGlobalOption", [options])

    def getGlobalStat(self):
        """
        This method returns global statistics such as overall download and upload speed.

        return: The method response is of type struct and contains following keys.
        """
        return self._send_request("aria2.getGlobalStat")

    def purgeDownloadResult(self):
        """
        This method purges completed/error/removed downloads to free memory.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.purgeDownloadResult")

    def removeDownloadResult(self, gid):
        """
        This method removes completed/error/removed download denoted by gid from memory.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.removeDownloadResult", [gid])

    def getVersion(self):
        """
        This method returns version of the program and the list of enabled features.

        return: The method response is of type dict and contains following keys.
        """
        return self._send_request("aria2.getVersion")

    def getSessionInfo(self):
        """
        This method returns session information.

        return: The response is of type dict.
        """
        return self._send_request("aria2.getSessionInfo")

    def shutdown(self):
        """
        This method shutdowns aria2.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.shutdown")

    def forceShutdown(self):
        """
        This method shutdowns aria2.

        return: This method returns OK for success.
        """
        return self._send_request("aria2.forceShutdown")