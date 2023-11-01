import hashlib
from google.cloud import storage
from io import BytesIO
from flask import Flask, send_file
from google.cloud.exceptions import NotFound
import re
from bs4 import BeautifulSoup
import math
import json


class Backend:

    def __init__(self):
        self.global_hashmap = {}
        self.junk_words = set(["and","or",'but', "an", "the", "of",
        "in", "to", "is", "are", "was", "were"])
        self.search_keyword = ""            
        
    def get_wiki_page(self, file_name, storage_client = storage.Client()):
        """Retrieves the contents of a wiki page stored in a Google Cloud Storage bucket.

        Args:
            file_name (str): The name of the file containing the wiki page content.
            storage_client (google.cloud.storage.client.Client): A client for accessing the Google Cloud Storage service. Defaults to storage.Client().
        
        Returns:
            str: The contents of the specified wiki page.
        """ 
        # Create a client to access the Google Cloud Storage service.
        bucket_wikiPage = storage_client.bucket("ama_wiki_content")

        # Get the blob corresponding to the specified file name.
        blob = bucket_wikiPage.blob(file_name)

        # Open the blob as a file and read its contents.
        with blob.open('r') as f:
            return f.read()

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
    
    def search(self, file, page_name):
        """
        Search method to index a file and add relevant words to a global hashmap with their associated page names and snippets.

        Args:
            file (str): The string to search for words.
            page_name (str): The name of the page to which the file belongs.

        Returns:
            None

        """
        text_list = re.split("\\W+", file)  # split string object exclusively on words into a list.

        # Extract the page title from the page name.
        page_title = page_name[6:-9]

        # Split the page title into a list of words.
        page_to_content = page_title.split()        

        # Add the page title words to the file text list.
        text_list.extend(page_to_content)

        # Remove any duplicate words in the list.
        text_list = set(text_list)        

        # Truncate the file text to 150 characters, if necessary.
        if len(file) > 150:
            snippet = file[:151]
        else:
            snippet = file

        # Iterate through the list of words in the file text.
        for word in text_list:
            # Check if the word is not a junk word.
            if word.lower() not in self.junk_words:
                # Check if the word is already in the global hashmap.
                if word.lower() in self.global_hashmap:
                    # Append the page name and snippet to the existing list of values for the word.
                    self.global_hashmap[word.lower()].append([page_name, snippet])
                else:
                    # Add a new key-value pair to the global hashmap for the word.
                    self.global_hashmap[word.lower()] = [[page_name, snippet]]

        return 
    
    def search_results(self, keyword):
        """
        Search method to retrieve search results for a given keyword from the global hashmap.

        Args:
            keyword (str): The keyword to search for.

        Returns:
            A list of lists containing the page names and snippets associated with the keyword, or an empty list if the keyword is not found.

        """
        # Check if the keyword exists in the global hashmap.
        if keyword.lower() in self.global_hashmap:
            return self.global_hashmap[keyword.lower()] 

        # Return an empty list if the keyword is not found.
        return [[]]
    

    def word_processing(self,query):
        """
        Word processing method to clean and normalize a query string.

        Args:
            query (str): The query string to process.

        Returns:
            A cleaned and normalized version of the query string.

        """
        # Remove leading/trailing white spaces
        query = query.strip()
        
        # Remove all types of white spaces
        query = re.sub(r'\s+', '', query)
        
        # Remove non-alphanumeric characters except space
        query = re.sub(r'[^\w\s]', '', query)
        return query


    def scan_contents(self,contents,pages_lst=None):
        """Scans contents for references to wiki pages and returns a formatted string.

        Args:
            contents: A string containing the text to scan for wiki page references.
            pages_lst: An optional list of strings representing the names of wiki pages
                to use for the scan. Defaults to None.

        Returns:
            A string containing the original contents with any wiki page references
            formatted as hyperlinks.
        """
        pages_list= pages_lst or self.get_all_page_names('ama_wiki_content','pages/')
        max_length = -math.inf # Length of the longest wiki page title
        pages_set = set() # Set of strings with the list of pages in the string

        for i in range(len(pages_list)):
            temp = pages_list[i][6:-9] # Removes the prefix 'pages/' and '/contents' from every page name
            if len(temp) > max_length:
                max_length = len(temp)
            pages_set.add(temp)

        used_pages = set() # Saves the pages that have already been used in the
        split_contents = contents.split() # Splits every string / page title into a list
        result = ''       
        i = 0

        # Goes through the list of all words
        while i < len(split_contents):
            longest_valid_title = ''
            temp = ''
            skip_count = 0
            j = i

            # Finds the longest title, from the starting word in the first while loop, all the way to the right until the string does not match a page title
            while (j < len(split_contents)) and (len(temp) <= max_length):
                if temp == '':
                    temp += split_contents[j]
                else:
                    temp += ' ' + split_contents[j] 

                # Removes the dot from the end of the string because page titles usually do not have dots
                dot_at_the_end = False # Helps remember if there was a dot to add it later  
                if temp[-1] == '.':
                    temp = temp[:-1]      
                    dot_at_the_end = True  

                # Checks if the new string is a page title and not already a linked page.
                if (temp in pages_set) and (temp not in used_pages) and (len(temp) > len(longest_valid_title)):
                    longest_valid_title = temp
                    if dot_at_the_end: # Adds the "." back, Why? To remember later there is a dot and include it in the final string
                        longest_valid_title += '.'
                    skip_count = j-i
                j += 1

            # If the starting word did not build a title, just add the word as normal
            if longest_valid_title == '':
                # If starting word in contents. dont add space
                if result == '':
                    result += split_contents[i]
                else:
                    result += ' ' + split_contents[i]
            else:
                # Another dot check
                dot_at_the_end_part_2 = False # Helps remember again if the word had a dot before removing it
                if longest_valid_title[-1] == '.': # Removes the dot
                    longest_valid_title = longest_valid_title[:-1]
                    dot_at_the_end_part_2 = True

                used_pages.add(longest_valid_title) # Adds the built string that matched the page into the set, to no longer be used
                longest_valid_title = f'<a href=\"/page_results?current_page=pages/{longest_valid_title}/contents\">{longest_valid_title}</a>' # Creates a hyperlink of the linked page

                # Adds the dot after the hyperlink if there was a dot
                if dot_at_the_end_part_2:
                    longest_valid_title += '.'
                # If starting word in the contents, dont add space
                if result == '':
                    result += longest_valid_title
                else:
                    result += ' ' + longest_valid_title
            i += skip_count + 1
        return result

    def upload(self, bucket_name, file, file_name, file_type, username, storage_client=storage.Client(), soup=BeautifulSoup, scan=None, add_page=None, upload_attributes=None):
        """ Uploads a file to the bucket.

        The contents of the incoming file are cleaned up of any unwanted html blocks, then another function in the backend class is called
        to create hyperlinks for related pages in the wiki. Finally the formatted content is uploaded into the bucket.

        Args:
            file: The file object to upload.
            file_name: The name to give the uploaded file.
            file_type: The content type of the uploaded file.
            storage_client: used to accept mock storage client, default is normal storage client
            soup: used to accept mock soup, default uses BeautifulSoup()
            mock_format: used to replace self.format() to remove dependecy
        """
        # Checks if any mock objects were injected
        if scan is None:
            scan = self.scan_contents
        if add_page is None:
            add_page = self.add_page_to_user_data
        if upload_attributes is None:
            upload_attributes = self.create_page_attributes
            
        # Read the contents fo the file into a byte string
        file_contents = file.read()

        # Sanitze any HTML tags in the file contents
        clean_content = soup(file_contents,'html.parser',from_encoding='utf-8').get_text()

        # Calls scan_contents() by default to identify all possible page links
        formatted_content = scan(clean_content)

        # TODO: Pass the image url of the image linked to the page, change the 3rd parameter
        upload_attributes(file_name,username,'image_url')

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f'pages/{file_name}/contents')
        blob.upload_from_string(formatted_content, content_type=file_type)
        add_page(username,file_name)
        return formatted_content

    def add_page_to_user_data(self,username,file_name,storage_client=storage.Client(),json_module=json):
        ''' Updates user list of pages authored after uploading a page

        Processes the user json file to a python dictionary, adds the new uploaded page file name to the list.
        Processes the dictionary back to json and uploads.

        Args:
            username: used to update the right user file
            file_name: used to add the file name to the user list of pages authored
            storage_client: used to inject mock storage, uses google storage by default
            json_module: used to inject mock json, uses normal json by default
        '''
        bucket = storage_client.bucket('ama_users_passwords')
        blob = bucket.blob(username)
        user_data = {}
        with blob.open('r') as b:
            user_data = json_module.loads(b.read())
        user_data['pages_uploaded'].append('pages/'+file_name)
        json_data = json_module.dumps(user_data)
        blob.upload_from_string(json_data,content_type="application/json")

    def get_pages_authored(self,username,storage_client=storage.Client(),json_module=json):
        '''Gets the list of pages authored by the user
        
        Converts user data from json to python dictionary and returns key pages_uploaded that contains a list of pages authored

        Args:
            username: used to get the data from the user
            storage_client: used to inject mock storage, uses google storage by default
            json_module: used to inject mock json, uses normal json by default
        '''
        bucket = storage_client.bucket('ama_users_passwords')
        blob = bucket.blob(username)
        user_data = {}
        with blob.open('r') as b:
            user_data = json_module.loads(b.read())
        return user_data['pages_uploaded']

    def sign_up(self, username, password, storage_client=storage.Client(), json_module=json):
        #Creating a list of blobs (all_blobs) which holds a file for each username.
        bucket = storage_client.bucket("ama_users_passwords")

        #setting cap for username length
        if len(username) > 32:
            return False

        #Opening list of blobs to read filenames to see if a file matches the username that was just inputted
        blob = bucket.blob(username)
        if blob.exists():
            return False

        else:
            #hashing password and adding it to the username file that correlates with it
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            user_data = {
                "key" : hashed_password,
                "pages_uploaded" : [] 
                }

            json_data = json_module.dumps(user_data)
            blob.upload_from_string(json_data,content_type="application/json")
            return True

    def get_user_key(self, username, storage_client=storage.Client(), json_module=json):
        bucket = storage_client.bucket('ama_users_passwords')
        blob = bucket.blob(username)
        if blob.exists():
            map = {}
            with blob.open('r') as b:
                map = json_module.loads(b.read())
            return map['key']
        else:
            return None

    def sign_in(self,
                username,
                password,
                storage_client=storage.Client(),
                hash=hashlib.sha256,
                get_key=None):
        '''Returns a boolean if the user is found and the password matches.

        Searches the ama_users_passwords bucket for a match with the parameters received.

        Args:
            username: used to search a specific blob in the ama_users_passwords bucket
            password: used to compare to the value inside the username blob
            storage_client: used to receive a mock storage client, default is normal storage client
        '''
        if get_key is None:
            get_key = self.get_user_key
        bucket = storage_client.bucket("ama_users_passwords")
        blob = bucket.blob(username)
        if blob.exists():
            hashed_password = hash(password.encode()).hexdigest()
            key = get_key(username)
            if key == hashed_password:
                return True
            else:
                return False
        else:
            return False

    def get_image(self,
                  file_name,
                  storage_client=storage.Client(),
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
        else:
            return None

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
