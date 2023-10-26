import re
import os

from guessit.api import default_api
import cn2an

import log
from config import RMT_MEDIAEXT
from app.media.meta._base import MetaBase
from app.media.meta.release_groups import ReleaseGroupsMatcher
from app.media.meta.customization import CustomizationMatcher
from .mediaItem import MediaItem
from app.utils import StringUtils
from app.utils.types import MediaType
from app.utils.tokens import Tokens
        
class MetaVideoV2(MetaBase):

    _media_item_title = None
    _media_item_subtitle = None
    _original_title = None
    _original_subtitle = None

    _name_no_begin_re = r"^\[.+?]"
    _name_nostring_re = r"^PTS|^JADE|^ViuTV|^AOD|^CHC|^[A-Z]{1,4}TV[\-0-9UVHDK]*" \
                    r"|HBO$|\s+HBO|\d{1,2}th|\d{1,2}bit|NETFLIX|AMAZON|IMAX|^3D|\s+3D|^BBC\s+|\s+BBC|BBC$|DISNEY\+?|XXX|\s+DC$" \
                    r"|[第\s共]+[0-9一二三四五六七八九十\-\s]+季" \
                    r"|[第\s共]+[0-9一二三四五六七八九十百零\-\s]+[集话話]" \
                    r"|连载|日剧|美剧|电视剧|动画片|动漫|欧美|西德|日韩|超高清|高清|蓝光|翡翠台|梦幻天堂·龙网|★?\d*月?新番" \
                    r"|最终季|合集|[多中国英葡法俄日韩德意西印s泰台港粤双文语简繁体特效内封官译外挂]+字幕|版本|出品|台版|港版|\w+字幕组" \
                    r"|未删减版|UNCUT$|UNRATE$|WITH EXTRAS$|RERIP$|SUBBED$|PROPER$|REPACK$|SEASON$|EPISODE$|Complete$|Extended$|Extended Version$" \
                    r"|S\d{2}\s*-\s*S\d{2}|S\d{2}|\s+S\d{1,2}|EP?\d{2,4}\s*-\s*EP?\d{2,4}|EP?\d{2,4}|\s+EP?\d{1,4}" \
                    r"|CD[\s.]*[1-9]|DVD[\s.]*[1-9]|DISK[\s.]*[1-9]|DISC[\s.]*[1-9]" \
                    r"|[248]K|\d{3,4}[PIX]+" \
                    r"|CD[\s.]*[1-9]|DVD[\s.]*[1-9]|DISK[\s.]*[1-9]|DISC[\s.]*[1-9]"
    _release_group_re = r"\[.*(?:字幕组|字幕社|发布组|手抄部|手抄组|压制|动漫|新番|合集|连载|日剧|美剧|电视剧|动画片|动漫|欧美|西德|日韩|超高清|高清|蓝光|翡翠台|梦幻天堂·龙网|喵萌奶茶屋|Sub|LoliHouse|毀片黨|毁片党|论坛|Raws)\]"
    _seasons_re = r"(?:第)?\s*(?:\d+|[一二三四五六七八九十]+)\s*(季)?\s*\.\s*(?:第)?\s*(?:\d+|[一二三四五六七八九十]+)\s*(季)"
    _seasons_re_2 = r"(?:[Ss]0*|Season|season)([0-9]+)\s*\.\s*(?:[Ss]0*|Season|season)([0-9]+)"
    _season_re = r"(?:第)?\s*(?:\d+|[一二三四五六七八九十]+)\s*(季)"
    _season_re_2 = r"(?<![a-zA-Z0-9_])(?i)[sS](eason)?\s*0*\d+"
    _season_all_re = r"(?<![^\s.\\-])\s*(?<!第)(?:\d+|[一二三四五六七八九十]+)\s*(季)\s*(全)(?![^\s.\\-]*[\d一二三四五六七八九十])"
    _season_all_re_2 = r"(全|共)\s*(?:\d+|[一二三四五六七八九十]+)\s*(季)"
    _episodes_re = r"(?:第)?\s*(?<![sS])(?:\d+|[一二三四五六七八九十]+)\s*(?:集|话|話)?\s*\.\s*(?:第)?\s*(?:\d+|[一二三四五六七八九十]+)\s*(?:集|话|話)"
    _episodes_re_2 = r"(?:[Ee]0*|episode|ep)([0-9]+)\s*\.\s*(?:[Ee]0*|episode|ep)([0-9]+)"
    _episode_re = r"(?:第)?\s*(?:\d+|[一二三四五六七八九十]+)\s*(?:集|话|話)"
    _episode_re_2 = r"(?<![a-zA-Z0-9_])(?i)(?:e|ep|episode)\s*0*\d+"
    _episode_all_re = r"(?<![^\s.\\-])\s*(?<!第)(?:\d+|[一二三四五六七八九十]+)\s*(寄|集|话|話)\s*(全)(?![^\s.\\-]*[\d一二三四五六七八九十])"
    _episode_all_re_2 = r"(全|共)\s*(?:\d+|[一二三四五六七八九十]+)\s*(寄|集|话|話)"
    _numbers_re = r"\d+|[一二三四五六七八九十]+"
    _years_re = r"(\d{4}(?!p|P))\s*\.\s*(\d{4})(?![pP])"
    _release_date_re = r"\d{2,4}年\d+(?:月)?(?:新番|合集|)"
    _other_re = r"\[(?:★|❤|GB|JP|KR|CN|TW|US|SG|招募翻译(?:校对)?|招募翻譯(?:校對)?|)\]"
    _special_resource_team = r"(?i)(HDCTV)"
    _special_streaming_service = r"(?i)(Jade|ViuTv)"

    def __init__(self,
                 title,
                 subtitle=None,
                 fileflag=False,
                 filePath=None,
                 media_type=None,
                 cn_name=None,
                 en_name=None,
                 tmdb_id=None,
                 imdb_id=None):
        super().__init__(title,
                         subtitle,
                         fileflag,
                         filePath,
                         media_type,
                         cn_name,
                         en_name,
                         tmdb_id,
                         imdb_id)

        self._original_title = title
        self._original_subtitle = subtitle

        # 判断是否纯数字命名
        if os.path.splitext(title)[-1] in RMT_MEDIAEXT \
                and os.path.splitext(title)[0].isdigit() \
                and len(os.path.splitext(title)[0]) < 5:
            self.begin_episode = int(os.path.splitext(title)[0])
            self.type = MediaType.TV
            return

        _fixed_title = self.__fix_title(title)
        _fixed_subtitle = self.__fix_release_group(subtitle)
        media_item_title, media_item_subtitle = self.guess_media_item(_fixed_title, _fixed_subtitle)
        self._media_item_title = media_item_title
        self._media_item_subtitle = media_item_subtitle

        if not self._media_item_title and not self._media_item_subtitle:
            return

        # 视频类型：电影/剧集
        self.__init_type()
        # 年份
        self.__init_year()
        # 名称
        self.__init_name()
        # 季
        self.__init_season()
        # 集
        self.__init_episode()
        # part
        self.__init_part()
        # edition
        self.__init_edition()
        # 来源
        self.__init_resource_type()
        # 音频编码
        self.__init_audio_encode()
        # 视频编码
        self.__init_video_encode()
        # 分辨率
        self.__init_resource_pix()
        # 视频效果
        self.__init_resource_effect()

        # 提取原盘DIY
        if self.resource_type and "BluRay" in self.resource_type:
            if (self.subtitle and re.findall(r'D[Ii]Y', self.subtitle)) \
                    or re.findall(r'-D[Ii]Y@', self._original_title):
                self.resource_type = f"{self.resource_type} DIY"

        # 修正季/集/媒体类型
        self.__fix_season()
        self.__fix_episode()
        self.__fix_media_type()

        # 去掉名字中不需要的干扰字符，过短的纯数字不要
        self.cn_name = self.__fix_name(self.cn_name)
        self.en_name = StringUtils.str_title(self.__fix_name(self.en_name))
        
        # 处理part
        if StringUtils.is_string_and_not_empty(self.part) and self.part.upper() == "PART":
            self.part = None

        # 制作组/字幕组
        self.resource_team = ReleaseGroupsMatcher().match(title=self._original_title) or None
        self.__fix_resource_team()
        # 自定义占位符
        self.customization = CustomizationMatcher().match(title=self._original_title) or None

    def __init_type(self):
        media_type = self._media_item_title.main.media_type if self._media_item_title.main.media_type else self._media_item_subtitle.main.media_type
        if StringUtils.is_string_and_not_empty(media_type):
            self.type = MediaType.MOVIE if media_type.lower() == "movie" else MediaType.TV
            self.media_type = MediaType.MOVIE if media_type.lower() == "movie" else MediaType.TV  
        else:
            self.type = MediaType.MOVIE
            self.media_type = MediaType.MOVIE

    def __init_name(self):
        if StringUtils.is_string_and_not_empty(self.cn_name) and StringUtils.is_string_and_not_empty(self.en_name):
            return
        name = self._media_item_title.main.title if StringUtils.is_string_and_not_empty(self._media_item_title.main.title) else self._media_item_subtitle.main.title
        if not StringUtils.is_string_and_not_empty(name):
            return
        if StringUtils.is_eng_media_name_format(name):
            self.en_name = name
            return
        if StringUtils.is_all_chinese(name):
            self.cn_name = name
            return
        tokens = Tokens(name)
        token = tokens.get_next()
        chinese_name = ""
        eng_name = ""
        while token:
            if StringUtils.is_chinese(token):
                chinese_name += f"{token} "
            else:
                eng_name += f"{token} "
            token = tokens.get_next()
        chinese_name = chinese_name.strip()
        eng_name = eng_name.strip()
        self.cn_name = chinese_name if StringUtils.is_string_and_not_empty(chinese_name) else self.cn_name
        self.en_name = eng_name if StringUtils.is_string_and_not_empty(eng_name) else self.en_name

    def __init_year(self):
        year = self._media_item_title.main.year if self._media_item_title.main.year else self._media_item_subtitle.main.year
        if StringUtils.is_string_and_not_empty(year) or self.__is_digit(year):
            self.year = year

    def __init_season(self):
        media_type = self._media_item_title.main.media_type if self._media_item_title.main.media_type else self._media_item_subtitle.main.media_type
        if media_type.lower() != "episode":
            return
        title_seasons = self._media_item_title.episode.season
        title_seasons_count = self._media_item_title.episode.season_count
        subltitle_seasons = self._media_item_subtitle.episode.season
        subltitle_seasons_count = self._media_item_subtitle.episode.season_count

        if self.__is_digit_array(title_seasons) and not self.__is_digit_array(subltitle_seasons):
            title_seasons = sorted(title_seasons)
            self.begin_season = title_seasons[0]
            self.end_season = title_seasons[-1]
            self.total_seasons = len(title_seasons) if not title_seasons_count else title_seasons_count
        elif not self.__is_digit_array(title_seasons) and self.__is_digit_array(subltitle_seasons):
            subltitle_seasons = sorted(subltitle_seasons)
            self.begin_season = subltitle_seasons[0]
            self.end_season = subltitle_seasons[-1]
            self.total_seasons = len(subltitle_seasons) if not subltitle_seasons_count else subltitle_seasons_count
        else:
            if StringUtils.is_string_and_not_empty(title_seasons) or self.__is_digit(title_seasons):
                self.begin_season = title_seasons
                self.end_season = None
                self.total_seasons = 1
            elif StringUtils.is_string_and_not_empty(subltitle_seasons) or self.__is_digit(subltitle_seasons):
                self.begin_season = subltitle_seasons
                self.end_season = None
                self.total_seasons = 1
            else:
                self.begin_season = None
                self.end_season = None
                self.total_seasons = 0

    def __init_episode(self):
        media_type = self._media_item_title.main.media_type if self._media_item_title.main.media_type else self._media_item_subtitle.main.media_type
        if media_type.lower() != "episode":
            return
        title_episodes = self._media_item_title.episode.episode
        title_episodes_count = self._media_item_title.episode.episode_count
        subltitle_episodes = self._media_item_subtitle.episode.episode
        subltitle_episodes_count = self._media_item_subtitle.episode.episode_count

        if self.__is_digit_array(title_episodes) and not self.__is_digit_array(subltitle_episodes):
            title_episodes = sorted(title_episodes)
            self.begin_episode = title_episodes[0]
            self.end_episode = title_episodes[-1]
            self.total_episodes = len(title_episodes) if not title_episodes_count else title_episodes_count
        elif not self.__is_digit_array(title_episodes) and self.__is_digit_array(subltitle_episodes):
            subltitle_episodes = sorted(subltitle_episodes)
            self.begin_episode = subltitle_episodes[0]
            self.end_episode = subltitle_episodes[-1]
            self.total_episodes = len(subltitle_episodes) if not subltitle_episodes_count else subltitle_episodes_count
        else:
            if StringUtils.is_string_and_not_empty(title_episodes) or self.__is_digit(title_episodes):
                self.begin_episode = title_episodes
                self.end_episode = None
                self.total_episodes = 1
            elif StringUtils.is_string_and_not_empty(subltitle_episodes) or self.__is_digit(subltitle_episodes):
                self.begin_episode = subltitle_episodes
                self.end_episode = None
                self.total_episodes = 1
            else:
                self.begin_episode = None
                self.end_episode = None
                self.total_episodes = 0

    def __init_part(self):
        title_parts = self._media_item_title.episode.part
        subltitle_parts = self._media_item_subtitle.episode.part

        if isinstance(title_parts, list) and len(title_parts) > 0:
            self.part = " ".join(title_parts)
        elif isinstance(subltitle_parts, list) and len(subltitle_parts) > 0:
            self.part = " ".join(subltitle_parts)
        else:
            if StringUtils.is_string_and_not_empty(title_parts) or self.__is_digit(title_parts):
                self.part = title_parts
            elif StringUtils.is_string_and_not_empty(subltitle_parts) or self.__is_digit(subltitle_parts):
                self.part = subltitle_parts
            else:
                self.part = None

    def __init_resource_type(self):
        title_resource_types = self._media_item_title.video.source
        subltitle_resource_types = self._media_item_subtitle.video.source

        if isinstance(title_resource_types, list) and len(title_resource_types) > 0:
            self.resource_type = " ".join(title_resource_types)
        elif isinstance(subltitle_resource_types, list) and len(subltitle_resource_types) > 0:
            self.resource_type = " ".join(subltitle_resource_types)
        else:
            if StringUtils.is_string_and_not_empty(title_resource_types):
                self.resource_type = title_resource_types
            elif StringUtils.is_string_and_not_empty(subltitle_resource_types):
                self.resource_type = subltitle_resource_types
            else:
                self.resource_type = None

        if StringUtils.is_string_and_not_empty(self.resource_type):
            self.resource_type = "WEB-DL" if self.resource_type.lower() == "web" else self.resource_type

        title_streaming_services = self._media_item_title.main.streaming_service
        subltitle_streaming_services = self._media_item_subtitle.main.streaming_service
        streaming_services = ""
        if isinstance(title_streaming_services, list) and len(title_streaming_services) > 0:
            streaming_services = " ".join(title_streaming_services)
        elif isinstance(subltitle_streaming_services, list) and len(subltitle_streaming_services) > 0:
            streaming_services = " ".join(subltitle_streaming_services)
        else:
            if StringUtils.is_string_and_not_empty(title_streaming_services):
                streaming_services = title_streaming_services
            elif StringUtils.is_string_and_not_empty(subltitle_streaming_services):
                streaming_services = subltitle_streaming_services

        if not StringUtils.is_string_and_not_empty(streaming_services):
            return

        if StringUtils.is_string_and_not_empty(self.resource_type):
            self.resource_type += f" {streaming_services}"
        else:
            self.resource_type = streaming_services

        self.resource_type = re.sub(r'\+', '', self.resource_type)
        self.resource_type = re.sub(r'(?i)amazon prime', 'AMZN', self.resource_type)
        self.resource_type = re.sub(r'(?i)disney', 'DSNP', self.resource_type)
        self.resource_type = re.sub(r'(?i)hbo max', 'HMAX', self.resource_type)

        if re.findall(r'%s' % self._special_resource_team, self._original_title):
            self.resource_type = re.sub(r'(?i)ctv', '', self.resource_type)

        special_streaming_services_matches = re.findall(r'%s' % self._special_streaming_service, self._original_title)
        if len(special_streaming_services_matches) > 1:
            special_streaming_services_text = ' '.join(special_streaming_services_matches)
        else:
            special_streaming_services_text = special_streaming_services_matches[0] if special_streaming_services_matches else ""
        if special_streaming_services_text:
            self.resource_type += f" {special_streaming_services_text}"
            self.resource_type = self.resource_type.rstrip()

    def __init_resource_effect(self):
        title_resource_effects = self._media_item_title.other.other
        subltitle_resource_effects = self._media_item_subtitle.other.other

        if isinstance(title_resource_effects, list) and len(title_resource_effects) > 0:
            self.resource_effect = " ".join(title_resource_effects)
        elif isinstance(subltitle_resource_effects, list) and len(subltitle_resource_effects) > 0:
            self.resource_effect = " ".join(subltitle_resource_effects)
        else:
            if StringUtils.is_string_and_not_empty(title_resource_effects):
                self.resource_effect = title_resource_effects
            elif StringUtils.is_string_and_not_empty(subltitle_resource_effects):
                self.resource_effect = subltitle_resource_effects
            else:
                self.resource_effect = None

    def __init_resource_pix(self):
        title_resource_pixs = self._media_item_title.video.screen_size
        subltitle_resource_pixs = self._media_item_subtitle.video.screen_size

        if isinstance(title_resource_pixs, list) and len(title_resource_pixs) > 0:
            self.resource_pix = "&".join(title_resource_pixs)
        elif isinstance(subltitle_resource_pixs, list) and len(subltitle_resource_pixs) > 0:
            self.resource_pix = "&".join(subltitle_resource_pixs)
        else:
            if StringUtils.is_string_and_not_empty(title_resource_pixs):
                self.resource_pix = title_resource_pixs
            elif StringUtils.is_string_and_not_empty(subltitle_resource_pixs):
                self.resource_pix = subltitle_resource_pixs
            else:
                self.resource_pix = None

    def __init_edition(self):
        title_editions = self._media_item_title.other.edition
        subltitle_editions = self._media_item_subtitle.other.edition

        if isinstance(title_editions, list) and len(title_editions) > 0:
            self.edition = " ".join(title_editions)
        elif isinstance(subltitle_editions, list) and len(subltitle_editions) > 0:
            self.edition = " ".join(subltitle_editions)
        else:
            if StringUtils.is_string_and_not_empty(title_editions):
                self.edition = title_editions
            elif StringUtils.is_string_and_not_empty(subltitle_editions):
                self.edition = subltitle_editions
            else:
                self.edition = None

    def __init_video_encode(self):
        title_video_encodes = self._media_item_title.video.video_codec
        subltitle_video_encodes = self._media_item_subtitle.video.video_codec

        if isinstance(title_video_encodes, list) and len(title_video_encodes) > 0:
            self.video_encode = "&".join(title_video_encodes)
        elif isinstance(subltitle_video_encodes, list) and len(subltitle_video_encodes) > 0:
            self.video_encode = "&".join(subltitle_video_encodes)
        else:
            if StringUtils.is_string_and_not_empty(title_video_encodes):
                self.video_encode = title_video_encodes
            elif StringUtils.is_string_and_not_empty(subltitle_video_encodes):
                self.video_encode = subltitle_video_encodes
            else:
                self.video_encode = None 

        title_video_color_depths = self._media_item_title.video.color_depth
        subltitle_video_color_depths = self._media_item_subtitle.video.color_depth

        color_depth = ""
        if isinstance(title_video_color_depths, list) and len(title_video_color_depths) > 0:
            color_depth = " ".join(title_video_color_depths)
        elif isinstance(subltitle_video_color_depths, list) and len(subltitle_video_color_depths) > 0:
            color_depth = " ".join(subltitle_video_color_depths)
        else:
            if StringUtils.is_string_and_not_empty(title_video_color_depths):
                color_depth = title_video_color_depths
            elif StringUtils.is_string_and_not_empty(subltitle_video_color_depths):
                color_depth = subltitle_video_color_depths

        if not StringUtils.is_string_and_not_empty(color_depth):
            return

        if StringUtils.is_string_and_not_empty(self.video_encode):
            self.video_encode += f" {color_depth}"
        else:
            self.video_encode = color_depth

    def __init_audio_encode(self):
        title_audio_encodes = self._media_item_title.audio.audio_codec
        subltitle_audio_encodes = self._media_item_subtitle.audio.audio_codec

        if isinstance(title_audio_encodes, list) and len(title_audio_encodes) > 0:
            self.audio_encode = " ".join(title_audio_encodes)
        elif isinstance(subltitle_audio_encodes, list) and len(subltitle_audio_encodes) > 0:
            self.audio_encode = " ".join(subltitle_audio_encodes)
        else:
            if StringUtils.is_string_and_not_empty(title_audio_encodes):
                self.audio_encode = title_audio_encodes
            elif StringUtils.is_string_and_not_empty(subltitle_audio_encodes):
                self.audio_encode = subltitle_audio_encodes

        # 替换一些长的编码为简写
        if StringUtils.is_string_and_not_empty(self.audio_encode):
            self.audio_encode = self.audio_encode.replace("Dolby Digital Plus", "DDP")

        title_audio_channels = self._media_item_title.audio.audio_channels
        subltitle_audio_channels = self._media_item_subtitle.audio.audio_channels

        audio_channels = ""
        if isinstance(title_audio_channels, list) and len(title_audio_channels) > 0:
            audio_channels = " ".join(title_audio_channels)
        elif isinstance(subltitle_audio_channels, list) and len(subltitle_audio_channels) > 0:
            audio_channels = " ".join(subltitle_audio_channels)
        else:
            if StringUtils.is_string_and_not_empty(title_audio_channels):
                audio_channels = title_audio_channels
            elif StringUtils.is_string_and_not_empty(subltitle_audio_channels):
                audio_channels = subltitle_audio_channels

        if not StringUtils.is_string_and_not_empty(audio_channels):
            return

        if StringUtils.is_string_and_not_empty(self.audio_encode):
            self.audio_encode += f" {audio_channels}"
        else:
            self.audio_encode = audio_channels


    def __fix_resource_team(self):
        if StringUtils.is_string_and_not_empty(self.resource_team):
            return
        title_resource_teams = self._media_item_title.main.release_group
        subltitle_resource_teams = self._media_item_subtitle.main.release_group

        if isinstance(title_resource_teams, list) and len(title_resource_teams) > 0:
            self.resource_team = "&".join(title_resource_teams)
        elif isinstance(subltitle_resource_teams, list) and len(subltitle_resource_teams) > 0:
            self.resource_team = "&".join(subltitle_resource_teams)
        else:
            if StringUtils.is_string_and_not_empty(title_resource_teams):
                self.resource_team = title_resource_teams
            elif StringUtils.is_string_and_not_empty(subltitle_resource_teams):
                self.resource_team = subltitle_resource_teams
            else:
                self.resource_team = None

        special_resource_team_matches = re.findall(r'%s' % self._special_resource_team, self._original_title)
        if len(special_resource_team_matches) > 1:
            special_resource_team_text = ' '.join(special_resource_team_matches)
        else:
            special_resource_team_text = special_resource_team_matches[0] if special_resource_team_matches else ""
        if special_resource_team_text:
            self.resource_team += f" {special_resource_team_text}"
            self.resource_team = self.resource_team.rstrip()

    def guess_media_item(self, title, subtitle):
        """
        通过标题和副标题获取信息
        """
        media_item_title = MediaItem(datas=default_api.guessit(title or ""))
        media_item_subtitle = MediaItem(datas=default_api.guessit(subtitle or ""))

        return media_item_title, media_item_subtitle

    def __fix_release_group(self, title):
        if not StringUtils.is_string_and_not_empty(title):
            return None
        # 定义正则表达式模式，匹配以英文 [任意内容] 或中文 【任意内容】 开头的部分
        pattern = r'^(\[[^\]]+\]|【[^】]+】)'
        # 定义关键词列表，包含需要检查的关键词
        keywords = ["raws", "raw", "sub", "studio", "搬运组", "搬運組", "字幕组", "字幕組", "漢化組", "汉化组",
                    "发布组", "發佈組", "字幕团", "字幕社", "工作室", "制作组", "制作組", "Team",
                    "LoliHouse", "ANi", "喵萌", "c.c動漫", "c.c动漫", "压制", "MagicStar",
                    "芝士动物朋友", "招募", "丸子家族", "LoveEcho!", "VCB-Studio", "虹咲学园烤肉同好会",
                    "練習組", "练习组", "夜莺家族", "APTX4869", "事务所", "新番", "合集", "连载",
                    "日剧", "美剧", "电视剧", "动画片", "动漫", "欧美", "西德", "日韩", "超高清", "高清", "蓝光",
                    "翡翠台", "梦幻天堂", "毀片黨", "毁片党", "论坛", "ViuTV", "PTS", "JADE", "AOD", "CHC",
                    "周年", "纪念版", "白金", "特效", "首发", "原盘", "❀拨雪寻春❀", "喵萌奶茶屋", "熔岩动画",
                    "Xrip", "AKito秋人", "智械尚未危机制作", "jibaketa", "亿次研同好会", "VARYG", "B站小鱼儿呼唤爱",
                    "hchcsen", "niizk", "Xeon晚生", "氢气烤肉架", "7³ACG", "LittleBakas", "FSD粉羽社", "一只出格君",
                    "OPFans枫雪动漫"]

        match = re.search(pattern, title, re.IGNORECASE)
        if not match:
            return title

        matched_part = match.group(0)
        if not matched_part:
            return title

        contains_keyword = any(keyword.lower() in matched_part.lower() for keyword in keywords)
        if not contains_keyword:
            return title

        title = title.replace(matched_part, '', 1)
        title += matched_part

        return title

    def __fix_title(self, title):
        if not StringUtils.is_string_and_not_empty(title):
            return

        title = re.sub(r"[*?\\/\"<>~|]", "", title, flags=re.IGNORECASE) \
            .replace("-", ".") \
            .replace("【",  "[") \
            .replace("】", "]") \

        # 将开头字幕组信息移动至字符串末尾
        title = self.__fix_release_group(title)
        # 去除其他不重要的信息
        title = re.sub(r'%s' % self._other_re, '', title, flags=re.IGNORECASE)
        # 中括号里单独的数字大概率是集数
        title = re.sub(r'\[(\d+)\]', r'[E\1]', title, flags=re.IGNORECASE)

        if title.startswith("["):
            title = title.replace("[", "", 1)
        title = title.replace("[", ".")
        title = title.replace("]", ".")

        # 匹配出季组
        seasons_pattern = f"({self._seasons_re}|{self._seasons_re_2})"
        seasons_match = re.search(r'%s' % seasons_pattern, title, flags=re.IGNORECASE)
        if seasons_match:
            seasons_match_text = seasons_match.group(0)
            seasons = re.findall(r'%s' % self._numbers_re, seasons_match_text, flags=re.IGNORECASE)
            seasons = sorted(seasons)
            if len(seasons) >= 2:
                try:
                    begin_season = int(cn2an.cn2an(seasons[0], "smart"))
                    end_season = int(cn2an.cn2an(seasons[-1], "smart"))
                    title = re.sub(r'%s' % seasons_pattern, f".S{begin_season}-S{end_season}.", title, flags=re.IGNORECASE)
                except Exception as e:
                    pass
        else:
            # 匹配出季
            seasons_pattern = f"({self._season_re}|{self._season_re_2})"
            season_match = re.search(r'%s' % seasons_pattern, title, flags=re.IGNORECASE)
            if season_match:
                season_matched_text = season_match.group(0)
                season = re.findall(r'%s' % self._numbers_re, season_matched_text, flags=re.IGNORECASE)[0]
                if season:
                    season = re.sub(r'^0+', '', season)
                    try:
                        fix_season = cn2an.cn2an(season, "smart")
                        fix_season = int(fix_season)
                        title = re.sub(r'%s' % seasons_pattern, f".S{fix_season}.", title, flags=re.IGNORECASE)
                    except Exception as e:
                        pass

        # 匹配出集组
        episodes_pattern = f"({self._episodes_re}|{self._episodes_re_2})"
        episodes_match = re.search(r'%s' % episodes_pattern, title, flags=re.IGNORECASE)
        if episodes_match:
            episodes_match_text = episodes_match.group(0)
            episodes = re.findall(r'%s' % self._numbers_re, episodes_match_text, flags=re.IGNORECASE)
            episodes = sorted(episodes)
            if len(episodes) >= 2:
                try:
                    begin_episode = int(cn2an.cn2an(episodes[0], "smart"))
                    end_episode = int(cn2an.cn2an(episodes[-1], "smart"))
                    title = re.sub(r'%s' % episodes_pattern, f".E{begin_episode}-E{end_episode}.", title, flags=re.IGNORECASE)
                except Exception as e:
                    pass
        else:
            # 匹配出集
            episode_pattern = f"({self._episode_re}|{self._episode_re_2})"
            episode_match = re.search(r'%s' % episode_pattern, title, flags=re.IGNORECASE)
            if episode_match:
                episode_matched_text = episode_match.group(0)
                episode = re.findall(r'%s' % self._numbers_re, episode_matched_text, flags=re.IGNORECASE)[0]
                if episode:
                    episode = re.sub(r'^0+', '', episode)
                    try:
                        fix_episode = cn2an.cn2an(episode, "smart")
                        fix_episode = int(fix_episode)
                        title = re.sub(r'%s' % episode_pattern, f".E{fix_episode}.", title, flags=re.IGNORECASE)
                    except Exception as e:
                        pass

        # 匹配出年份范围
        years_match = re.search(r'%s' % self._years_re, title)
        if years_match:
            begin_year = years_match.group(1)
            end_year = years_match.group(2)
            try:
                begin_year_number = int(cn2an.cn2an(begin_year, "smart"))
                end_year_number = int(cn2an.cn2an(end_year, "smart"))
                max_year_number = end_year_number if end_year_number >= begin_year_number else begin_year_number
                title = re.sub(r'%s' % self._years_re, f"{max_year_number}", title)
            except Exception as e:
                pass

        # 替换连续的多个.为一个.
        title = re.sub(r'\.{2,}', '.', title).rstrip('.')
        # 去除XX月新番
        title = re.sub(r'%s' % self._release_date_re, '', title)
        # 去除多音轨标志
        title = re.sub(r'\d+Audio', '', title)
        # 去掉名称中第1个[]的内容
        title = re.sub(r'%s' % self._name_no_begin_re, "", title, count=1)
        # 把xxxx-xxxx年份换成较大的年份，常出现在季集上
        title = re.sub(r'([\s.]+)(\d{4})-(\d{4})', r'\1\2', title)
        # 把大小去掉
        title = re.sub(r'[0-9.]+\s*[MGT]i?B(?![A-Z]+)', "", title, flags=re.IGNORECASE)
        # 把年月日去掉
        title = re.sub(r'\d{4}[\s._-]\d{1,2}[\s._-]\d{1,2}', "", title)
        # 替换 - 为 .
        title = title.replace("-", ".")

        return title

    def __fix_name(self, name):
        if not name:
            return name
        name = re.sub(r'%s' % self._name_nostring_re, '', name,
                      flags=re.IGNORECASE).strip()
        name = re.sub(r'\s+', ' ', name)
        if name.isdigit() \
                and int(name) < 1800 \
                and not self.year \
                and not self.begin_season \
                and not self.resource_pix \
                and not self.resource_type \
                and not self.audio_encode \
                and not self.video_encode:
            if self.begin_episode is None:
                self.begin_episode = int(name)
                name = None
            elif self.is_in_episode(int(name)) and not self.begin_season:
                name = None
        return name

    def __fix_season(self):
        # 修正年份被识别为季
        if self.begin_season and self.year and self.begin_season == self.year:
            self.begin_season = None

        if not StringUtils.is_string_and_not_empty(self._original_subtitle):
            self._original_subtitle = ""
        fixed_subtitle = self._original_subtitle.replace("-", ".")

        # 匹配出季组
        seasons_pattern = f"({self._seasons_re}|{self._seasons_re_2})"
        seasons_match = re.search(r'%s' % seasons_pattern, fixed_subtitle, flags=re.IGNORECASE)
        if seasons_match:
            seasons_match_text = seasons_match.group(0)
            seasons = re.findall(r'%s' % self._numbers_re, seasons_match_text, flags=re.IGNORECASE)
            seasons = sorted(seasons)
            if len(seasons) >= 2:
                try:
                    begin_season = int(cn2an.cn2an(seasons[0], "smart"))
                    end_season = int(cn2an.cn2an(seasons[-1], "smart"))
                    self.begin_season = begin_season
                    self.end_season = end_season
                    self.total_seasons = begin_season if begin_season == end_season else end_season
                except Exception as e:
                    pass
        else:
            # 匹配出季
            seasons_pattern = f"({self._season_re}|{self._season_re_2})"
            season_match = re.search(r'%s' % seasons_pattern, fixed_subtitle, flags=re.IGNORECASE)
            if season_match:
                season_matched_text = season_match.group(0)
                season = re.findall(r'%s' % self._numbers_re, season_matched_text, flags=re.IGNORECASE)[0]
                if season:
                    season = re.sub(r'^0+', '', season)
                    fix_season = cn2an.cn2an(season, "smart")
                    try:
                        fix_season = int(fix_season)
                        self.begin_season = fix_season
                        self.end_episode = None
                        self.total_seasons = 1
                    except Exception as e:
                        pass

        # 匹配出总季数
        season_all_match_pattern = f"({self._season_all_re}|{self._season_all_re_2})"
        season_all_match = re.search(r'%s' % season_all_match_pattern, fixed_subtitle, flags=re.IGNORECASE)
        if season_all_match:
            season_all = None
            season_all_number_match = re.search(r'%s' % self._numbers_re, season_all_match.group(1))
            if season_all_number_match:
                season_all = season_all_number_match.group(0)
            if season_all:
                season_all = re.sub(r'^0+', '', season_all)
                try:
                    fix_season_all = cn2an.cn2an(season_all, "smart")
                    fix_season_all = int(fix_season_all)
                    self.begin_season = 1
                    self.end_season = None if fix_season_all == 1 else fix_season_all
                    self.total_seasons = fix_season_all
                except Exception as e:
                    pass

        # 如果副标题没有总季数，从主标题在匹配一遍看是否有总季数，以免遗漏
        fixed_title = self._original_title.replace("-", ".")
        season_all_match_pattern = f"({self._season_all_re}|{self._season_all_re_2})"
        season_all_by_title_match = re.search(r'%s' % season_all_match_pattern, fixed_title, flags=re.IGNORECASE)
        if season_all_by_title_match:
            season_all = None
            season_all_number_match = re.search(r'%s' % self._numbers_re, season_all_by_title_match.group(1))
            if season_all_number_match:
                season_all = season_all_number_match.group(0)
            if season_all:
                season_all = re.sub(r'^0+', '', season_all)
                try:
                    fix_season_all = cn2an.cn2an(season_all, "smart")
                    fix_season_all = int(fix_season_all)
                    self.begin_season = 1
                    self.end_season = None if fix_season_all == 1 else fix_season_all
                    self.total_seasons = fix_season_all
                except Exception as e:
                    pass

        if self.begin_season and self.end_season and self.begin_season == self.end_season:
            self.end_season = None

    def __fix_episode(self):
        if not StringUtils.is_string_and_not_empty(self._original_subtitle):
            self._original_subtitle = ""
        fixed_subtitle = self._original_subtitle.replace("-", ".")

        # 匹配出集组
        episodes_pattern = f"({self._episodes_re}|{self._episodes_re_2})"
        episodes_match = re.search(r'%s' % episodes_pattern, fixed_subtitle, flags=re.IGNORECASE)
        if episodes_match:
            episodes_match_text = episodes_match.group(0)
            episodes = re.findall(r'%s' % self._numbers_re, episodes_match_text, flags=re.IGNORECASE)
            episodes = sorted(episodes)
            if len(episodes) >= 2:
                try:
                    begin_episode = int(cn2an.cn2an(episodes[0], "smart"))
                    end_episode = int(cn2an.cn2an(episodes[-1], "smart"))
                    self.begin_episode = begin_episode
                    self.end_episode = end_episode
                    self.total_episodes = begin_episode if begin_episode == end_episode else end_episode
                except Exception as e:
                    pass
        else:
            # 匹配出集
            episode_pattern = f"({self._episode_re}|{self._episode_re_2})"
            episode_match = re.search(r'%s' % episode_pattern, fixed_subtitle, flags=re.IGNORECASE)
            if episode_match:
                episode_matched_text = episode_match.group(0)
                episode = re.findall(r'%s' % self._numbers_re, episode_matched_text, flags=re.IGNORECASE)[0]
                if episode:
                    episode = re.sub(r'^0+', '', episode)
                    try:
                        fix_episode = cn2an.cn2an(episode, "smart")
                        fix_episode = int(fix_episode)
                        self.begin_episode = fix_episode
                        self.end_episode = None
                        self.total_episodes = 1
                    except Exception as e:
                        pass

        # 匹配出总集数
        episode_all_match_pattern = f"({self._episode_all_re}|{self._episode_all_re_2})"
        episode_all_match = re.search(r'%s' % episode_all_match_pattern, fixed_subtitle, flags=re.IGNORECASE)
        if episode_all_match:
            episode_all = None
            episode_all_number_match = re.search(r'%s' % self._numbers_re, episode_all_match.group(1))
            if episode_all_number_match:
                episode_all = episode_all_number_match.group(0)
            if episode_all:
                episode_all = re.sub(r'^0+', '', episode_all)
                try:
                    fix_episode_all = cn2an.cn2an(episode_all, "smart")
                    fix_episode_all = int(fix_episode_all)
                    self.begin_episode = 1
                    self.end_episode = None if fix_episode_all == 1 else fix_episode_all
                    self.total_episodes = fix_episode_all
                except Exception as e:
                    pass

        # 如果副标题没有总集数，从主标题在匹配一遍看是否有总集数，以免遗漏
        fixed_title = self._original_title.replace("-", ".")
        episode_all_match_pattern = f"({self._episode_all_re}|{self._episode_all_re_2})"
        episode_all_by_title_match = re.search(r'%s' % episode_all_match_pattern, fixed_title, flags=re.IGNORECASE)
        if episode_all_by_title_match:
            episode_all = None
            episode_all_number_match = re.search(r'%s' % self._numbers_re, episode_all_by_title_match.group(1))
            if episode_all_number_match:
                episode_all = episode_all_number_match.group(0)
            if episode_all:
                episode_all = re.sub(r'^0+', '', episode_all)
                try:
                    fix_episode_all = cn2an.cn2an(episode_all, "smart")
                    fix_episode_all = int(fix_episode_all)
                    self.begin_episode = 1
                    self.end_episode = None if fix_episode_all == 1 else fix_episode_all
                    self.total_episodes = fix_episode_all
                except Exception as e:
                    pass

        if self.begin_episode and self.end_episode and self.begin_episode == self.end_episode:
            self.end_episode = None
            
        if self.begin_season and self.end_season and self.begin_season != self.end_season:
            self.begin_episode = None
            self.end_episode = None
            self.total_episodes = None

    def __fix_media_type(self):
        if self.begin_season or self.begin_episode:
            self.media_type = MediaType.TV
            self.type = MediaType.TV

    def __is_digit_array(self, arr):
        if not isinstance(arr, list):
            return False
        for element in arr:
            if not isinstance(element, (int, float)):
                return False
        return True

    def __is_digit(self, number):
        return isinstance(number, (int, float))


