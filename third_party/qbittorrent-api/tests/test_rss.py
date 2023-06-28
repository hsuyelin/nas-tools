from time import sleep

import pytest

from qbittorrentapi._version_support import v
from qbittorrentapi.rss import RSSitemsDictionary
from tests.conftest import check
from tests.conftest import get_func

folder_one = "testFolderOne"
folder_two = "testFolderTwo"

item_one = "YTS"
item_two = "YTSNew"
url = "https://yts.mx/rss/0/all/all/0/en"


def test_refresh_item(client, api_version, rss_feed):
    if v(api_version) >= v("2.2"):
        client.rss_refresh_item(item_path=rss_feed)
        check(
            lambda: client.rss_items(include_feed_data=True)[rss_feed]["lastBuildDate"],
            "",
            negate=True,
            check_limit=20,
        )
        last_refresh = client.rss_items(include_feed_data=True)[rss_feed][
            "lastBuildDate"
        ]
        sleep(1)
        client.rss_refresh_item(item_path=rss_feed)
        check(
            lambda: client.rss_items(include_feed_data=True)[rss_feed]["lastBuildDate"],
            last_refresh,
            negate=True,
            check_limit=20,
        )
    else:
        with pytest.raises(NotImplementedError):
            client.rss_refresh_item(item_path=rss_feed)

    if v(api_version) >= v("2.2"):
        client.rss.refresh_item(item_path=rss_feed)
        check(
            lambda: client.rss_items(include_feed_data=True)[rss_feed]["lastBuildDate"],
            "",
            negate=True,
            check_limit=20,
        )
        last_refresh = client.rss_items(include_feed_data=True)[rss_feed][
            "lastBuildDate"
        ]
        sleep(1)
        client.rss.refresh_item(item_path=rss_feed)
        check(
            lambda: client.rss_items(include_feed_data=True)[rss_feed]["lastBuildDate"],
            last_refresh,
            negate=True,
            check_limit=20,
        )
    else:
        with pytest.raises(NotImplementedError):
            client.rss.refresh_item(item_path=rss_feed)


def test_items(client, api_version, rss_feed):
    if v(api_version) >= v("2.2"):
        check(lambda: client.rss_items(), rss_feed, reverse=True)
        check(lambda: client.rss_items(include_feed_data=True), rss_feed, reverse=True)
        check(
            lambda: client.rss_items(include_feed_data=True)[rss_feed],
            "articles",
            reverse=True,
        )

        check(lambda: client.rss.items(), rss_feed, reverse=True)
        check(lambda: client.rss.items.without_data, rss_feed, reverse=True)
        check(lambda: client.rss.items.with_data[rss_feed], "articles", reverse=True)


def test_add_feed(client, api_version, rss_feed):
    if v(api_version) >= v("2.2"):
        if rss_feed not in client.rss_items():
            raise Exception("rss feed not found", client.rss_items())


def test_remove_feed1(client, api_version, rss_feed):
    if v(api_version) >= v("2.2"):
        client.rss_remove_item(item_path=rss_feed)
        check(lambda: client.rss_items(), rss_feed, reverse=True, negate=True)


def test_remove_feed2(client, api_version, rss_feed):
    if v(api_version) >= v("2.2"):
        client.rss.remove_item(item_path=rss_feed)
        check(lambda: client.rss_items(), rss_feed, reverse=True, negate=True)


def test_add_remove_folder(client, api_version):
    if v(api_version) >= v("2.2"):
        name = "test_isos"

        client.rss_add_folder(folder_path=name)
        check(lambda: client.rss_items(), name, reverse=True)
        client.rss_remove_item(item_path=name)
        check(lambda: client.rss_items(), name, reverse=True, negate=True)

        client.rss.add_folder(folder_path=name)
        check(lambda: client.rss.items(), name, reverse=True)
        client.rss.remove_item(item_path=name)
        check(lambda: client.rss.items(), name, reverse=True, negate=True)


