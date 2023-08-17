import json
import subprocess

from app.utils import SystemUtils


class FfmpegHelper:

    @staticmethod
    def is_ffmpeg_supported():
        """
        是否支持ffmpeg
        """
        return not SystemUtils.is_windows()

    @staticmethod
    def get_thumb_image_from_video(video_path, image_path, frames="00:03:01"):
        """
        使用ffmpeg从视频文件中截取缩略图
        """
        if not video_path or not image_path:
            return False
        cmd = 'ffmpeg -i "{video_path}" -ss {frames} -vframes 1 -f image2 "{image_path}"'.format(video_path=video_path,
                                                                                                 frames=frames,
                                                                                                 image_path=image_path)
        result = SystemUtils.execute(cmd)
        if result:
            return True
        return False

    @staticmethod
    def extract_wav_from_video(video_path, audio_path, audio_index=None):
        """
        使用ffmpeg从视频文件中提取16000hz, 16-bit的wav格式音频
        """
        if not video_path or not audio_path:
            return False

        # 提取指定音频流
        if audio_index:
            command = ['ffmpeg', "-hide_banner", "-loglevel", "warning", '-y', '-i', video_path,
                       '-map', f'0:a:{audio_index}',
                       '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', audio_path]
        else:
            command = ['ffmpeg', "-hide_banner", "-loglevel", "warning", '-y', '-i', video_path,
                       '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', audio_path]

        ret = subprocess.run(command).returncode
        if ret == 0:
            return True
        return False

    @staticmethod
    def get_video_metadata(video_path):
        """
        获取视频元数据
        {
            "streams": [
                {
                    "index": 0,
                    "codec_name": "h264",
                    "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
                    "profile": "High",
                    "codec_type": "video",
                    "codec_tag_string": "avc1",
                    "codec_tag": "0x31637661",
                    "width": 1280,
                    "height": 720,
                    "coded_width": 1280,
                    "coded_height": 720,
                    "closed_captions": 0,
                    "film_grain": 0,
                    "has_b_frames": 4,
                    "sample_aspect_ratio": "1:1",
                    "display_aspect_ratio": "16:9",
                    "pix_fmt": "yuv420p",
                    "level": 40,
                    "color_range": "tv",
                    "color_space": "bt709",
                    "color_transfer": "bt709",
                    "color_primaries": "bt709",
                    "chroma_location": "left",
                    "field_order": "progressive",
                    "refs": 1,
                    "is_avc": "true",
                    "nal_length_size": "4",
                    "id": "0x1",
                    "r_frame_rate": "25/1",
                    "avg_frame_rate": "25/1",
                    "time_base": "1/16000",
                    "start_pts": 0,
                    "start_time": "0.000000",
                    "duration_ts": 42308480,
                    "duration": "2644.280000",
                    "bit_rate": "995126",
                    "bits_per_raw_sample": "8",
                    "nb_frames": "66107",
                    "extradata_size": 46,
                    "disposition": {
                        "default": 1,
                        "dub": 0,
                        "original": 0,
                        "comment": 0,
                        "lyrics": 0,
                        "karaoke": 0,
                        "forced": 0,
                        "hearing_impaired": 0,
                        "visual_impaired": 0,
                        "clean_effects": 0,
                        "attached_pic": 0,
                        "timed_thumbnails": 0,
                        "captions": 0,
                        "descriptions": 0,
                        "metadata": 0,
                        "dependent": 0,
                        "still_image": 0
                    },
                    "tags": {
                        "language": "und",
                        "handler_name": "VideoHandler",
                        "vendor_id": "[0][0][0][0]"
                    }
                },
                {
                    "index": 1,
                    "codec_name": "aac",
                    "codec_long_name": "AAC (Advanced Audio Coding)",
                    "profile": "LC",
                    "codec_type": "audio",
                    "codec_tag_string": "mp4a",
                    "codec_tag": "0x6134706d",
                    "sample_fmt": "fltp",
                    "sample_rate": "48000",
                    "channels": 2,
                    "channel_layout": "stereo",
                    "bits_per_sample": 0,
                    "initial_padding": 0,
                    "id": "0x2",
                    "r_frame_rate": "0/0",
                    "avg_frame_rate": "0/0",
                    "time_base": "1/48000",
                    "start_pts": 0,
                    "start_time": "0.000000",
                    "duration_ts": 126928880,
                    "duration": "2644.351667",
                    "bit_rate": "170682",
                    "nb_frames": "123954",
                    "extradata_size": 2,
                    "disposition": {
                        "default": 1,
                        "dub": 0,
                        "original": 0,
                        "comment": 0,
                        "lyrics": 0,
                        "karaoke": 0,
                        "forced": 0,
                        "hearing_impaired": 0,
                        "visual_impaired": 0,
                        "clean_effects": 0,
                        "attached_pic": 0,
                        "timed_thumbnails": 0,
                        "captions": 0,
                        "descriptions": 0,
                        "metadata": 0,
                        "dependent": 0,
                        "still_image": 0
                    },
                    "tags": {
                        "language": "und",
                        "handler_name": "SoundHandler",
                        "vendor_id": "[0][0][0][0]"
                    }
                }
            ],
            "format": {
                "filename": "/Users/hsuyelin/Downloads/咒术回战/Season 1/S01E01.mp4",
                "nb_streams": 2,
                "nb_programs": 0,
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "format_long_name": "QuickTime / MOV",
                "start_time": "0.000000",
                "duration": "2644.351667",
                "size": "387344177",
                "bit_rate": "1171838",
                "probe_score": 100,
                "tags": {
                    "major_brand": "isom",
                    "minor_version": "512",
                    "compatible_brands": "isomiso2avc1mp41",
                    "encoder": "Lavf58.29.100",
                    "description": "Packed by Bilibili XCoder v2.0.2"
                }
            }
        }
        """
        if not video_path:
            return False

        try:
            command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return json.loads(result.stdout.decode("utf-8"))
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def extract_subtitle_from_video(video_path, subtitle_path, subtitle_index=None):
        """
        从视频中提取字幕
        """
        if not video_path or not subtitle_path:
            return False

        if subtitle_index:
            command = ['ffmpeg', "-hide_banner", "-loglevel", "warning", '-y', '-i', video_path,
                       '-map', f'0:s:{subtitle_index}',
                       subtitle_path]
        else:
            command = ['ffmpeg', "-hide_banner", "-loglevel", "warning", '-y', '-i', video_path, subtitle_path]
        ret = subprocess.run(command).returncode
        if ret == 0:
            return True
        return False
