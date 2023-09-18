import os.path
import regex as re

import log
from app.helper import WordsHelper
from app.media.meta.metaanime import MetaAnime
from app.media.meta.metavideo import MetaVideo
from app.media.meta.metavideov2 import MetaVideoV2
from app.utils.types import MediaType
from app.utils import StringUtils
from config import Config, RMT_MEDIAEXT
from app.helper import FfmpegHelper

def MetaInfo(title,
             subtitle=None,
             mtype=None,
             filePath=None,
             media_type=None,
             cn_name=None,
             en_name=None,
             tmdb_id=None,
             imdb_id=None):
    """
    媒体整理入口，根据名称和副标题，判断是哪种类型的识别，返回对应对象
    :param title: 标题、种子名、文件名
    :param subtitle: 副标题、描述
    :param mtype: 指定识别类型，为空则自动识别类型
    :return: MetaAnime、MetaVideo
    """

    # 使用ffmpeg获取视频元数据状态
    media = Config().get_config('media')
    ffmpeg_video_meta_enable = False
    if media:
        ffmpeg_video_meta_enable = media.get('ffmpeg_video_meta', False) or False
    # 记录原始名称
    org_title = title
    # 应用自定义识别词，获取识别词处理后名称
    rev_title, msg, used_info = WordsHelper().process(title)
    if rev_title and ffmpeg_video_meta_enable and filePath:
        rev_title = __complete_rev_title(rev_title, filePath)
    if subtitle:
        subtitle, _, _ = WordsHelper().process(subtitle)

    if msg:
        for msg_item in msg:
            log.warn("【Meta】%s" % msg_item)

    # 判断是否处理文件
    if org_title and os.path.splitext(org_title)[-1] in RMT_MEDIAEXT:
        fileflag = True
    else:
        fileflag = False

    laboratory = Config().get_config('laboratory')
    recognize_enhance_enable = False
    if laboratory:
        recognize_enhance_enable = laboratory.get('recognize_enhance_enable', False) or False

    if recognize_enhance_enable:
         meta_info = MetaVideoV2(rev_title, subtitle, fileflag, filePath, media_type, cn_name, en_name, tmdb_id, imdb_id)
    else:
        if mtype == MediaType.ANIME or is_anime(rev_title):
            meta_info = MetaAnime(rev_title, subtitle, fileflag, filePath, media_type, cn_name, en_name, tmdb_id, imdb_id)
        else:
            meta_info = MetaVideo(rev_title, subtitle, fileflag, filePath, media_type, cn_name, en_name, tmdb_id, imdb_id)
    # 设置原始名称
    meta_info.org_string = org_title
    # 设置识别词处理后名称
    meta_info.rev_string = rev_title
    # 设置应用的识别词
    meta_info.ignored_words = used_info.get("ignored")
    meta_info.replaced_words = used_info.get("replaced")
    meta_info.offset_words = used_info.get("offset")

    return meta_info


def is_anime(name):
    """
    判断是否为动漫
    :param name: 名称
    :return: 是否动漫
    """
    if not name:
        return False
    if re.search(r'【[+0-9XVPI-]+】\s*【', name, re.IGNORECASE):
        return True
    if re.search(r'\s+-\s+[\dv]{1,4}\s+', name, re.IGNORECASE):
        return True
    if re.search(r"S\d{2}\s*-\s*S\d{2}|S\d{2}|\s+S\d{1,2}|EP?\d{2,4}\s*-\s*EP?\d{2,4}|EP?\d{2,4}|\s+EP?\d{1,4}", name,
                 re.IGNORECASE):
        return False
    if re.search(r'\[[+0-9XVPI-]+]\s*\[', name, re.IGNORECASE):
        return True
    return False