def test_move(client, api_version, rss_feed):
    if v(api_version) >= v("2.2"):
        new_name = "new_loc"

        client.rss_move_item(orig_item_path=rss_feed, new_item_path=new_name)
        check(lambda: client.rss_items(), new_name, reverse=True)

        client.rss.move_item(orig_item_path=new_name, new_item_path=rss_feed)
        check(lambda: client.rss.items(), rss_feed, reverse=True)


def test_mark_as_read(client, api_version, rss_feed):
    if v(api_version) >= v("2.5.1"):
        item_id = client.rss.items.with_data[rss_feed]["articles"][0]["id"]
        client.rss_mark_as_read(item_path=rss_feed, article_id=item_id)
        check(
            lambda: client.rss.items.with_data[rss_feed]["articles"][0],
            "isRead",
            reverse=True,
        )
    else:
        with pytest.raises(NotImplementedError):
            client.rss_mark_as_read(item_path=rss_feed, article_id=1)

    if v(api_version) >= v("2.5.1"):
        item_id = client.rss.items.with_data[rss_feed]["articles"][1]["id"]
        client.rss.mark_as_read(item_path=rss_feed, article_id=item_id)
        check(
            lambda: client.rss.items.with_data[rss_feed]["articles"][1],
            "isRead",
            reverse=True,
        )
    else:
        with pytest.raises(NotImplementedError):
            client.rss.mark_as_read(item_path=rss_feed, article_id=1)


@pytest.mark.parametrize(
    "client_func",
    (
        (
            "rss_add_feed",
            "rss_set_rule",
            "rss_rules",
            "rss_rename_rule",
            "rss_matching_articles",
            "rss_remove_rule",
            "rss_remove_item",
        ),
        (
            "rss.add_feed",
            "rss.set_rule",
            "rss.rules",
            "rss.rename_rule",
            "rss.matching_articles",
            "rss.remove_rule",
            "rss.remove_item",
        ),
    ),
)
def test_rules(client, api_version, client_func, rss_feed):
    def check_for_rule(name):
        try:
            get_func(client, client_func[2])()  # rss_rules
            check(
                lambda: get_func(client, client_func[2])(), name, reverse=True
            )  # rss_rules
        except TypeError:
            check(
                lambda: get_func(client, client_func[2]), name, reverse=True
            )  # rss_rules

    if v(api_version) >= v("2.2"):
        _ = rss_feed  # reference to avoid errors; needed to load RSS feed in to qbt
        rule_name = item_one + "Rule"
        rule_name_new = rule_name + "New"
        rule_def = {"enabled": True, "affectedFeeds": url, "addPaused": True}
        try:
            # rss_set_rule
            get_func(client, client_func[1])(rule_name=rule_name, rule_def=rule_def)
            check_for_rule(rule_name)

            if v(api_version) >= v("2.6"):  # rename was broken for a bit
                get_func(client, client_func[3])(
                    orig_rule_name=rule_name, new_rule_name=rule_name_new
                )  # rss_rename_rule
                check_for_rule(rule_name_new)
            if v(api_version) >= v("2.5.1"):
                assert isinstance(
                    get_func(client, client_func[4])(rule_name=rule_name),
                    RSSitemsDictionary,
                )  # rss_matching_articles
            else:
                with pytest.raises(NotImplementedError):
                    get_func(client, client_func[4])(
                        rule_name=rule_name
                    )  # rss_matching_articles
        finally:
            get_func(client, client_func[5])(rule_name=rule_name)  # rss_remove_rule
            get_func(client, client_func[5])(rule_name=rule_name_new)  # rss_remove_rule
            check(lambda: client.rss_rules(), rule_name, reverse=True, negate=True)
            get_func(client, client_func[6])(item_path=item_one)  # rss_remove_item
            assert item_two not in client.rss_items()
            check(lambda: client.rss_items(), item_two, reverse=True, negate=True)
