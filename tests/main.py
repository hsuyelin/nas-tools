from test_utils import TestUtils

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

#     movie1 = "Super.Mario.Bros.Movie.2023.4K.UHD.Blu-ray.REMUX.H265.10bit.Dolby.Vision.TrueHD.Atmos.mkv"
#     movie2 = "The Outcast S02 2017 1080p WEB-DL H265 AAC-HHWEB"
#     movie3 = "I AM Nobody S01 2023 1080p WEB-DL H264 AAC-HHWEB"
#     movie4 = "一人之下 - S01E01 - 阿威十八式.1024x576.WEB-DL.H264.AAC-HHWEB"
#     movie5 = "这个杀手不太冷.导演剪辑版.1024x576.WEB-DL.H264.AAC-HHWEB"
#     movie6 = "[HorribleSubs] 牙狼 -VANISHING LINE - 01 [1080p].mkv"
#     movie7 = "Spider-Man.Across.the.Spider-Verse.2023.2160p.WEB-DL.DDP5.1.Atmos.DV.H.265-yiiha"
#     print(TestUtils.guess_movie_info(movie1))
#     print(TestUtils.guess_movie_info(movie2))
#     print(TestUtils.guess_movie_info(movie3))
#     print(TestUtils.guess_movie_info(movie4))
#     print(TestUtils.guess_movie_info(movie5))
#     print(TestUtils.guess_movie_info(movie6))
#     print(TestUtils.guess_movie_info(movie7))

if __name__ == "__main__":
    main()