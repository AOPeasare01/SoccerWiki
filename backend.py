from google.cloud import storage
from flask import Flask
from google.cloud.exceptions import NotFound
import re

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
