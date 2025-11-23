import pytest
from datetime import datetime
from tempfile import TemporaryDirectory
import os
from src.image_metadata import get_image_year_month


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


class TestImageDate:


    def test_with_datetime_original(self, mock_image):
        mock_image({
            36867: "2021:05:17 10:20:30"
        })
        assert get_image_year_month("dummy.jpg") == (2021, 5)

    def test_with_digitized_fallback(self, mock_image):
        mock_image({
            36868: "2020:11:03 08:30:00"
        })
        assert get_image_year_month("dummy.jpg") == (2020, 11)

    def test_with_generic_datetime_fallback(self, mock_image):
        mock_image({
            306: "2019:02:14 12:00:00"
        })
        assert get_image_year_month("dummy.jpg") == (2019, 2)

    def test_fallback_to_file_modification_time(self, mock_image):
        mock_image({
            36867: None,
            36868: None,
            306: None
        })
        # Create a temporary file
        with TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "testfile.jpg")
            with open(file_path, "w") as fw:
                fw.write("dummydata")

            # Set known modification time
            known_dt = datetime(2020, 12, 25, 15, 30)
            ts = known_dt.timestamp()
            os.utime(file_path, (ts, ts))

            # Execute the function
            year, month = get_image_year_month(str(file_path))

            assert (year, month) == (2020, 12)

    def test_missing_exif(self, mock_image):
        mock_image(None)
        with pytest.raises(Exception):
            get_image_year_month("dummy.jpg")