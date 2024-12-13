from flask import Flask, url_for, render_template, request 
from markupsafe import Markup
import pymongo
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
#from flask_oauthlib.contrib.apps import github #import to make requests to GitHub's OAuth

import pprint
import os

import os
import json

app = Flask(__name__) #__name__ = "__main__" if this is the file that was run.  Otherwise, it is the name of the file (ex. webapp)

app.debug = True #Change this to False for production

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

#render home page
@app.route("/")
def render_main():
    return render_template('home.html')

#render page 0    
@app.route("/graphmath")
def render_main_graph_math():
    states = get_state_options()
    state = ""
    if 'state' in request.args:
        state = request.args['state']
    else: 
        state = 'AL'
    mathscore = get_math_scores(state)
    print(state)
    place = "Verbal Scores in " + state + ", from 2005 to 2015."
    return render_template('graphmath.html', graph_math_points = mathscore,  state_options=states, title=place)

#render page 1
@app.route("/graphverbal")
def render_main_graph_verbal():
    states = get_state_options()
    state = ""
    if 'state' in request.args:
        state = request.args['state']
    else: 
        state = 'AL'
    verbalscore = get_verbal_scores(state)
    print(state)
    place = "Verbal Scores in " + state + ", from 2005 to 2015."
    return render_template('graphverbal.html', graph_verbal_points = verbalscore, state_options=states, title=place)

# render page 2
@app.route("/mathscorebystate")
def render_main_mathscorebystates():
    states = get_state_options()
    state = ""
    if 'state' in request.args:
        state = request.args['state']
    else: 
        state = 'AL'
    print(state)    
    averagescore = get_avg_math_score(state)
    line = "The average math score in " + state + " is " + str(averagescore) + " from 2005 to 2015."
    return render_template('mathscorebystate.html', title=line, state_options=states)

#render page 3
@app.route("/verbalscorebystate")
def render_main_verbalscorebystates():
    states = get_state_options()
    state = ""
    if 'state' in request.args:
        state = request.args['state']
    else: 
        state = 'AL'
    print(state)    
    averagescore = get_avg_verbal_score(state)
    line = "The average math score in " + state + " is " + str(averagescore) + " from 2005 to 2015."
    return render_template('verbalscorebystate.html', title=line, state_options=states)         
 
#select state 
def get_state_options():
    with open('school_scores.json') as scores_data:
        state = json.load(scores_data)
    states=[]
    for c in state:
        if c["State"]["Code"] not in states:
            states.append(c["State"]["Code"])
    print(states)        
    options=""
    for s in states:
        options += Markup("<option value=\"" + s + "\">" + s + "</option>") #Use Markup so <, >, " are not escaped lt, gt, etc.
    return options

#x and y values for math scores 
def get_math_scores(state):
    with open('school_scores.json') as scores_data:
        sat_scores = json.load(scores_data)
    mathscore={}
    for m in sat_scores:      
        if m['State']['Code']== state:
            mathscore[str(m['Year'])] = m['Total']['Math']
    print(mathscore)
    graph_math_points= ""
    for key, value in mathscore.items():
        graph_math_points= graph_math_points + Markup('{ x: ' + str(key) + ', y: ' + str(value) + ' },')        
    return graph_math_points 

#x and y values for verbal scores     
def get_verbal_scores(state):
    with open('school_scores.json') as scores_data:
        sat_scores = json.load(scores_data)
    verbalscore={}
    for v in sat_scores:      
        if v['State']['Code']== state:
            verbalscore[v['Year']] = v['Total']['Verbal']
    print(verbalscore)   
    graph_verbal_points= ""
    for key, value in verbalscore.items():
        graph_verbal_points = graph_verbal_points + Markup('{ x: ' + str(key) + ', y: ' + str(value) + ' },')
    return graph_verbal_points

# avg math score by state 
def get_avg_math_score(state):
    with open('school_scores.json') as scores_data:
        sat_scores = json.load(scores_data)
    mathavgscore = 0
    num = 0
    for m in sat_scores:      
        if m['State']['Code']== state:
            mathavgscore = mathavgscore + m['Total']['Math']
            num = num + 1
    mathavgscore = round(mathavgscore/num)    
    print(mathavgscore)
    return mathavgscore

# avg verbal score by state
def get_avg_verbal_score(state):
    with open('school_scores.json') as scores_data:
        sat_scores = json.load(scores_data)
    verbalavgscore = 0
    num = 0
    for m in sat_scores:      
        if m['State']['Code']== state:
            verbalavgscore = verbalavgscore + m['Total']['Verbal']
            num = num + 1
    verbalavgscore = round(verbalavgscore/num)    
    print(verbalavgscore)
    return verbalavgscore           

@app.route('/googleb4c3aeedcc2dd103.html')
def render_google_verification():
    return render_template('googleb4c3aeedcc2dd103.html')

#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session['github_token']

if __name__=="__main__":
    app.run(debug=True)
