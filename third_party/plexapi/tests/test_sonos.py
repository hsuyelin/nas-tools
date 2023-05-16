# -*- coding: utf-8 -*-
from .payloads import SONOS_RESOURCES


def test_sonos_resources(mocked_account, requests_mock):
    requests_mock.get("https://sonos.plex.tv/resources", text=SONOS_RESOURCES)

    speakers = mocked_account.sonos_speakers()
    assert len(speakers) == 3

    # Finds individual speaker by name
    speaker1 = mocked_account.sonos_speaker("Speaker 1")
    assert speaker1.machineIdentifier == "RINCON_12345678901234561:1234567891"

    # Finds speaker as part of group
    speaker1 = mocked_account.sonos_speaker("Speaker 2")
    assert speaker1.machineIdentifier == "RINCON_12345678901234562:1234567892"

    # Finds speaker by Plex identifier
    speaker3 = mocked_account.sonos_speaker_by_id("RINCON_12345678901234563:1234567893")
    assert speaker3.title == "Speaker 3"

    # Finds speaker by Sonos identifier
    speaker3 = mocked_account.sonos_speaker_by_id("RINCON_12345678901234563")
    assert speaker3.title == "Speaker 3"

    assert mocked_account.sonos_speaker("Speaker X") is None
    assert mocked_account.sonos_speaker_by_id("ID_DOES_NOT_EXIST") is None
