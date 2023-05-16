import asyncio
from time import time

import pytest
from slack_sdk.signature import SignatureVerifier

from slack_bolt.middleware.request_verification.async_request_verification import (
    AsyncRequestVerification,
)
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_bolt.response import BoltResponse


async def next():
    return BoltResponse(status=200, body="next")


class TestAsyncRequestVerification:
    signing_secret = "secret"
    signature_verifier = SignatureVerifier(signing_secret)

    def generate_signature(self, body: str, timestamp: str):
        return self.signature_verifier.generate_signature(
            body=body,
            timestamp=timestamp,
        )

    def build_headers(self, timestamp: str, body: str):
        return {
            "content-type": ["application/x-www-form-urlencoded"],
            "x-slack-signature": [self.generate_signature(body, timestamp)],
            "x-slack-request-timestamp": [timestamp],
        }

    @pytest.fixture
    def event_loop(self):
        loop = asyncio.get_event_loop()
        yield loop
        loop.close()

    @pytest.mark.asyncio
    async def test_valid(self):
        middleware = AsyncRequestVerification(signing_secret="secret")
        timestamp = str(int(time()))
        raw_body = "payload={}"
        req = AsyncBoltRequest(body=raw_body, headers=self.build_headers(timestamp, raw_body))
        resp = BoltResponse(status=404)
        resp = await middleware.async_process(req=req, resp=resp, next=next)
        assert resp.status == 200
        assert resp.body == "next"

    @pytest.mark.asyncio
    async def test_invalid(self):
        middleware = AsyncRequestVerification(signing_secret="secret")
        req = AsyncBoltRequest(body="payload={}", headers={})
        resp = BoltResponse(status=404)
        resp = await middleware.async_process(req=req, resp=resp, next=next)
        assert resp.status == 401
        assert resp.body == """{"error": "invalid request"}"""
