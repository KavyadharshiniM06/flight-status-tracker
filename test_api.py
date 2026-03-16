import pytest
from unittest.mock import patch, MagicMock
from api import get_flight_data

MOCK_FLIGHT = {
    "airline": {"name": "Air India"},
    "flight": {"iata": "AI101"},
    "flight_status": "scheduled",
    "departure": {
        "airport": "Leonardo Da Vinci (Fiumicino)",
        "scheduled": "2026-03-16T10:50:00+00:00",
        "estimated": "2026-03-16T10:50:00+00:00",
        "actual": None,
        "terminal": "3",
        "gate": None
    },
    "arrival": {
        "airport": "John F Kennedy International",
        "scheduled": "2026-03-16T14:55:00+00:00",
        "estimated": None,
        "actual": None,
        "terminal": "4",
        "gate": None
    }
}


def test_get_flight_data_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [MOCK_FLIGHT]}
    mock_response.raise_for_status = MagicMock()

    with patch("api.requests.get", return_value=mock_response):
        result = get_flight_data("fake_key", "AI101")
        assert result["flight"]["iata"] == "AI101"
        assert result["airline"]["name"] == "Air India"


def test_get_flight_data_no_data():
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": []}
    mock_response.raise_for_status = MagicMock()

    with patch("api.requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No data found"):
            get_flight_data("fake_key", "XX999")


def test_get_flight_data_invalid_key():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")

    with patch("api.requests.get", return_value=mock_response):
        with pytest.raises(Exception):
            get_flight_data("bad_key", "AI101")