from unittest import mock
from unittest.mock import MagicMock, mock_open, patch

import pytest

from backend import Backend

@patch("google.cloud.storage.Client")
def test_get_all_page_names(mock_storage):
    class MockBlob:
        def __init__(self,name):
            self.name = name
        def name(self):
            return self.name

    my_bucket = MagicMock()

    backend = Backend()

    # Establishes return values for mock operations
    mock_storage.bucket.return_value = my_bucket
    my_bucket.list_blobs.return_value = [MockBlob('pages/file/contents'),MockBlob('pages/file/attributes'),MockBlob('pages/file2')]

    expected = ['pages/file/contents']
    result = backend.get_all_page_names("bucket","folder",mock_storage)
    mock_storage.bucket.assert_called_with('bucket')
    my_bucket.list_blobs.assert_called_with(prefix='folder')
    assert expected == result

