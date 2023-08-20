from test_utils import TestUtils

def main():
    html = """
<img class="pro_2Xfree" src="pic/trans.gif" alt="2XFree" title="免費">
    """

    matching_titles = TestUtils.find_matching_tables_with_title(html)
    if matching_titles:
        for title in matching_titles:
            print("match title - ", title)
    else:
        print("No match found.")

    matching_frees = TestUtils.find_matching_tables_with_free(html)
    if matching_frees:
        for free in matching_frees:
            print("match free success")
    else:
        print("No free")

    matching_2xfrees = TestUtils.find_matching_tables_with_2xfree(html)
    if matching_2xfrees:
        for free in matching_2xfrees:
            print("match 2xfree success")
    else:
        print("No 2xfree")

    name = "Super.？Mario.Bros.Movie,.：The.2023.4K.UHD.Blu-ray.REMUX.H265.10bit.Dolby.Vision.TrueHD.Atmos.mkv"
    print(TestUtils.clear_file_name(name))

if __name__ == "__main__":
    main()