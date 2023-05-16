from time import sleep

import pytest

from qbittorrentapi._version_support import v
from qbittorrentapi.exceptions import APIError
from qbittorrentapi.rss import RSSitemsDictionary
from tests.utils import check
from tests.utils import get_func

FOLDER_ONE = "testFolderOne"
FOLDER_TWO = "testFolderTwo"

ITEM_ONE = "YTS"
ITEM_TWO = "YTSNew"
URL = "https://yts.mx/rss/0/all/all/0/en"


@pytest.fixture(scope="function", autouse=True)
def rss_feed(client, api_version):
    def delete_feed(name):
        try:
            client.rss_remove_item(item_path=name)
            check(lambda: client.rss_items(), name, reverse=True, negate=True)
        except Exception:
            pass

    if v(api_version) >= v("2.2"):
        client.app.preferences = dict(rss_auto_downloading_enabled=False)
        # refreshing the feed is finicky...so try several times if necessary
        done = False
        for i in range(5):
            delete_feed(ITEM_ONE)
            client.rss.add_feed(url=URL, item_path=ITEM_ONE)
            check(lambda: client.rss_items(), ITEM_ONE, reverse=True)
            # wait until feed is refreshed
            for j in range(20):
                if client.rss.items.with_data[ITEM_ONE]["articles"]:
                    done = True
                    yield ITEM_ONE
                    delete_feed(ITEM_ONE)
                    break
                sleep(0.25)
            if done:
                break
        else:
            raise Exception("RSS Feed '%s' did not refresh..." % ITEM_ONE)
    else:
        yield ""


@pytest.mark.skipif_before_api_version("2.2.1")
@pytest.mark.parametrize(
    "client_func",
    ["rss_refresh_item", "rss_refreshItem", "rss.refresh_item", "rss.refreshItem"],
)
def test_refresh_item(client, rss_feed, client_func):
    get_func(client, client_func)(item_path=rss_feed)
    check(
        lambda: client.rss_items(include_feed_data=True)[rss_feed]["lastBuildDate"],
        "",
        negate=True,
    )
    last_refresh = client.rss_items(include_feed_data=True)[rss_feed]["lastBuildDate"]
    sleep(1)
    get_func(client, client_func)(item_path=rss_feed)
    check(
        lambda: client.rss_items(include_feed_data=True)[rss_feed]["lastBuildDate"],
        last_refresh,
        negate=True,
    )


# inconsistent behavior with endpoint for API version 2.2
@pytest.mark.skipif_after_api_version("2.2")
@pytest.mark.parametrize(
    "client_func",
    ["rss_refresh_item", "rss_refreshItem", "rss.refresh_item", "rss.refreshItem"],
)
def test_refresh_item_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.2")
@pytest.mark.parametrize("client_func", ["rss_items", "rss.items"])
def test_items(client, rss_feed, client_func):
    check(lambda: get_func(client, client_func)(), rss_feed, reverse=True)
    check(
        lambda: get_func(client, client_func)(include_feed_data=True),
        rss_feed,
        reverse=True,
    )
    check(
        lambda: get_func(client, client_func)(include_feed_data=True)[rss_feed],
        "articles",
        reverse=True,
    )

    if "." in client_func:
        check(
            lambda: get_func(client, client_func).without_data,
            rss_feed,
            reverse=True,
        )
        check(
            lambda: get_func(client, client_func).with_data[rss_feed],
            "articles",
            reverse=True,
        )


@pytest.mark.skipif_before_api_version("2.2")
@pytest.mark.parametrize("client_func", ["rss_items", "rss.items"])
def test_add_feed(client, rss_feed, client_func):
    assert rss_feed in get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.9.1")
@pytest.mark.parametrize(
    "client_func",
    ["rss_set_feed_url", "rss_setFeedURL", "rss.set_feed_url", "rss.setFeedURL"],
)
def test_set_feed_url(client, rss_feed, client_func):
    curr_feed_url = client.rss_items()[rss_feed].url
    new_feed_url = curr_feed_url + "asdf"
    get_func(client, client_func)(url=new_feed_url, item_path=rss_feed)
    assert new_feed_url == client.rss_items()[rss_feed].url


