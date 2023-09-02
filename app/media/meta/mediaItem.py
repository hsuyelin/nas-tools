import json

class MediaMainItem:

    def __init__(self, 
                 datas=None,
                 media_type=None, 
                 title=None, 
                 alternative_title=None, 
                 container=None,
                 mimetype=None,
                 date=None,
                 year=None,
                 week=None,
                 release_group=None,
                 website=None,
                 streaming_service=None):
        if not datas:
            datas = {}
        self.media_type = datas.get('type', '') if not media_type else media_type
        self.title = datas.get('title', '') if not title else title
        self.alternative_title = datas.get('alternative_title', '') if not alternative_title else alternative_title
        self.container = datas.get('container', '') if not container else container
        self.mimetype = datas.get('mimetype', '') if not mimetype else mimetype
        self.date = datas.get('date', '') if not date else date
        self.year = datas.get('year', '') if not year else year
        self.week = datas.get('week', '') if not week else week
        self.release_group = datas.get('release_group', '') if not release_group else release_group
        self.website = datas.get('website', '') if not website else website
        self.streaming_service = datas.get('streaming_service', '') if not streaming_service else streaming_service

    def to_dict(self):
        return {
            "media_type": self.media_type or "",
            "title": self.title or "",
            "alternative_title": self.alternative_title or "",
            "container": self.container or "",
            "mimetype": self.mimetype or "",
            "date": self.date or "",
            "year": self.year or "",
            "week": self.week or "",
            "release_group": self.release_group or "",
            "website": self.website or "",
            "streaming_service": self.streaming_service or ""
        }

    def to_dict_str(self, ensure_ascii=False, formatted=True):
        if formatted:
            return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=4)
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)

class MediaEpisodeItem:

    def __init__(self, 
                 datas=None,
                 season=None, 
                 episode=None, 
                 disc=None, 
                 episode_count=None,
                 season_count=None,
                 episode_details=None,
                 episode_format=None,
                 part=None,
                 version=None):
        if not datas:
            datas = {}
        self.season = datas.get('season', '') if not season else season
        self.episode = datas.get('episode', '') if not episode else episode
        self.disc = datas.get('disc', '') if not disc else disc
        self.episode_count = datas.get('episode_count', '') if not episode_count else episode_count
        self.season_count = datas.get('season_count', '') if not season_count else season_count
        self.episode_details = datas.get('episode_details', '') if not episode_details else episode_details
        self.episode_format = datas.get('episode_format', '') if not episode_format else episode_format
        self.part = datas.get('part', '') if not part else part
        self.version = datas.get('version', '') if not version else version

    def to_dict(self):
        return {
            "season": self.season or "",
            "episode": self.episode or "",
            "episode_count": self.episode_count or "",
            "season_count": self.season_count or "",
            "episode_details": self.episode_details or "",
            "episode_format": self.episode_format or "",
            "part": self.part or "",
            "version": self.version or ""
        }

    def to_dict_str(self, ensure_ascii=False, formatted=True):
        if formatted:
            return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=4)
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)

class MediaVideoItem:

    def __init__(self, 
                 datas=None,
                 source=None, 
                 screen_size=None, 
                 aspect_ratio=None, 
                 video_codec=None,
                 video_profile=None,
                 color_depth=None,
                 video_bit_rate=None,
                 frame_rate=None):
        if not datas:
            datas = {}
        self.source = datas.get('source') if not source else source
        self.screen_size = datas.get('screen_size') if not screen_size else screen_size
        self.aspect_ratio = datas.get('aspect_ratio') if not aspect_ratio else aspect_ratio
        self.video_codec = datas.get('video_codec') if not video_codec else video_codec
        self.video_profile = datas.get('video_profile') if not video_profile else video_profile
        self.color_depth = datas.get('color_depth') if not color_depth else color_depth
        self.video_bit_rate = datas.get('video_bit_rate') if not video_bit_rate else video_bit_rate
        self.frame_rate = datas.get('frame_rate') if not frame_rate else frame_rate

    def to_dict(self):
        return {
            "source": self.source or "",
            "screen_size": self.screen_size or "",
            "aspect_ratio": self.aspect_ratio or "",
            "video_codec": self.video_codec or "",
            "video_profile": self.video_profile or "",
            "color_depth": self.color_depth or "",
            "video_bit_rate": self.video_bit_rate or "",
            "frame_rate": self.frame_rate or ""
        }

    def to_dict_str(self, ensure_ascii=False, formatted=True):
        if formatted:
            return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=4)
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)