def __complete_rev_title(title, filePath):
    """
    根据输入的路径和文件名称完善视频的分辨率、视频编码、音频编码等信息
    """
    if not os.path.exists(filePath):
        log.info(f"【Meta】输入的视频路径不存在")
        return title

    # 获取文件元数据
    video_meta = FfmpegHelper().get_video_metadata(filePath)
    if not video_meta:
        log.info("【Meta】未能获取到视频元信息")
        return title

    # 视频分辨率(144p/288p/360p/480p/720p/1080p/2K/4K)
    resolution = __get_resolution(video_meta)
    # 色彩空间(SDR/HDR)
    color_space = __get_color_space(video_meta)
    # 杜比视界
    dolby_vision = __get_dolby_vision(video_meta)
    # 视频编码
    video_codec = __get_video_codec(video_meta)
    # 音频编码
    audio_codec = __get_audio_codec(video_meta)

    video_meta_title_list = []
    if StringUtils.is_string_and_not_empty(resolution):
        video_meta_title_list.append(resolution)
    if StringUtils.is_string_and_not_empty(color_space):
        video_meta_title_list.append(color_space)
    if StringUtils.is_string_and_not_empty(dolby_vision):
        video_meta_title_list.append(dolby_vision)
    if StringUtils.is_string_and_not_empty(video_codec):
        video_meta_title_list.append(video_codec)
    if StringUtils.is_string_and_not_empty(audio_codec):
        video_meta_title_list.append(audio_codec)

    video_meta_title = ".".join(video_meta_title_list)
    completed_video_meta_title = title
    title_without_extension, title_extension = os.path.splitext(title)
    title_extension_without_dot = title_extension[1:]
    if StringUtils.is_string_and_not_empty(video_meta_title):
        completed_video_meta_title = title_without_extension + "." + video_meta_title + "." + title_extension_without_dot
    return completed_video_meta_title

def __get_resolution(video_meta):
    """
    根据ffprobe获取到的视频信息，生成分辨率信息，480p/720p/1080p/4K
    """
    for stream in video_meta.get("streams", []):
        if stream.get("codec_type") == "video":
            height = stream.get("height")
            if isinstance(height, int):
                return __calculate_resolution(height)
    return None

def __calculate_resolution(height):
    """
    根据视频分辨率的高信息，输出144p/288p/360p/480p/576p/720p/960p/1080p/2K/4K
    """
    if height <= 144:
        return "144p"
    elif 144 < height <= 288:
        return "288p"
    elif 288 < height <= 360:
        return "360p"
    elif 360 < height <= 480:
        return "480p"
    elif 480 < height <= 576:
        return "576p"
    elif 576 < height <= 720:
        return "720p"
    elif 960 <= height < 1080:
        return "960p"
    elif 1080 <= height < 1440:
        return "1080p"
    elif 1400 <= height < 2160:
        return "2K"
    elif 2160 <= height < 4320:
        return "4K"
    elif height >= 4320:
        return "4K+"
    else:
        return None

def __get_color_space(video_meta):
    """
    根据ffprobe获取到的视频信息，获取色彩空间(SDR/HDR)
    """
    for stream in video_meta.get("streams", []):
        if stream.get("codec_type") == "video":
            color_space = stream.get("color_space")
            if StringUtils.is_string_and_not_empty(color_space):
                color_space_lower = color_space.lower().replace(".", "")
                if "bt709" in color_space_lower or "rec709" in color_space_lower:
                    return "SDR"
                elif "bt2020" in color_space_lower or "rec2020" in color_space_lower:
                    return "HDR"
    return None

def __get_dolby_vision(video_meta):
    """
    根据ffprobe获取到的视频信息，判断是否是杜比视界, 输出DV
    """
    for stream in video_meta.get("streams", []):
        if stream.get("codec_type") == "video":
            tags = stream.get("tags")
            if tags and any("dolby" in tag.lower() for tag in tags.values()):
                return "DV"
    return None

def __get_video_codec(video_meta):
    """
    根据ffprobe获取到的视频信息，生成视频编码信息，HEVC/H264/H265
    """
    for stream in video_meta.get("streams", []):
        if stream.get("codec_type") == "video":
            codec_name = stream.get("codec_name")
            if StringUtils.is_string_and_not_empty(codec_name):
                return codec_name.upper()
    return None

def __get_audio_codec(video_meta):
    """
    根据ffprobe获取到的视频信息，生成音频编码信息，AAC/FLAC/APE
    """
    for stream in video_meta.get("streams", []):
        if stream.get("codec_type") == "audio":
            codec_name = stream.get("codec_name")
            if StringUtils.is_string_and_not_empty(codec_name):
                return codec_name.upper()
    return None