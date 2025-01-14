import pymongo
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
#from flask_oauthlib.contrib.apps import github #import to make requests to GitHub's OAuth
from flask import render_template
from bson.objectid import ObjectId
import pprint
import os

# This code originally from https://github.com/lepture/flask-oauthlib/blob/master/example/github.py
# Edited by P. Conrad for SPIS 2016 to add getting Client Id and Secret from
# environment variables, so that this will work on Heroku.
# Edited by S. Adams for Designing Software for the Web to add comments and remove flash messaging

app = Flask(__name__)

app.debug = False #Change this to False for production

app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)
oauth.init_app(app) #initialize the app to be able to make requests for user information
#Set up GitHub as OAuth provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)
connection_string = os.environ["MONGO_CONNECTION_STRING"]
db_name = os.environ["MONGO_DBNAME"]

client = pymongo.MongoClient(connection_string)
db = client[db_name]
collection = db['Posts'] #1. put the name of your collection in the quotes

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


#context processors run before templates are rendered and add variable(s) to the template's context
#context processors must return a dictionary 
#this context processor adds the variable logged_in to the conext for all templates
@app.context_processor
def inject_logged_in():
    is_logged_in = 'github_token' in session #this will be true if the token is in the session and false otherwise
    return {"logged_in":is_logged_in}

@app.route('/')
def home():
    posts=[]
    for doc in collection.find():
        posts.append(doc)
    addComments=[]
    for doc in collection.find():
    	addComments.append(doc)
    return render_template('home.html', posts=posts, addComments=addComments)

#redirect to GitHub's OAuth page and confirm callback URL
@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='http')) #callback URL must match the pre-configured callback URL

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #Remove once done running locally

@app.route('/logout')
def logout():
    session.clear()
    return render_template('message.html', message='You were logged out')

@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        #session.clear()
        message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
    else:
        try:
            session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
            session['user_data']=github.get('user').data
            #pprint.pprint(vars(github['/email']))
            #pprint.pprint(vars(github['api/2/accounts/profile/']))
            print(session)
            message='You were successfully logged in as ' + session['user_data']['login'] + '.'
            print("logged in")
        except Exception as inst:
            #session.clear()
            print(inst)
            message='Unable to login, please try again.  '
    return render_template('message.html', message=message)


@app.route('/post', methods=['GET','POST'])
def renderPost():
	if 'user_data' in session:
		user_data_pprint = pprint.pformat(session['user_data'])#format the user data nicely
	else:
		user_data_pprint = '';
	if "writing" in request.form:
		session["writing"]=request.form['writing']
		author=session['user_data']['login']
		doc = {"Author":author,'Text':request.form['writing']}
		collection.insert_one(doc)
		return redirect(url_for('home'))
	return render_template('post.html', dump_user_data=user_data_pprint)
	
@app.route('/logintopost')
def renderLogintopost():
    if 'user_data' in session:
        user_data_pprint = pprint.pformat(session['user_data'])#format the user data nicely
    else:
          user_data_pprint = '';
    return render_template('logintopost.html', dump_user_data=user_data_pprint)
    
@app.route('/addcomments', methods=['GET','POST'])
def addComments():
	if 'user_data' in session:
		user_data_pprint = pprint.pformat(session['user_data'])#format the user data nicely
	else:
		user_data_pprint = '';
	parent_filter = {'_id': request.form['post.id']}
	if "comments" in request.form:
		author=session['user_data']['login']
		new_sub_document = { "Author": author,'Comments': request.form['comments']}
		print(request.form['comments'])
		#collection.append( parent_filter, {'$push': {'Comments': new_sub_document}})
		#print(ObjectID(request.form["post.id"]))
		#for doc in collection.find({"_id": ObjectId(request.form["post.id"])}):
			#doc["Comments"].append(new_sub_document)
		result = collection.update_one(
    		{"_id": ObjectId(request.form["post.id"])},
    		{"$push": {"Comments": new_sub_document}}
		)
		return redirect(url_for('home'))
	return redirect(url_for('home'))
	
    
    
"""def addLikes():
	if 'user_data' in session:
		user_data_pprint = pprint.pformat(session['user_data'])#format the user data nicely
	else:
		user_data_pprint = '';
	if "likes" in request.form: 
		session["likes"]=request.form["likes"] + 1
		doc = {"likes":Like}
		collection.insert_one(doc)
	return likes"""
    

@app.route('/googleb4c3aeedcc2dd103.html')
def render_google_verification():
    return render_template('googleb4c3aeedcc2dd103.html')

#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session['github_token']

if __name__ == '__main__':
    app.run()