class MediaAudioItem:

    def __init__(self, 
                 datas=None,
                 audio_channels=None, 
                 audio_codec=None, 
                 audio_profile=None, 
                 audio_bit_rate=None):
        if not datas:
            datas = {}
        self.audio_channels = datas.get('audio_channels', '') if not audio_channels else audio_channels
        self.audio_codec = datas.get('audio_codec', '') if not audio_codec else audio_codec
        self.audio_profile = datas.get('audio_profile', '') if not audio_profile else audio_profile
        self.audio_bit_rate = datas.get('audio_bit_rate', '') if not audio_bit_rate else audio_bit_rate

    def to_dict(self):
        return {
            "audio_channels": self.audio_channels or "",
            "audio_codec": self.audio_codec or "",
            "audio_profile": self.audio_profile or "",
            "audio_bit_rate": self.audio_bit_rate or ""
        }

    def to_dict_str(self, ensure_ascii=False, formatted=True):
        if formatted:
            return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=4)
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)

class MediaLocalizationItem:

    def __init__(self, 
                 datas=None,
                 country=None, 
                 language=None, 
                 subtitle_language=None):
        if not datas:
            datas = {}
        self.country = datas.get('country', '') if not country else country
        self.language = datas.get('language', '') if not language else language
        self.subtitle_language = datas.get('subtitle_language', '') if not subtitle_language else subtitle_language

    def to_dict(self):
        return {
            "country": self.country or "",
            "language": self.language or "",
            "subtitle_language": self.subtitle_language or ""
        }

    def to_dict_str(self, ensure_ascii=False, formatted=True):
        if formatted:
            return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=4)
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)

class MediaOtherItem:

    def __init__(self,
                 datas=None,
                 bonus=None,
                 bonus_title=None,
                 cd=None,
                 cd_count=None,
                 crc32=None,
                 uuid=None,
                 size=None,
                 edition=None,
                 film=None,
                 film_title=None,
                 film_series=None,
                 other=None):
        if not datas:
            datas = {}
        self.bonus = datas.get('bonus', '') if not bonus else bonus
        self.bonus_title = datas.get('bonus_title', '') if not bonus_title else bonus_title
        self.cd = datas.get('cd', '') if not cd else cd
        self.cd_count = datas.get('cd_count', '') if not cd_count else cd_count
        self.crc32 = datas.get('crc32', '') if not crc32 else crc32
        self.uuid = datas.get('uuid', '') if not uuid else uuid
        self.size = datas.get('size', '') if not size else size
        self.edition = datas.get('edition', '') if not edition else edition
        self.film = datas.get('film', '') if not film else film
        self.film_title = datas.get('film_title', '') if not film_title else film_title
        self.film_series = datas.get('film_series', '') if not film_series else film_series
        self.other = datas.get('other', '') if not other else other

    def to_dict(self):
        return {
            "bonus": self.bonus or "",
            "bonus_title": self.bonus_title or "",
            "cd": self.cd or "",
            "cd_count": self.cd_count or "",
            "crc32": self.crc32 or "",
            "uuid": self.uuid or "",
            "size": self.size or "",
            "edition": self.edition or "",
            "film": self.film or "",
            "film_title": self.film_title or "",
            "film_series": self.film_series or "",
            "other": self.other or ""
        }

    def to_dict_str(self, ensure_ascii=False, formatted=True):
        if formatted:
            return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=4)
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)

class MediaItem:

    def __init__(self, datas=None):
        if not isinstance(datas, dict):
            return

        self.main = MediaMainItem(datas=datas)
        self.episode = MediaEpisodeItem(datas=datas)
        self.video = MediaVideoItem(datas=datas)
        self.audio = MediaAudioItem(datas=datas)
        self.localization = MediaLocalizationItem(datas=datas)
        self.other = MediaOtherItem(datas=datas)

    def to_dict(self):
        return {
            "main": self.main.to_dict(),
            "episode": self.episode.to_dict(),
            "video": self.video.to_dict(),
            "audio": self.audio.to_dict(),
            "localization": self.localization.to_dict(),
            "other": self.other.to_dict()
        }

    def to_dict_str(self, ensure_ascii=False, formatted=True):
        if formatted:
            return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=4)
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii)