@pytest.mark.skipif_after_api_version("2.9.1")
@pytest.mark.parametrize(
    "client_func",
    ["rss_set_feed_url", "rss_setFeedURL", "rss.set_feed_url", "rss.setFeedURL"],
)
def test_set_feed_url_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.2")
@pytest.mark.parametrize(
    "client_func",
    ["rss_remove_item", "rss_removeItem", "rss.remove_item", "rss.removeItem"],
)
def test_remove_feed(client, rss_feed, client_func):
    get_func(client, client_func)(item_path=rss_feed)
    check(lambda: client.rss_items(), rss_feed, reverse=True, negate=True)


@pytest.mark.parametrize(
    "client_func",
    [
        ("rss_add_folder", "rss_remove_item"),
        ("rss_addFolder", "rss_removeItem"),
        ("rss.add_folder", "rss.remove_item"),
        ("rss.addFolder", "rss.removeItem"),
    ],
)
def test_add_remove_folder(client, client_func):
    name = "test_isos"

    get_func(client, client_func[0])(folder_path=name)  # add_folder
    check(lambda: client.rss_items(), name, reverse=True)
    get_func(client, client_func[1])(item_path=name)  # remove_folder
    check(lambda: client.rss_items(), name, reverse=True, negate=True)


@pytest.mark.skipif_before_api_version("2.2")
@pytest.mark.parametrize(
    "client_func", ["rss_move_item", "rss_moveItem", "rss.move_item", "rss.moveItem"]
)
def test_move(client, rss_feed, client_func):
    try:
        new_name = "new_loc"
        get_func(client, client_func)(orig_item_path=rss_feed, new_item_path=new_name)
        check(lambda: client.rss_items(), new_name, reverse=True)
    finally:
        try:
            client.rss_remove_item(item_path=new_name)
        except APIError:
            pass


@pytest.mark.skipif_before_api_version("2.5.1")
@pytest.mark.parametrize(
    "client_func",
    ["rss_mark_as_read", "rss_markAsRead", "rss.mark_as_read", "rss.markAsRead"],
)
def test_mark_as_read(client, rss_feed, client_func):
    item_id = client.rss.items.with_data[rss_feed]["articles"][0]["id"]
    get_func(client, client_func)(item_path=rss_feed, article_id=item_id)
    check(
        lambda: client.rss.items.with_data[rss_feed]["articles"][0],
        "isRead",
        reverse=True,
    )


@pytest.mark.skipif_after_api_version("2.5.1")
@pytest.mark.parametrize(
    "client_func",
    ["rss_mark_as_read", "rss_markAsRead", "rss.mark_as_read", "rss.markAsRead"],
)
def test_mark_as_read_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()


@pytest.mark.skipif_before_api_version("2.2")
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
            "rss_addFeed",
            "rss_setRule",
            "rss_rules",
            "rss_renameRule",
            "rss_matchingArticles",
            "rss_removeRule",
            "rss_removeItem",
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
        (
            "rss.addFeed",
            "rss.setRule",
            "rss.rules",
            "rss.renameRule",
            "rss.matchingArticles",
            "rss.removeRule",
            "rss.removeItem",
        ),
    ),
)
def test_rules(client, api_version, client_func):
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

    rule_name = ITEM_ONE + "Rule"
    rule_name_new = rule_name + "New"
    rule_def = {"enabled": True, "affectedFeeds": URL, "addPaused": True}
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
        get_func(client, client_func[6])(item_path=ITEM_ONE)  # rss_remove_item
        assert ITEM_TWO not in client.rss_items()
        check(lambda: client.rss_items(), ITEM_TWO, reverse=True, negate=True)


@pytest.mark.skipif_after_api_version("2.2")
@pytest.mark.parametrize(
    "client_func",
    [
        "rss_matching_articles",
        "rss_matchingArticles",
        "rss.matching_articles",
        "rss.matchingArticles",
    ],
)
def test_rules_not_implemented(client, client_func):
    with pytest.raises(NotImplementedError):
        get_func(client, client_func)()
