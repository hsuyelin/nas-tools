import os
import shutil
import re
from lxml import etree

import log
from app.sites.sites import Sites
from app.sites.siteconf import SiteConf
from app.helper import SiteHelper
from app.utils import RequestUtils, StringUtils, PathUtils, ExceptionUtils
from config import Config, RMT_SUBEXT
from urllib import parse

class SiteSubtitle:

    siteconf = None
    sites = None
    _save_tmp_path = None

    def __init__(self):
        self.siteconf = SiteConf()
        self.sites = Sites()
        self._save_tmp_path = Config().get_temp_path()
        if not os.path.exists(self._save_tmp_path):
            os.makedirs(self._save_tmp_path, exist_ok=True)

    # 拉取馒头字幕列表
    def _mt_get_subtitle_list(self, base_url, torrentid, ua, apikey):
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
                log.warn(f"【Sites】获取馒头{torrentid}字幕列表失败：{msg}")
                return subtitle_list
            results = res.json().get('data', [])
            for result in results:
                subtitle = {
                    "id": result.get("id"),
                    "filename": result.get("filename"),
                }
                subtitle_list.append(subtitle)
            log.info(f"【Sites】获取馒头{torrentid}字幕列表成功，捕获：{len(subtitle_list)}条字幕信息")
        elif res is not None:
            log.warn(f"【Sites】获取馒头{torrentid}字幕列表失败，错误码：{res.status_code}")
        else:
            log.warn(f"【Sites】获取馒头{torrentid}字幕列表失败，无法连接 {site_url}")
        return subtitle_list

    # 下载单个馒头字幕
    def _mt_download_single_subtitle(self, base_url, torrentid, subtitle_info, ua, apikey, download_dir):
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
                log.warn(f"【Sites】馒头{torrentid} 字幕文件非法：{subtitle_id}")
                return
            if file_name.lower().endswith(".zip"):
                # ZIP包
                zip_file = os.path.join(self._save_tmp_path, file_name)
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
                    log.info(f"【Sites】馒头{torrentid} 转移字幕 {sub_file} 到 {target_sub_file}")
                    SiteHelper.transfer_subtitle(sub_file, target_sub_file)
                # 删除临时文件
                try:
                    shutil.rmtree(zip_path)
                    os.remove(zip_file)
                except Exception as err:
                    ExceptionUtils.exception_traceback(err)
            else:
                sub_file = os.path.join(self._save_tmp_path, file_name)
                # 保存
                with open(sub_file, 'wb') as f:
                    f.write(res.content)
                target_sub_file = os.path.join(download_dir,
                                               os.path.splitext(os.path.basename(sub_file))[0])
                log.info(f"【Sites】馒头{torrentid} 转移字幕 {sub_file} 到 {target_sub_file}")
                SiteHelper.transfer_subtitle(sub_file, target_sub_file)
        elif res is not None:
            log.warn(f"【Sites】下载馒头{torrentid}字幕 {filename} 失败，错误码：{res.status_code}")
        else:
            log.warn(f"【Sites】下载馒头{torrentid}字幕 {filename} 失败，无法连接 {site_url}")

    # 下载馒头字幕
    def mt_download(self, media_info, site_id, cookie, ua, apikey, download_dir):
        addr = parse.urlparse(media_info.page_url)
        # log.info(f"【Sites】下载馒头字幕 {media_info.page_url}")
        # /detail/770**
        m = re.match("/detail/([0-9]+)", addr.path)
        if not m:
            log.warn(f"【Sites】获取馒头字幕失败 path：{addr.path}")
            return
        torrentid = int(m.group(1))
        if not apikey:
            log.warn(f"【Sites】获取馒头字幕失败, 未设置站点Api-Key")
            return
        base_url = StringUtils.get_base_url(media_info.page_url)
        subtitle_list = self._mt_get_subtitle_list(base_url, torrentid, ua, apikey)
        # 下载所有字幕文件
        for subtitle_info in subtitle_list:
            self._mt_download_single_subtitle(base_url, torrentid, subtitle_info, ua, apikey, download_dir)

    def download(self, media_info, site_id, cookie, ua, apikey, download_dir):
        """
        从站点下载字幕文件，并保存到本地
        """

        if not media_info.page_url:
            return
        # 字幕下载目录
        log.info("【Sites】开始从站点下载字幕：%s" % media_info.page_url)
        if not download_dir:
            log.warn("【Sites】未找到字幕下载目录")
            return
        # 站点流控
        if self.sites.check_ratelimit(site_id):
            log.warn(f"【Sites】{site_id}触发了站点流控，停止下载字幕")
            return
        # 馒头特殊处理
        domain = StringUtils.get_url_domain(media_info.page_url)
        if 'm-team' in domain:
            return self.mt_download(media_info, site_id, cookie, ua, apikey, download_dir)

        # 读取网站代码
        request = RequestUtils(cookies=cookie, headers=ua)
        res = request.get_res(media_info.page_url)
        if res and res.status_code == 200:
            if not res.text:
                log.warn(f"【Sites】读取页面代码失败：{media_info.page_url}")
                return
            html = etree.HTML(res.text)
            sublink_list = []
            for xpath in self.siteconf.get_subtitle_conf():
                sublinks = html.xpath(xpath)
                if sublinks:
                    for sublink in sublinks:
                        if not sublink:
                            continue
                        if not sublink.startswith("http"):
                            base_url = StringUtils.get_base_url(media_info.page_url)
                            if sublink.startswith("/"):
                                sublink = "%s%s" % (base_url, sublink)
                            else:
                                sublink = "%s/%s" % (base_url, sublink)
                        sublink_list.append(sublink)
            # 下载所有字幕文件
            for sublink in sublink_list:
                log.info(f"【Sites】找到字幕下载链接：{sublink}，开始下载...")
                # 下载
                ret = request.get_res(sublink)
                if ret and ret.status_code == 200:
                    # 创建目录
                    if not os.path.exists(download_dir):
                        os.makedirs(download_dir, exist_ok=True)
                    # 保存ZIP
                    file_name = SiteHelper.get_url_subtitle_name(ret.headers.get('content-disposition'), sublink)
                    if not file_name:
                        log.warn(f"【Sites】链接不是字幕文件：{sublink}")
                        continue
                    if file_name.lower().endswith(".zip"):
                        # ZIP包
                        zip_file = os.path.join(self._save_tmp_path, file_name)
                        # 解压路径
                        zip_path = os.path.splitext(zip_file)[0]
                        with open(zip_file, 'wb') as f:
                            f.write(ret.content)
                        # 解压文件
                        shutil.unpack_archive(zip_file, zip_path, format='zip')
                        # 遍历转移文件
                        for sub_file in PathUtils.get_dir_files(in_path=zip_path, exts=RMT_SUBEXT):
                            target_sub_file = os.path.join(download_dir,
                                                           os.path.splitext(os.path.basename(sub_file))[0])
                            log.info(f"【Sites】转移字幕 {sub_file} 到 {target_sub_file}")
                            SiteHelper.transfer_subtitle(sub_file, target_sub_file)
                        # 删除临时文件
                        try:
                            shutil.rmtree(zip_path)
                            os.remove(zip_file)
                        except Exception as err:
                            ExceptionUtils.exception_traceback(err)
                    else:
                        sub_file = os.path.join(self._save_tmp_path, file_name)
                        # 保存
                        with open(sub_file, 'wb') as f:
                            f.write(ret.content)
                        target_sub_file = os.path.join(download_dir,
                                                       os.path.splitext(os.path.basename(sub_file))[0])
                        log.info(f"【Sites】转移字幕 {sub_file} 到 {target_sub_file}")
                        SiteHelper.transfer_subtitle(sub_file, target_sub_file)
                else:
                    log.error(f"【Sites】下载字幕文件失败：{sublink}")
                    continue
            if sublink_list:
                log.info(f"【Sites】{media_info.page_url} 页面字幕下载完成")
            else:
                log.warn(f"【Sites】{media_info.page_url} 页面未找到字幕下载链接")
        elif res is not None:
            log.warn(f"【Sites】连接 {media_info.page_url} 失败，状态码：{res.status_code}")
        else:
            log.warn(f"【Sites】无法打开链接：{media_info.page_url}")
