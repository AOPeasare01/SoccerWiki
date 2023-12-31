import re
from io import BytesIO

from flask import Flask
from google.cloud import storage

from google.cloud.exceptions import NotFound


class Backend:
  def __init__(self):
    pass
  def get_all_page_names(self, bucket_name, folder_name,storage_client=storage.Client()):
        """
        Returns a list of all page names in a given GCS bucket and folder.

        Args:
            bucket_name (str): The name of the GCS bucket.
            folder_name (str): The prefix of the folder containing the pages.
            storage_client (google.cloud.storage.client.Client): A GCS client object. Defaults to a new client.

        Returns:
            List[str]: A list of page names in the specified bucket and folder.
        """
        list_page_names = []
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=folder_name)

        for blob in blobs:
            if not blob.name.endswith('/attributes') and blob.name.endswith('/contents'):
                list_page_names.append(blob.name)
        return list_page_names
        
def get_page_attributes(self,file_name,storage_client=storage.Client(),json_module=json):
            bucket = storage_client.bucket('ama_wiki_content')
            blob = bucket.blob(f'pages/{file_name}/attributes')
            if blob.exists():
                map = {}
                with blob.open('r') as b:
                    map = json_module.loads(b.read())
                return map
            else:
                return None

def create_page_attributes(self,file_name,user,image_url,storage_client=storage.Client(),json_module=json):
            page_data = {
                "author" : user,
                "image_path": image_url
                }
            json_data = json_module.dumps(page_data)
            bucket = storage_client.bucket('ama_wiki_content')
            blob = bucket.blob(f'pages/{file_name}/attributes')
            blob.upload_from_string(json_data,content_type="application/json")

def get_image(self,file_name, storage_client=storage.Client(),
  bytes_io=BytesIO):
  '''Returns an image from the ama_wiki_content bucket, in the ama_images folder

Extracts a blob from the ama_wiki_content bucket that can be used as a route for an image to be rendered in html

Args:
file_name: used to complete the path required to find the image blob in the bucket.
storage_client: used to accept mock storage client, default is normal storage client
bytes_io: used to accept mock bytes io class, default is normal BytesIO class
Example class
    class MockBytes:
        def __init__(self,data):
            self.data = data
        def read(self):
            return self.data
'''
  bucket = storage_client.bucket('ama_wiki_content')
  blob = bucket.blob('ama_images/' + file_name)
  
  if blob.exists():
    with blob.open("rb") as f:
       return bytes_io(f.read())

