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

  @patch("google.cloud.storage.Client")
def test_create_page_attributes(mock_storage):
    ''' Tests if create_page_attributes() successfully uploads a json file as a blob

    Tests if a blob is successfully uploaded by asserting if the methods are called with the expected parameters.
    Removes google storage module and json dependencies.
    '''
    # Creates magic mocks
    my_bucket = MagicMock()
    my_blob = MagicMock()
    mock_json = MagicMock()

    # Sets return values for certain function calls
    mock_storage.bucket.return_value = my_bucket
    my_bucket.blob.return_value = my_blob
    mock_json.dumps.return_value = "-author:alan,image_path:someimage.png-"

    backend = Backend()

    expected = "-author:alan,image_path:someimage.png-"

    # Asserts if methods were called with specific values
    backend.create_page_attributes('my_file','alan','someimage.png',mock_storage,mock_json)
    mock_storage.bucket.assert_called_with('ama_wiki_content')
    my_bucket.blob.assert_called_with('pages/my_file/attributes')
    my_blob.upload_from_string.assert_called_with(expected,content_type='application/json')

@patch("google.cloud.storage.Client")
def test_get_page_attributes_success(mock_storage):
    ''' Tests get_page_attributes()

    Expects a successful retrieval of the json attributes file, converting json to a python dictionary and returning it.
    Removing google storage and json dependencies.
    '''
    # Creates magic mocks
    my_bucket = MagicMock()
    my_blob = MagicMock()
    mock_json = MagicMock()

    backend = Backend()

    expected = {'author':'alan'} # Expected dictionary to be returned

    # Modify return values of mock operations
    mock_storage.bucket.return_value = my_bucket
    my_bucket.blob.return_value = my_blob
    my_blob.open = mock_open(read_data="This does not matter")
    my_blob.exists.return_value = True
    mock_json.loads.return_value = expected
    
    assert expected == backend.get_page_attributes('my_file',mock_storage,mock_json)
    mock_storage.bucket.assert_called_with('ama_wiki_content')
    my_bucket.blob.assert_called_with('pages/my_file/attributes')

@patch("google.cloud.storage.Client")
def test_get_page_attributes_fail(mock_storage):
    ''' Tests get_page_attributes()

    Expects an unsuccessful retrieval of the json attributes file, returning None, because attributes does not exist.
    Removing google storage and json dependencies.
    '''
    # Creates magic mocks
    my_bucket = MagicMock()
    my_blob = MagicMock()

    backend = Backend()

    # Modify return values of mock operations
    mock_storage.bucket.return_value = my_bucket
    my_bucket.blob.return_value = my_blob
    my_blob.exists.return_value = False
    
    assert None == backend.get_page_attributes('my_file',mock_storage)
    mock_storage.bucket.assert_called_with('ama_wiki_content')
    my_bucket.blob.assert_called_with('pages/my_file/attributes')

@patch("google.cloud.storage.Client")
def test_get_image_succeeds(mock_storage):
    ''' Tests get_image() and expects a successful retrival

    Tests get_image() and expects a successful retrival.
    Removes dependencies: storage client, bucket, blob, and bytesio

    '''

    class MockBytes:
        '''Mocks the class of BytesIO

        Mocks the class of BytesIO with similar needed methods.

        Attributes:
            data: saves data when initializing the object
        '''

        def __init__(self, data):
            self.data = data

        def read(self):
            '''
            Returns the attribute data in the class
            '''
            return self.data

    # Creates Magic Mocks
    my_client = MagicMock()
    my_bucket = MagicMock()
    my_blob = MagicMock()

    backend = Backend()

    # Establishes return values for mock operations
    mock_storage = my_client
    my_client.bucket.return_value = my_bucket
    my_bucket.blob.return_value = my_blob
    my_blob.exists.return_value = True  # Makes the function believe that the blob exists

    # Creates a mock image with binary data
    my_image_data = b"This is an image"

    # Sets blob open value of read to mock image
    my_blob.open = mock_open(read_data=my_image_data)

    # Returns a bytesio object, in this case, the mock bytes io object.
    results = backend.get_image('my_image_name', mock_storage, MockBytes)

    # Calls the method read() inside the mock bytesio object returned from get_image()
    assert results.read() == my_image_data


@patch("google.cloud.storage.Client")
def test_get_image_fail(mock_storage):
    ''' Tests get_image() and expects a unsuccessful retrival

    Tests get_image() and expects a successful retrival.
    Removes dependencies: storage client, bucket, blob, and bytesio

    '''

    class MockBytes:
        '''Mocks the class of BytesIO with similar needed methods.

        Attributes:
            data: saves data when initializing the object
        '''

        def __init__(self, data):
            self.data = data

        def read(self):
            # Returns the attribute data in the class
            return self.data

    # Creates Magic Mocks
    my_client = MagicMock()
    my_bucket = MagicMock()
    my_blob = MagicMock()

    backend = Backend()

    # Establishes return values for mock operations
    mock_storage = my_client
    my_client.bucket.return_value = my_bucket
    my_bucket.blob.return_value = my_blob
    my_blob.exists.return_value = False  # Makes the function believe that the blob does not exist

    # Creates a mock image with binary data
    my_image_data = b"This is an image"

    # Sets blob open value of read to mock image
    my_blob.open = mock_open(read_data=my_image_data)

    # Returns a bytesio object, in this case, the mock bytes io object.
    results = backend.get_image('my_image_name', mock_storage, MockBytes)

    # Since the blob does not exist, it returns None
    assert results == None


