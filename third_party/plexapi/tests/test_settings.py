def test_settings_group(plex):
    assert plex.settings.group("general")


def test_settings_get(plex):
    value = plex.settings.get("FriendlyName").value
    assert isinstance(value, str)


def test_settings_set(plex):
    cd = plex.settings.get("autoEmptyTrash")
    old_value = cd.value
    new_value = not old_value
    cd.set(new_value)
    plex.settings.save()
    del plex.__dict__['settings']
    assert plex.settings.get("autoEmptyTrash").value == new_value


def test_settings_set_str(plex):
    cd = plex.settings.get("OnDeckWindow")
    new_value = 99
    cd.set(new_value)
    plex.settings.save()
    del plex.__dict__['settings']
    assert plex.settings.get("OnDeckWindow").value == 99
