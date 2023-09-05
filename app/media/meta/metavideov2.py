import re

from guessit.api import default_api

import log
from app.media.meta._base import MetaBase
from app.media.meta.release_groups import ReleaseGroupsMatcher
from app.media.meta.customization import CustomizationMatcher
from .mediaItem import MediaItem
from app.utils import StringUtils
from app.utils.types import MediaType

        
class MetaVideoV2(MetaBase):

    _media_item_title = None
    _media_item_subtitle = None

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

        original_title = title

        media_item_title, media_item_subtitle = self.guess_media_item(title, subtitle)
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
                    or re.findall(r'-D[Ii]Y@', original_title):
                self.resource_type = f"{self.resource_type} DIY"

        # 去掉名字中不需要的干扰字符，过短的纯数字不要
        self.cn_name = self.__fix_name(self.cn_name)
        self.en_name = StringUtils.str_title(self.__fix_name(self.en_name))

        # 制作组/字幕组
        self.resource_team = ReleaseGroupsMatcher().match(title=original_title) or None
        self.__fix_resource_team()
        # 自定义占位符
        self.customization = CustomizationMatcher().match(title=original_title) or None

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

        if StringUtils.is_chinese(name):
            self.cn_name = self.cn_name if StringUtils.is_string_and_not_empty(self.cn_name) else name
        else:
            self.en_name = self.en_name if StringUtils.is_string_and_not_empty(self.en_name) else name

        self.title = self.cn_name if StringUtils.is_string_and_not_empty(self.cn_name) else self.en_name

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

    def guess_media_item(self, title, subtitle):
        """
        通过标题和副标题获取信息
        """
        media_item_title = MediaItem(datas=default_api.guessit(title or ""))
        media_item_subtitle = MediaItem(datas=default_api.guessit(subtitle or ""))

        return media_item_title, media_item_subtitle

    def __fix_name(self, name):
        if not name:
            return name

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

    def __is_digit_array(self, arr):
        if not isinstance(arr, list):
            return False
        for element in arr:
            if not isinstance(element, (int, float)):
                return False
        return True

    def __is_digit(self, number):
        return isinstance(number, (int, float))


