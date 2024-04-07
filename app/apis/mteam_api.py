# coding: utf-8
import json
import os
import shutil
from datetime import datetime

import re
import log
from app.helper import ChromeHelper, SiteHelper, DbHelper
from app.message import Message
from app.sites.site_limiter import SiteRateLimiter
from app.utils import RequestUtils, StringUtils, PathUtils, ExceptionUtils
from app.utils.commons import singleton
from config import Config, RMT_SUBEXT
from urllib import parse

class MTeamApi:
    # 测试站点连通性
    @staticmethod
    def test_mt_connection(site_info):
        # 计时
        start_time = datetime.now()
        site_url = StringUtils.get_base_url(site_info.get("signurl")) + "/api/system/hello"
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": site_info.get("ua"),
            "x-api-key": site_info.get("apikey"),
            "Accept": "application/json"
        }
        res = RequestUtils(headers=headers,
                           proxies=Config().get_proxies() if site_info.get("proxy") else None
                           ).post_res(url=site_url)
        seconds = int((datetime.now() - start_time).microseconds / 1000)
        if res and res.status_code == 200:
            msg = res.json().get("message") or "null"
            if msg == "SUCCESS":
                return True, "连接成功", seconds
            else:
                return False, msg, seconds
        elif res is not None:
            return False, f"连接失败，状态码：{res.status_code}", seconds
        else:
            return False, "无法打开网站", seconds

    # 根据种子详情页查询种子地址
    @staticmethod
    def get_torrent_url_by_detail_url(base_url, detailurl, site_info):
        m = re.match(".+/detail/([0-9]+)", detailurl)
        if not m:
            log.warn(f"【MTeanApi】 获取馒头种子连接失败 path：{detailurl}")
            return ""
        torrentid = int(m.group(1))
        apikey = site_info.get("apikey")
        if not apikey:
            log.warn(f"【MTeanApi】 {torrentid}未设置站点Api-Key，无法获取种子连接")
            return ""
        downloadurl = "%s/api/torrent/genDlToken" % base_url
        res = RequestUtils(
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": site_info.get("ua"),
                "x-api-key": site_info.get("apikey"),
            },
            proxies=Config().get_proxies() if site_info.get("proxy") else None,
            timeout=30
        ).post_res(url=downloadurl, data=("id=%d" % torrentid))
        if res and res.status_code == 200:
            res_json = res.json()
            msg = res_json.get('message')
            torrent_url = res_json.get('data')
            if msg != "SUCCESS":
                log.warn(f"【MTeanApi】 {torrentid}获取种子连接失败：{msg}")
                return ""
            log.info(f"【MTeanApi】 {torrentid} 获取馒头种子连接成功: {torrent_url}")
            return torrent_url
        elif res is not None:
            log.warn(f"【MTeanApi】 {torrentid}获取种子连接失败，错误码：{res.status_code}")
        else:
            log.warn(f"【MTeanApi】 {torrentid}获取种子连接失败，无法连接 {base_url}")
        return ""

    # 拉取馒头字幕列表
    @staticmethod
    def get_subtitle_list(base_url, torrentid, ua, apikey):
        subtitle_list = []
        site_url = "%s/api/subtitle/list" % base_url
        res = RequestUtils(
            headers={
                'x-api-key': apikey,
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": ua,
                "Accept": "application/json"
            },
            timeout=30
        ).post_res(url=site_url, data=("id=%d" % torrentid))
        if res and res.status_code == 200:
            msg = res.json().get('message')
            if msg != "SUCCESS":
                log.warn(f"【MTeanApi】 获取馒头{torrentid}字幕列表失败：{msg}")
                return subtitle_list
            results = res.json().get('data', [])
            for result in results:
                subtitle = {
                    "id": result.get("id"),
                    "filename": result.get("filename"),
                }
                subtitle_list.append(subtitle)
            log.info(f"【MTeanApi】 获取馒头{torrentid}字幕列表成功，捕获：{len(subtitle_list)}条字幕信息")
        elif res is not None:
            log.warn(f"【MTeanApi】 获取馒头{torrentid}字幕列表失败，错误码：{res.status_code}")
        else:
            log.warn(f"【MTeanApi】 获取馒头{torrentid}字幕列表失败，无法连接 {site_url}")
        return subtitle_list

    # 下载单个馒头字幕
    @staticmethod
    def download_single_subtitle(base_url, torrentid, subtitle_info, ua, apikey, download_dir):
        subtitle_id = int(subtitle_info.get("id"))
        filename = subtitle_info.get("filename")
        # log.info(f"【Sites】开始下载馒头{torrentid}字幕 {filename}")
        site_url = "%s/api/subtitle/dl?id=%d" % (base_url, subtitle_id)
        res = RequestUtils(
            headers={
                'x-api-key': apikey,
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": ua,
                "Accept": "*/*"
            },
            timeout=30
        ).get_res(site_url)
        if res and res.status_code == 200:
            # 创建目录
            if not os.path.exists(download_dir):
                os.makedirs(download_dir, exist_ok=True)
            # 保存ZIP
            file_name = filename
            if not file_name:
                log.warn(f"【MTeanApi】 馒头{torrentid} 字幕文件非法：{subtitle_id}")
                return
            save_tmp_path = Config().get_temp_path()
            if file_name.lower().endswith(".zip"):
                # ZIP包
                zip_file = os.path.join(save_tmp_path, file_name)
                # 解压路径
                zip_path = os.path.splitext(zip_file)[0]
                with open(zip_file, 'wb') as f:
                    f.write(res.content)
                # 解压文件
                shutil.unpack_archive(zip_file, zip_path, format='zip')
                # 遍历转移文件
                for sub_file in PathUtils.get_dir_files(in_path=zip_path, exts=RMT_SUBEXT):
                    target_sub_file = os.path.join(download_dir,
                                                   os.path.splitext(os.path.basename(sub_file))[0])
                    log.info(f"【MTeanApi】 馒头{torrentid} 转移字幕 {sub_file} 到 {target_sub_file}")
                    SiteHelper.transfer_subtitle(sub_file, target_sub_file)
                # 删除临时文件
                try:
                    shutil.rmtree(zip_path)
                    os.remove(zip_file)
                except Exception as err:
                    ExceptionUtils.exception_traceback(err)
            else:
                sub_file = os.path.join(save_tmp_path, file_name)
                # 保存
                with open(sub_file, 'wb') as f:
                    f.write(res.content)
                target_sub_file = os.path.join(download_dir,
                                               os.path.splitext(os.path.basename(sub_file))[0])
                log.info(f"【MTeanApi】 馒头{torrentid} 转移字幕 {sub_file} 到 {target_sub_file}")
                SiteHelper.transfer_subtitle(sub_file, target_sub_file)
        elif res is not None:
            log.warn(f"【MTeanApi】 下载馒头{torrentid}字幕 {filename} 失败，错误码：{res.status_code}")
        else:
            log.warn(f"【MTeanApi】 下载馒头{torrentid}字幕 {filename} 失败，无法连接 {site_url}")

    # 下载馒头字幕
    @staticmethod
    def download_subtitle(media_info, site_id, cookie, ua, apikey, download_dir):
        addr = parse.urlparse(media_info.page_url)
        log.info(f"【Sites】下载馒头字幕 {media_info.page_url}")
        # /detail/770**
        m = re.match("/detail/([0-9]+)", addr.path)
        if not m:
            log.warn(f"【MTeanApi】 获取馒头字幕失败 path：{addr.path}")
            return
        torrentid = int(m.group(1))
        if not apikey:
            log.warn(f"【MTeanApi】 获取馒头字幕失败, 未设置站点Api-Key")
            return
        base_url = StringUtils.get_base_url(media_info.page_url)
        subtitle_list = MTeamApi.get_subtitle_list(base_url, torrentid, ua, apikey)
        # 下载所有字幕文件
        for subtitle_info in subtitle_list:
            MTeamApi.download_single_subtitle(base_url, torrentid, subtitle_info, ua, apikey, download_dir)

    # 检查m-team种子属性
    @staticmethod
    def check_torrent_attr(torrent_url, ua=None, apikey=None, proxy=False):
        ret_attr = {
            "free": False,
            "2xfree": False,
            "hr": False,
            "peer_count": 0,
            "downloadvolumefactor": 1.0,
            "uploadvolumefactor": 1.0,
        }
        addr = parse.urlparse(torrent_url)
        # /detail/770**
        m = re.match("/detail/([0-9]+)", addr.path)
        if not m:
            log.warn(f"【MTeanApi】 获取馒头种子属性失败 path：{addr.path}")
            return ret_attr
        torrentid = int(m.group(1))
        if not apikey:
            log.warn(f"【MTeanApi】 获取馒头种子属性失败, 未设置站点Api-Key")
            return ret_attr
        site_url = "%s/api/torrent/detail" % StringUtils.get_base_url(torrent_url)
        res = RequestUtils(
            headers={
                'x-api-key': apikey,
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": ua,
                "Accept": "application/json"
            },
            proxies=proxy,
            timeout=30
        ).post_res(url=site_url, data=("id=%d" % torrentid))
        if res and res.status_code == 200:
            msg = res.json().get('message')
            if msg != "SUCCESS":
                log.warn(f"【MTeanApi】 获取馒头种子{torrentid}属性失败：{msg}")
                return ret_attr
            result = res.json().get('data', {})
            status = result.get('status')
            ret_attr["peer_count"] = status.get('seeders')
            """
            NORMAL:上传下载都1倍
            _2X_FREE:上傳乘以二倍，下載不計算流量。
            _2X_PERCENT_50:上傳乘以二倍，下載計算一半流量。
            _2X:上傳乘以二倍，下載計算正常流量。
            PERCENT_50:上傳計算正常流量，下載計算一半流量。
            PERCENT_30:上傳計算正常流量，下載計算該種子流量的30%。
            FREE:上傳計算正常流量，下載不計算流量。
            """
            discount = status.get('discount')
            if discount == "_2X_FREE":
                ret_attr["2xfree"] = True
                ret_attr["free"] = True
                ret_attr["downloadvolumefactor"] = 0
                ret_attr["uploadvolumefactor"] = 2.0
            elif discount == "_2X_PERCENT_50":
                ret_attr["2xfree"] = True
                ret_attr["free"] = True
                ret_attr["downloadvolumefactor"] = 0.5
                ret_attr["uploadvolumefactor"] = 2.0
            elif discount == "_2X":
                ret_attr["2xfree"] = True
                ret_attr["free"] = True
                ret_attr["downloadvolumefactor"] = 1.0
                ret_attr["uploadvolumefactor"] = 2.0
            elif discount == "PERCENT_50":
                ret_attr["downloadvolumefactor"] = 0.5
                ret_attr["uploadvolumefactor"] = 1.0
            elif discount == "PERCENT_30":
                ret_attr["downloadvolumefactor"] = 0.3
                ret_attr["uploadvolumefactor"] = 1.0
            elif discount == "FREE":
                ret_attr["free"] = True
                ret_attr["downloadvolumefactor"] = 0
                ret_attr["uploadvolumefactor"] = 1.0
            # log.info(f"【SiteConf】获取馒头种子{torrentid}属性成功: {ret_attr}")
        elif res is not None:
            log.warn(f"【MTeanApi】 获取馒头种子{torrentid}属性失败，错误码：{res.status_code}")
        else:
            log.warn(f"【MTeanApi】 获取馒头种子{torrentid}属性失败，无法连接 {site_url}")
        return ret_attr