
import time
from unittest.mock import MagicMock

import redis

from Backend.cache import RequestCache


def test_fingerprint_ignores_case_and_extra_whitespace():
    first = RequestCache.fingerprint(
        "Flood water entered houses",
        "Demo Location",
    )
    second = RequestCache.fingerprint(
        "  FLOOD   WATER ENTERED HOUSES  ",
        " demo location ",
    )

    assert first == second


def test_first_claim_succeeds_and_second_is_duplicate():
    cache = RequestCache("redis://localhost:6379/0")
    text = "Automated cache duplicate test"
    location = "Automated Test Location"

    try:
        cache.forget_request(text, location)

        assert cache.claim_request(text, location) is True
        assert cache.claim_request(text, location) is False
    finally:
        cache.forget_request(text, location)
        cache.close()


def test_request_can_be_claimed_after_expiration():
    cache = RequestCache("redis://localhost:6379/0")
    text = "Automated cache expiration test"
    location = "Automated Test Location"

    try:
        cache.forget_request(text, location)

        assert cache.claim_request(text, location) is True

        key = (
            "floodsense:request:"
            + cache.fingerprint(text, location)
        )
        cache.client.expire(key, 1)
        time.sleep(2)

        assert cache.claim_request(text, location) is True
    finally:
        cache.forget_request(text, location)
        cache.close()


def test_redis_failure_allows_processing(monkeypatch):
    cache = RequestCache("redis://localhost:6399/0")

    def raise_redis_error(*args, **kwargs):
        raise redis.ConnectionError("Simulated Redis failure")

    monkeypatch.setattr(
        cache.client,
        "exists",
        raise_redis_error,
    )
    monkeypatch.setattr(
        cache.client,
        "set",
        raise_redis_error,
    )

    try:
        assert cache.is_duplicate("Failure test", "Test Location") is False
        assert cache.claim_request("Failure test", "Test Location") is True
    finally:
        cache.close()