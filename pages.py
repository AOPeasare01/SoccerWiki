from flask import render_template, send_file, request, redirect, url_for, jsonify
from flaskr import backend
from flask_login import logout_user, current_user
import json
from google.cloud import storage


def make_endpoints(app, backend):
    pages_to_search =backend.get_all_page_names("ama_wiki_content", "pages/")
    for page in pages_to_search:
        file = backend.get_wiki_page(page)
        backend.search(file, page)
    
    data_fetcher = backend.get_soccer_news()
    
    @app.route("/")
    def home():
        # Fetch the soccer news data
        news_data = data_fetcher
        print("Hello")
        print("Hello")
        print("Hello")
        print(news_data)
        # Check if there was an error fetching the data
        # if "error" in news_data:
        #     # Handle the error appropriately - maybe display a default message or a custom error page
        #     news_data = {"error": "Unable to fetch news at this time."}
        
        # Pass the fetched data to your template
        return render_template('home.html', news_data=news_data)


    @app.route("/about")
    def about():
        return render_template('about.html',open_img=False)
        
    @app.route("/open_image/<url>")
    def open_image(url):
        return render_template('about.html',open_img=True,image_url=url)

    @app.route('/upload')
    def upload():
        return render_template('upload.html')
    
    @app.route('/api/pages/<pagename>/react', methods=['POST'])
    def update_likes_dislikes(pagename):
        # Assuming 'backend' is defined and accessible here
        # and it has a method 'update_likes_dislikes' that not only updates the counts
        # but also returns the updated counts as a dictionary
        
        # Extract the 'like' field from the JSON request body
        data = request.json
        like = data.get('like', True)  # Default to True if 'like' not specified

        # Call your backend function with extracted pagename and like/dislike
        # Note: Ensure your backend method accepts pagename correctly and
        # returns the updated counts. You might need to adjust it based on your implementation.
        updated_counts = backend.update_likes_dislikes(pagename, like=like, storage_client=storage.Client(), json_module=json)
        
        # Return the updated counts as JSON
        return jsonify(updated_counts)

    @app.route('/api/pages/<pagename>/counts', methods=['GET'])
    def get_counts(pagename):
        # Assuming a function exists to fetch counts from your storage
        counts = backend.get_counts(pagename)
        return jsonify(counts)

    @app.route("/pages")
    def pages():
        pages = backend.get_all_page_names("ama_wiki_content", "pages/")
        return render_template('pages.html', pagenames=pages)

    @app.route("/page_results")
    def page_results():
        current_page = request.args.get('current_page')
        attributes = backend.get_page_attributes(current_page[6:-9])
        contents = backend.get_wiki_page(current_page)
        return render_template('page_results.html',
                        pagename=current_page[6:-9],
                        contents=contents,
                        author=attributes['author']) 

    @app.route("/search", methods=['GET', 'POST'])
    def search():
        """
        Flask route to handle search requests.

        Args:
        None

        Returns:
        A redirect or a rendered template, depending on the request method and query parameters.

        """
        # Handle POST requests containing a search query.
        if request.method == 'POST':
            # Extract the search query from the request form.
            keyword = request.form['query']
            # Store the search query in the backend.
            backend.search_keyword = keyword
            # Redirect to the search page.
            return redirect(url_for('search'))

        # Handle GET requests for the search page.
        else:
            # Extract the search query from the backend.
            keyword = backend.search_keyword
            
            # Clean and normalize the search query.
            query = backend.word_processing(keyword)
            
            # Search for results if the query length is greater than 2.
            if len(query) > 2:
                results = backend.search_results(query)
                return render_template('search.html', results=results, keyword=keyword)
            
            # Redirect to the pages page if the query is empty.
            elif len(query) == 0:
                return redirect(url_for("pages"))
            
            # Return an empty result set for short queries.
            return render_template('search.html', results=[[]], keyword=keyword)

    @app.route("/my_pages")
    def my_pages():
        pages_authored = backend.get_pages_authored(current_user.id)
        return render_template('pages_authored.html',pagenames=pages_authored)


    @app.route("/logout")
    def logout():
        logout_user()
        return render_template('logout.html')

    @app.route("/images/<file_name>")
    def images(file_name):
        '''Returns a path/element/src for a file using the get_image method
        
        [IMPORTANT] Only png images supported. Lets try to only upload png images to the bucket.
        [SUGGESTION] Use this in the html <img src="images/{{ file }}"/ alt="Could not find: {{ file }}.">

        Args:
            file_name used to pass the value to get image, and used as a reference in route to support different images.
        '''
        return send_file(backend.get_image(file_name), mimetype='image/png')

    @app.route('/upload_wiki', methods=['POST'])
    def handle_upload():
        '''Handles the form block in upload.html

        A route to handle file uploads from upload.html, using POST request. Makes sure there are no empty values.

        [DEPENDENCIES] upload(), get_all_page_names(), and "request".
        
        Variables:
            input_value: Stores the value inside the input block named 'wikiname'. Empty value error handled.
            file: Stores the value in input block named 'file_to_upload'. Empty field (no file uploaded yet) handled.
            pages: Stores the list of pages in the bucket 'ama_wiki_content'

        '''
        input_value = request.form['wikiname']
        file = request.files.get('file_to_upload')
        pages = backend.get_all_page_names('ama_wiki_content', 'pages/')
        if f'pages/{input_value}' in pages:
            # Wiki name already in use
            return render_template('upload.html', status='used')
        elif 'file_to_upload' not in request.files:
            return render_template('upload.html', status='no_file')
        elif input_value.strip() == '':
            # Input is empty
            return render_template('upload.html', status='empty')
        elif file.content_type != 'text/plain':
            # If not .txt
            return render_template('upload.html', status='wrong_file')
        else:
            backend.upload('ama_wiki_content', file, input_value, 'text/plain', current_user.id)
            return render_template('upload.html', status='successful')

