from app.media.tmdbv3api.as_obj import AsObj
from app.media.tmdbv3api.tmdb import TMDb
from app.utils import StringUtils

class Episode(TMDb):
    _urls = {
        "images": "/tv/%s/season/%s/episode/%s/images",
        "details": "/tv/%s/season/%s/episode/%s"
    }

    def images(self, tv_id, season_num, episode_num, include_image_language=None):
        """
        Get the images that belong to a TV episode.
        :param tv_id: int
        :param season_num: int
        :param episode_num: int
        :param include_image_language: str
        :return:
        """
        try:
            images = AsObj(
                **self._call(
                    self._urls["details"] % (tv_id, season_num, episode_num),
                    "language=%s" % include_image_language if include_image_language else "" + "&append_to_response=images"
                )
            )
            if not images:
                return None
            still_path = images.get("still_path")
            if isinstance(still_path, str):
                return [{"file_path": still_path}]
            elif isinstance(still_path, list):
                return [
                    {"file_path": str(file_path)}
                    for file_path in images
                    if StringUtils.is_string_and_not_empty(file_path)
                ]
            else:
                return None
        except Exception as e:
            return None
