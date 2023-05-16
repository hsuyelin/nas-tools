from qbittorrentapi import Client


def test_is_logged_in():
    client = Client(
        RAISE_NOTIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS=True,
        VERIFY_WEBUI_CERTIFICATE=False,
    )
    assert client.is_logged_in is False

    client.auth_log_in()
    assert client.is_logged_in is True

    client.auth_log_out()
    assert client.is_logged_in is False


def test_session_cookie(app_version):
    client = Client(
        RAISE_NOTIMPLEMENTEDERROR_FOR_UNIMPLEMENTED_API_ENDPOINTS=True,
        VERIFY_WEBUI_CERTIFICATE=False,
    )
    assert client._session_cookie() is None

    # make the client perform a login
    assert client.app.version == app_version

    # should test other cookie names but it's difficult to change
    curr_sess_cookie = client._http_session.cookies["SID"]
    assert client._SID == curr_sess_cookie
    assert client._session_cookie() == curr_sess_cookie
