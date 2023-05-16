from time import time

from slack_sdk.signature import SignatureVerifier

from slack_bolt.middleware import RequestVerification
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


def next():
    return BoltResponse(status=200, body="next")


class TestRequestVerification:
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

    def test_valid(self):
        middleware = RequestVerification(signing_secret=self.signing_secret)
        timestamp = str(int(time()))
        raw_body = "payload={}"
        req = BoltRequest(body=raw_body, headers=self.build_headers(timestamp, raw_body))
        resp = BoltResponse(status=404, body="default")
        resp = middleware.process(req=req, resp=resp, next=next)
        assert resp.status == 200
        assert resp.body == "next"

    def test_invalid(self):
        middleware = RequestVerification(signing_secret=self.signing_secret)
        req = BoltRequest(body="payload={}", headers={})
        resp = BoltResponse(status=404)
        resp = middleware.process(req=req, resp=resp, next=next)
        assert resp.status == 401
        assert resp.body == """{"error": "invalid request"}"""
