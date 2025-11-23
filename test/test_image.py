import pytest
from datetime import datetime
from types import SimpleNamespace

from image_metadata import get_image_year_month  # replace with real module name


class FakeImage:
    """Simple fake image object with controllable EXIF."""
    def __init__(self, exif_dict):
        self._exif = exif_dict

    def getexif(self):
        return self._exif

    def _getexif(self):
        return self._exif


@pytest.fixture
def mock_image(monkeypatch):
    def _mock(exif_dict):
        monkeypatch.setattr(
            "PIL.Image.open",
            lambda _: FakeImage(exif_dict)
        )
    return _mock


def test_with_datetime_original(mock_image):
    mock_image({
        36867: "2021:05:17 10:20:30",
        37521: "123"
    })
    assert get_image_year_month("dummy.jpg") == (2021, 5)


def test_with_digitized_fallback(mock_image):
    mock_image({
        36868: "2020:11:03 08:30:00",
        37522: "55"
    })
    assert get_image_year_month("dummy.jpg") == (2020, 11)


def test_with_generic_datetime_fallback(mock_image):
    mock_image({
        306: "2019:02:14 12:00:00",
        37520: "0"
    })
    assert get_image_year_month("dummy.jpg") == (2019, 2)


def test_missing_exif(mock_image):
    mock_image(None)
    with pytest.raises(Exception):
        get_image_year_month("dummy.jpg")


def test_no_valid_datetime(mock_image):
    mock_image({
        36867: None,
        36868: None,
        306: None
    })
    with pytest.raises(Exception):
        get_image_year_month("dummy.jpg")
