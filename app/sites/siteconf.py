import random
import time
import re
import log
from functools import lru_cache

from lxml import etree

from app.helper import ChromeHelper
from app.utils import ExceptionUtils, StringUtils, RequestUtils
from app.utils.commons import singleton
from config import Config
from web.backend.pro_user import ProUser
from urllib import parse


@singleton
class SiteConf:
    user = None
    # 站点签到支持的识别XPATH
    _SITE_CHECKIN_XPATH = [
        '//a[@id="signed"]',
        '//a[contains(@href, "attendance")]',
        '//a[contains(text(), "签到")]',
        '//a/b[contains(text(), "签 到")]',
        '//span[@id="sign_in"]/a',
        '//a[contains(@href, "addbonus")]',
        '//input[@class="dt_button"][contains(@value, "打卡")]',
        '//a[contains(@href, "sign_in")]',
        '//a[contains(@onclick, "do_signin")]',
        '//a[@id="do-attendance"]',
        '//shark-icon-button[@href="attendance.php"]'
    ]

    # 站点详情页字幕下载链接识别XPATH
    _SITE_SUBTITLE_XPATH = [
        '//td[@class="rowhead"][text()="字幕"]/following-sibling::td//a/@href',
    ]

    # 站点登录界面元素XPATH
    _SITE_LOGIN_XPATH = {
        "username": [
            '//input[@name="username"]',
            '//input[@id="form_item_username"]',
            '//input[@id="username"]'
        ],
        "password": [
            '//input[@name="password"]',
            '//input[@id="form_item_password"]',
            '//input[@id="password"]'
        ],
        "captcha": [
            '//input[@name="imagestring"]',
            '//input[@name="captcha"]',
            '//input[@id="form_item_captcha"]'
        ],
        "captcha_img": [
            '//img[@alt="CAPTCHA"]/@src',
            '//img[@alt="SECURITY CODE"]/@src',
            '//img[@id="LAY-user-get-vercode"]/@src',
            '//img[contains(@src,"/api/getCaptcha")]/@src'
        ],
        "submit": [
            '//input[@type="submit"]',
            '//button[@type="submit"]',
            '//button[@lay-filter="login"]',
            '//button[@lay-filter="formLogin"]',
            '//input[@type="button"][@value="登录"]'
        ],
        "error": [
            "//table[@class='main']//td[@class='text']/text()"
        ],
        "twostep": [
            '//input[@name="two_step_code"]',
            '//input[@name="2fa_secret"]'
        ]
    }

    def __init__(self):
        self.init_config()

    def init_config(self):
        self.user = ProUser()

    def get_checkin_conf(self):
        return self._SITE_CHECKIN_XPATH

    def get_subtitle_conf(self):
        return self._SITE_SUBTITLE_XPATH

    def get_login_conf(self):
        return self._SITE_LOGIN_XPATH

    def get_grap_conf(self, url=None):
        if not url:
            return self.user.get_brush_conf()
        for k, v in self.user.get_brush_conf().items():
            if StringUtils.url_equal(k, url):
                return v
        return {}

    # 检查m-team种子属性
    def check_mt_torrent_attr(self, torrent_url, ua=None, apikey=None, proxy=False):
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
            log.warn(f"【SiteConf】获取馒头种子属性失败 path：{addr.path}")
            return ret_attr
        torrentid = int(m.group(1))
        if not apikey:
            log.warn(f"【SiteConf】获取馒头种子属性失败, 未设置站点Api-Key")
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
                log.warn(f"【SiteConf】获取馒头种子{torrentid}属性失败：{msg}")
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
            log.warn(f"【SiteConf】获取馒头种子{torrentid}属性失败，错误码：{res.status_code}")
        else:
            log.warn(f"【SiteConf】获取馒头种子{torrentid}属性失败，无法连接 {site_url}")
        return ret_attr

    def check_torrent_attr(self, torrent_url, cookie, ua=None, apikey=None, proxy=False):
        """
        检验种子是否免费，当前做种人数
        :param torrent_url: 种子的详情页面
        :param cookie: 站点的Cookie
        :param ua: 站点的ua
        :param apikey: 站点的apikey
        :param proxy: 是否使用代理
        :return: 种子属性，包含FREE 2XFREE HR PEER_COUNT等属性
        """
        ret_attr = {
            "free": False,
            "2xfree": False,
            "hr": False,
            "peer_count": 0,
            "downloadvolumefactor": 1.0,
            "uploadvolumefactor": 1.0,
        }
        if not torrent_url:
            return ret_attr
        domain = StringUtils.get_url_domain(torrent_url)
        if 'm-team' in domain:
            return self.check_mt_torrent_attr(torrent_url, ua, apikey, proxy)
        xpath_strs = self.get_grap_conf(torrent_url)
        if not xpath_strs:
            return ret_attr
        html_text = self.__get_site_page_html(url=torrent_url,
                                              cookie=cookie,
                                              ua=ua,
                                              render=xpath_strs.get('RENDER'),
                                              proxy=proxy)
        if not html_text:
            return ret_attr
        try:
            html = etree.HTML(html_text)
            # 检测2XFREE
            for xpath_str in xpath_strs.get("2XFREE"):
                if html.xpath(xpath_str):
                    ret_attr["free"] = True
                    ret_attr["2xfree"] = True
                    ret_attr["downloadvolumefactor"] = 0
                    ret_attr["uploadvolumefactor"] = 2.0
            # 检测FREE
            for xpath_str in xpath_strs.get("FREE"):
                if html.xpath(xpath_str):
                    ret_attr["free"] = True
                    ret_attr["downloadvolumefactor"] = 0
                    ret_attr["uploadvolumefactor"] = 1.0
            # 检测HR
            for xpath_str in xpath_strs.get("HR"):
                if html.xpath(xpath_str):
                    ret_attr["hr"] = True
            # 检测PEER_COUNT当前做种人数
            for xpath_str in xpath_strs.get("PEER_COUNT"):
                peer_count_dom = html.xpath(xpath_str)
                if peer_count_dom:
                    peer_count_str = ''.join(peer_count_dom[0].itertext())
                    peer_count_digit_str = ""
                    for m in peer_count_str:
                        if m.isdigit():
                            peer_count_digit_str = peer_count_digit_str + m
                        if m == " ":
                            break
                    ret_attr["peer_count"] = int(peer_count_digit_str) if len(peer_count_digit_str) > 0 else 0
        except Exception as err:
            ExceptionUtils.exception_traceback(err)
        # 随机休眼后再返回
        time.sleep(round(random.uniform(1, 5), 1))
        return ret_attr

    @staticmethod
    @lru_cache(maxsize=128)
    def __get_site_page_html(url, cookie, ua, render=False, proxy=False):
        chrome = ChromeHelper(headless=True)
        if render and chrome.get_status():
            # 开渲染
            if chrome.visit(url=url, cookie=cookie, ua=ua, proxy=proxy):
                # 等待页面加载完成
                time.sleep(10)
                return chrome.get_html()
        else:
            res = RequestUtils(
                cookies=cookie,
                headers=ua,
                proxies=Config().get_proxies() if proxy else None
            ).get_res(url=url)
            if res and res.status_code == 200:
                res.encoding = res.apparent_encoding
                return res.text
        return ""
