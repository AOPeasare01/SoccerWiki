import random, string
from flask import Flask, render_template

app = Flask(  # Create a flask app
  __name__,
  template_folder='templates',  # Name of html file folder
  static_folder='static'  # Name of directory for static files
)

# ok_chars = string.ascii_letters + string.digits


# @app.route('/')  # What happens when the user visits the site
# def base_page():
# 	random_num = random.randint(1, 100000)  # Sets the random number
# 	return render_template(
# 		'base.html',  # Template file path, starting from the templates folder. 
# 		random_number=random_num  # Sets the variable random_number in the template
# 	)


# @app.route('/2')
# def page_2():
# 	rand_ammnt = random.randint(10, 100)
# 	random_str = ''.join(random.choice(ok_chars) for a in range(rand_ammnt))
# 	return render_template('site_2.html', random_str=random_str)


# if __name__ == "__main__":  # Makes sure this is the main process
# 	app.run( # Starts the site
# 		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
# 		port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
# 	)
    
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')
    
@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route("/pages")
def pages():
  return render_template('pages.html')

@app.route("/login")
def login():
  return render_template('login.html')

@app.route("/signup")
def signup():
  return render_template('signup.html')

if __name__ == "__main__":  # Makes sure this is the main process
	app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
	)

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
