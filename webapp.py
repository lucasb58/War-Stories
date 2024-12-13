from flask import Flask, url_for, render_template, request 
from markupsafe import Markup

import os
import json

app = Flask(__name__) #__name__ = "__main__" if this is the file that was run.  Otherwise, it is the name of the file (ex. webapp)

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


if __name__=="__main__":
    app.run(debug=True)
