import pytest
from unittest.mock import patch, MagicMock
from scraper import get_airport_info, normalize_airport_name, parse_coordinates


def test_normalize_airport_name():
    assert normalize_airport_name("Leonardo Da Vinci (Fiumicino)") == "Leonardo Da Vinci Fiumicino"
    assert normalize_airport_name("John F Kennedy  International") == "John F Kennedy International"


def test_parse_coordinates_decimal():
    lat, lon = parse_coordinates("41.8003; 12.2389")
    assert abs(lat - 41.8003) < 0.001
    assert abs(lon - 12.2389) < 0.001


def test_parse_coordinates_dms():
    lat, lon = parse_coordinates("41°48′01″N 12°14′20″E")
    assert abs(lat - 41.800) < 0.01
    assert abs(lon - 12.238) < 0.01


def test_parse_coordinates_invalid():
    lat, lon = parse_coordinates("no coordinates here")
    assert lat is None
    assert lon is None


def test_get_airport_info_cache_hit():
    with patch("scraper.get_cached", return_value={"country": "Italy", "timezone": "Europe/Rome"}):
        info = get_airport_info("Leonardo Da Vinci (Fiumicino)")
        assert info["country"] == "Italy"
        assert info["timezone"] == "Europe/Rome"


def test_get_airport_info_missing():
    with patch("scraper.get_cached", return_value=None), \
         patch("scraper.search_wikipedia", return_value={}), \
         patch("scraper.requests.get", return_value=MagicMock(text="<html></html>")):
        info = get_airport_info("Nonexistent Airport")
        assert info == {}