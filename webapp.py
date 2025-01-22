import pymongo
from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth
from bson.objectid import ObjectId
import pprint
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.run(debug = False)


app.secret_key = os.environ['SECRET_KEY']
oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'],
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize'
)

connection_string = os.environ["MONGO_CONNECTION_STRING"]
db_name = os.environ["MONGO_DBNAME"]

client = pymongo.MongoClient(connection_string)
db = client[db_name]
collection = db['Posts']

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.context_processor
def inject_logged_in():
    return {"logged_in": 'github_token' in session}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    posts = list(collection.find())
    return render_template('home.html', posts=posts)

@app.route('/savepost', methods=['GET','POST'])
def savepost():
    if 'user_data' in session:
        if "savepost" in request.form:
            holder = session['user_data']['login']
            result = collection.update_one(
                {"_id": ObjectId(request.form["post.id"])},
                {"$push": {"savedby": holder}}
            )
        savedposts = [doc for doc in collection.find() if session['user_data']['login'] in doc.get('savedby', [])]
        return render_template('savepost.html', savedposts=savedposts)
    return render_template('savepost.html')

@app.route('/unsavepost', methods=['GET', 'POST'])
def unsavepost():
    if 'user_data' in session:
        if "unsavepost" in request.form:
            holder = session['user_data']['login']
            result = collection.update_one(
                {"_id": ObjectId(request.form["post.id"])},
                {"$pull": {"savedby": holder}}
            )
        savedposts = [doc for doc in collection.find() if session['user_data']['login'] in doc.get('savedby', [])]
        return render_template('savepost.html', savedposts=savedposts)
    return render_template('savepost.html')

@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='http'))

@app.route('/logout')
def logout():
    session.clear()
    return render_template('message.html', message='You were logged out')

@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
    else:
        try:
            session['github_token'] = (resp['access_token'], '')
            session['user_data'] = github.get('user').data
            message = 'You were successfully logged in as ' + session['user_data']['login'] + '.'
        except Exception as inst:
            print(inst)
            message = 'Unable to login, please try again.'
    return render_template('message.html', message=message)

@app.route('/post', methods=['GET','POST'])
def renderPost():
    if 'user_data' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        writing = request.form.get('writing')
        author = session['user_data']['login']
        
        doc = {"Author": author, 'Text': writing, "savedby": [], "Comments": []}
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                doc['ImagePath'] = 'uploads/' + filename

        collection.insert_one(doc)
        return redirect(url_for('home'))

    return render_template('post.html')

@app.route('/logintopost')
def renderLogintopost():
    return render_template('logintopost.html')

@app.route('/googleb4c3aeedcc2dd103.html')
def render_google_verification():
    return render_template('googleb4c3aeedcc2dd103.html')

@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')

if __name__ == '__main__':
    app.run()

