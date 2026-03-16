import pytest
import time
from unittest.mock import patch
from cache import get_cached, set_cached


def test_cache_miss():
    with patch("cache.load_cache", return_value={}):
        result = get_cached("Some Airport")
        assert result is None


def test_cache_hit():
    fake_cache = {
        "Some Airport": {
            "data": {"country": "Italy"},
            "cached_at": time.time()
        }
    }
    with patch("cache.load_cache", return_value=fake_cache):
        result = get_cached("Some Airport")
        assert result["country"] == "Italy"


def test_cache_expiry():
    fake_cache = {
        "Some Airport": {
            "data": {"country": "Italy"},
            "cached_at": time.time() - (8 * 86400)  # 8 days ago
        }
    }
    with patch("cache.load_cache", return_value=fake_cache):
        result = get_cached("Some Airport")
        assert result is None  # expired
