import requests
import json
from base64 import b64encode
from urllib.parse import urlencode

import log
from config import Config
from app.utils import RequestUtils, StringUtils

class OcrHelper:

    _ocr_b64_url = "https://ocr.ddsrem.com/captcha/base64"
    _baiduocr_api_key = None
    _baiduocr_secret_key = None

    def __init__(self):
        ocr = Config().get_config('ocr')
        if ocr:
            self._baiduocr_api_key = ocr.get('baiduocr_api_key', '') or ''
            self._baiduocr_secret_key = ocr.get('baiduocr_secret_key', '') or ''
            custom_oc_url = ocr.get('custom_ocr_url', '') or ''
            if StringUtils.is_string_and_not_empty(custom_oc_url):
                self._ocr_b64_url = custom_oc_url.rstrip('/')

    def get_captcha_text(self, image_url=None, image_b64=None, cookie=None, ua=None):
        """
        根据图片地址，获取验证码图片，并识别内容
        :param image_url: 图片地址
        :param image_b64: 图片base64，跳过图片地址下载
        :param cookie: 下载图片使用的cookie
        :param ua: 下载图片使用的ua
        """
        if image_url:
            ret = RequestUtils(headers=ua,
                               cookies=cookie).get_res(image_url)
            if ret is not None:
                image_bin = ret.content
                if not image_bin:
                    return ""
                image_b64 = b64encode(image_bin).decode()
        if not image_b64:
            return ""

        captcha = ""
        if self.baiduocr_avaliable():
            captcha = self.get_captcha_text_by_baiduocr(image_b64=image_b64)
        if StringUtils.is_string_and_not_empty(captcha):
            return captcha

        if not self.custom_server_avaliable():
            return ""

        ret = RequestUtils(content_type="application/json").post_res(
            url=self._ocr_b64_url,
            json={"base64_img": image_b64})
        if ret:
            return ret.json().get("result")
        return ""

    def get_captcha_text_by_baiduocr(self, image_b64=None):
        if not self.baiduocr_avaliable() or not image_b64:
            return ""

        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=" + self.get_baiduocr_access_token()
        payload = {'image': f'{image_b64}'}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if not response:
            return ""
        if response.status_code != 200:
            return ""
        try:
            result = response.json()
            if 'words_result' in result:
                words_result = result.get('words_result', []) or []
                if len(words_result) > 0:
                    captcha_text_list = [result['words'] for result in words_result]
                    return " ".join(captcha_text_list)
                else:
                    return ""
            else:
                log.error(f"【OCR】验证码识别失败, 原始返回: {response.json()}")
                return ""
        except Exception as e:
            log.error(f"【OCR】验证码识别失败: {str(e)}")
            return ""

    def get_baiduocr_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self._baiduocr_api_key, "client_secret": self._baiduocr_secret_key}
        return str(requests.post(url, params=params).json().get("access_token"))

    def baiduocr_avaliable(self):
        """
        判断百度OCR是否可用
        """
        return StringUtils.is_string_and_not_empty(self._baiduocr_api_key) and StringUtils.is_string_and_not_empty(self._baiduocr_secret_key)

    def custom_server_avaliable(self):
        """
        判断自建服务端OCR是否可用
        """
        return StringUtils.is_string_and_not_empty(self._ocr_b64_url)
