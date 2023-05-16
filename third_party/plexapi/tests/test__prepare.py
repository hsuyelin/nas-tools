# -*- coding: utf-8 -*-
import time

import pytest

MAX_ATTEMPTS = 60


def wait_for_idle_server(server):
    """Wait for PMS activities to complete with a timeout."""
    attempts = 0
    while server.activities and attempts < MAX_ATTEMPTS:
        print(f"Waiting for activities to finish: {server.activities}")
        time.sleep(1)
        attempts += 1
    assert attempts < MAX_ATTEMPTS, f"Server still busy after {MAX_ATTEMPTS}s"


def wait_for_metadata_processing(server):
    """Wait for async metadata processing to complete."""
    attempts = 0

    while True:
        busy = False
        for section in server.library.sections():
            tl = section.timeline()
            if tl.updateQueueSize > 0:
                busy = True
                print(f"{section.title}: {tl.updateQueueSize} items left")
        if not busy or attempts > MAX_ATTEMPTS:
            break
        time.sleep(1)
        attempts += 1
    assert attempts < MAX_ATTEMPTS, f"Metadata still processing after {MAX_ATTEMPTS}s"


def test_ensure_activities_completed(plex):
    wait_for_idle_server(plex)


@pytest.mark.authenticated
def test_ensure_activities_completed_authenticated(plex):
    wait_for_idle_server(plex)


def test_ensure_metadata_scans_completed(plex):
    wait_for_metadata_processing(plex)


@pytest.mark.authenticated
def test_ensure_metadata_scans_completed_authenticated(plex):
    wait_for_metadata_processing(plex)
