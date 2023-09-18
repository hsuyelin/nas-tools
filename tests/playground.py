import os
import sys

# # # 获取当前文件所在目录的上层目录，即项目根目录
# project_root = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
# # 将项目根目录添加到模块搜索路径中
# sys.path.append(project_root)

# from app.helper import OcrHelper
# from app.media.meta import MediaItem
from tests_utils import TestUtils

def main():
    print("hello world")
#     html = """
# <img class="pro_2Xfree" src="pic/trans.gif" alt="2XFree" title="免費">
#     """

#     matching_titles = TestUtils.find_matching_tables_with_title(html)
#     if matching_titles:
#         for title in matching_titles:
#             print("match title - ", title)
#     else:
#         print("No match found.")

#     matching_frees = TestUtils.find_matching_tables_with_free(html)
#     if matching_frees:
#         for free in matching_frees:
#             print("match free success")
#     else:
#         print("No free")

#     matching_2xfrees = TestUtils.find_matching_tables_with_2xfree(html)
#     if matching_2xfrees:
#         for free in matching_2xfrees:
#             print("match 2xfree success")
#     else:
#         print("No 2xfree")

#     name = "Super.？Mario.Bros.Movie,.：The.2023.4K.UHD.Blu-ray.REMUX.H265.10bit.Dolby.Vision.TrueHD.Atmos.mkv"
#     print(TestUtils.clear_file_name(name))

#     html1 = """
#     <h1 style="margin-top:15px;margin-buttom:-10px;color:#f29d38;font-size:20px;text-align:center;font-weight:bold;font-family:'Microsoft YaHei'">全站 [Free] 生效中！时间：2023-08-18 00:00:00 ~ 2023-08-24 23:59:59</h1>
#     <h1 style="margin-top:15px;margin-buttom:-10px;color:#f29d38;font-size:20px;text-align:center;font-weight:bold;font-family:'Microsoft YaHei'">全站生效中！时间：2023-08-18 00:00:00 ~ 2023-08-24 23:59:59</h1>
#     """
#     print(TestUtils.clean_all_sites_free(html1))

    # video1 = "Super.Mario.Bros.Movie.2023.4K.UHD.Blu-ray.REMUX.H265.10bit.Dolby.Vision.HDR10.TrueHD.Atmos.mkv"
    # video1_dict = TestUtils.guess_movie_info(video1)
    # video1_item = MediaItem(datas=video1_dict)
    # print(video1_item.to_dict_str())

    # video2 = "Teenage Mutant Ninja Turtles Mutant Mayhem 2023 2160p iTunes WEB-DL DDP5.1 Atmos DV H 265-HHWEB.mkv"
    # video2_dict = TestUtils.guess_movie_info(video2)
    # video2_item = MediaItem(datas=video2_dict)
    # print(video2_item.to_dict_str())

    # video3 = "I AM Nobody S01 2023 1080p WEB-DL H264 AAC-HHWEB"
    # video3_dict = TestUtils.guess_movie_info(video3)
    # video3_item = MediaItem(datas=video3_dict)
    # print(video3_item.to_dict_str())

    # video4 = "一人之下 - S01E1001-S01E1110 - 阿威十八式.1024x576.WEB-DL.H264.FLAC.AAC-HHWEB"
    # video4_dict = TestUtils.guess_movie_info(video4)
    # video4_item = MediaItem(datas=video4_dict)
    # print(video4_item.to_dict_str())

    # video5 = "夺宝奇兵5.Indiana Jones and the Dial of Destiny.2023.2160p.HDR.H265.内嵌中英字幕.mp4"
    # video5_dict = TestUtils.guess_movie_info(video5)
    # video5_item = MediaItem(datas=video5_dict)
    # print(video5_item.to_dict_str())

    # video6 = "[HorribleSubs] 牙狼 -VANISHING LINE - 01 [1080p].mkv"
    # video6_dict = TestUtils.guess_movie_info(video6)
    # video6_item = MediaItem(datas=video6_dict)
    # print(video6_item.to_dict_str())

    # video7 = "Spider-Man.Across.the.Spider-Verse.2023.2160p.WEB-DL.DDP5.1.H.265.Part.1-yiiha"
    # video7_dict = TestUtils.guess_movie_info(video7)
    # video7_item = MediaItem(datas=video7_dict)
    # print(video7_item.to_dict_str())
    
    # ocr_result = OcrHelper().get_captcha_text(image_url="https://www.yht7.com/upload/image/20191109/1735560-20191109220533186-1855679599.jpg")
    # print(ocr_result)

if __name__ == "__main__":
    main()