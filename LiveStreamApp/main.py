# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 12:32:39 2020

@author:
"""

from flask import Flask, render_template, request, Response, session, redirect, url_for
from main_sql_schema import db, User
from flask_sqlalchemy import SQLAlchemy

import sqlite3
import os

import requests     # to support getting another site

basedir = os.path.abspath(os.path.dirname(__file__))

# check to see if the database exists, and if not, create one

try:
    open("data.sqlite")
    print(" SQlite-> database already exists")
except IOError as e:
    db.create_all()
    user1 = User("LastName1", "FirstName1", "email1@uab.edu", "Password1")
    db.session.add_all([user1])
    db.session.commit()
    print(" SQlite-> Database created successfully")



#db.create_all()
# need application for AWS Beanstalk
application = app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   # changed from TRAC to TRACK
# next line for session
app.config["SECRET_KEY"] = "ourveryveryverysecretkey"

# add this to correct error "sqlalchemy extension was not registered..."
# also imported SQLAlchemy
# see notes at the bottom of the code
sqlalchemy = SQLAlchemy()
sqlalchemy.init_app(app)

# this route builds the initial sign-in page, redirect here if not signed in
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')
# this route builds the initial sign-up page
@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/plans')
def plans():
    return render_template('plans.html')

@app.route('/payment')
def payment():
    
    # =======
    # NOTE: DO we want to ensure the user is signed-in before they enter their payment info?
    # If not, remove the following lines:
    # get the session information we set at sign-in
    if not session.get("email") is None:  # we have a user signed in
        email = session.get("email")
    else:  # user is not signed-in, return to sign-in page
        return redirect(url_for("login"))
    # =======
    
    planid = request.args.get('planid')
    print("plan id :" + planid)
    email =  session.get("email")
    print("email " + email)
    if  ( planid == 'free' ):
        price = "$0"
    else :
        price = "$20"

    try:
        existingUser = User.query.filter(User.email == email)   # was 'email@uab.edu'
        print("user exists: " + existingUser[0].email) 
        # print(existingUser[0])
        existingUser[0].instaKey = planid
        db.session.add(existingUser[0])
        db.session.commit()
        print("user exists: " + existingUser[0].email + "plan id " + existingUser[0].instaKey ) 
        return render_template('payment.html' , planid = planid , price = price)
    except:
        print('Could not update the plan details')
        
# this route takes the info from the sign-in page and completes the sign-in process
@app.route('/signin')
def signin():
    email = request.args.get('email')
    pwd = request.args.get('pwd')
    print(email + " | " + pwd + " is attempting to sign-in")
    userExists = False
    try:
        existingUser = User.query.filter(User.email == email)
        print("user exists: " + existingUser[0].email)
        userExists = True
        #userExists = User.query.filter(User.email == email).first is not None
        #print("======= userExists: " + userExists)
        #existingUser = User.query.filter(User.email == email)
    except:   # user doesn't exist in the database
        print("user doesn't exist")
        warning = "Log-in information is incorrect, try again"
        return render_template('index.html', warning=warning)
    
    if userExists and existingUser[0].pwd == pwd: # user exists and passwords match
        print("user exists and passwords match")
        name = existingUser[0].firstName
        # get link information so we can create the chat page appropriately
        yt_link = existingUser[0].youtubeLink
        twitch_link = existingUser[0].instaLink   # just using an existing column (instaLink) for Twitch
        # set up a session
        session["email"] = existingUser[0].email
        print("session email set")
        print(session)
        # ======= TO DO: Should we send them to the admin page first?
        # return redirect(url_for("admin"), ytlink=yt_link, t_link=twitch_link)
        return render_template('integrated_chat.html', name=name, ytlink=yt_link, t_link=twitch_link)
    else:  # password doesn't match
        print("user exists but passwords don't match")
        warning = "Log-in information is incorrect, try again"
        return render_template('login.html', warning=warning)

# ======= this route takes the information from the sign-in page and creates
#         a user in the database
@app.route('/report')
def report():
    lastName = request.args.get('lastName')
    firstName = request.args.get('firstName')
    email = request.args.get('email')
    pwd1 = request.args.get('pwd1')
    pwd2 = request.args.get('pwd2')
    passwordsMatch = False
    incl_lower = False
    incl_upper = False
    end_num = False
    length = False
    result = ""
    warning = ""
    details = list()
    user = None
    numAttempts = 0
    
    # check to see if the user is already in the database, and if so
    #     send a message
    try:
        existingUser = User.query.filter(User.email == email)
        print("user already exists: " + existingUser[0].email)
        userExists = True
        #userExists = User.query.filter(User.email == email).first is not None
        warning = warning + "This user is already registered!"
        return render_template('signup.html', warning=warning)
    except:   # user doesn't already exist, so we can add them
        print("user doesn't already exist, so we can complete the process to add")
    
    # ======= check the password rules =======
    # first check to ensure the passwords match
    if pwd1 == pwd2:
        passwordsMatch = True
    
    # check first two rules, upper and lower case
    for c in pwd1:
        if c.isupper():
            incl_upper = True
        if c.islower():
            incl_lower = True
        
    # check to ensure last digit is a number
    if pwd1[-1].isdigit():
        end_num = True
            
    # check length is at least 8 characters
    if len(pwd1) >= 8:
        length = True
        

    # ======= create the appropriate feedback =======
    if not incl_lower:
        details.append("Must have a lower case letter")
    if not incl_upper:
        details.append("Must have an upper case letter")
    if not end_num:
        details.append("Must have a number at the end")
    if not length:
        details.append("Must be at least 8 characters")
    if not passwordsMatch:
        details.append("Passwords don't match")
        warning = warning + "The passwords must match!"
    
    if incl_lower and incl_upper and end_num and length and passwordsMatch:
        result = "Your password met all 4 requirements!"
        numAttempts = 0
        
        # add user to the database
        user2 = User(lastName, firstName, email, pwd1)
        print("we got here, with user: " + str(user2))
        db.session.add(user2)
        db.session.commit()
        
        # set the session email so the user is signed-in
        session["email"] = email
        
        return render_template('plans.html')
    
    else:
        result = "Oh No!  It looks like you had issues with your password! "
        numAttempts += 1
        if numAttempts >=3:
            warning = "WARNING: there are 3 consecutive failed attempts"        

        return render_template('signup.html', firstname=firstName, result=result, details=details, warning=warning)
# end report()

# ===== this route creates the initial admin page
@app.route('/admin')
def admin():
    # set up the variables
    warning = ""

    # get the session information we set at sign-in
    if not session.get("email") is None:  # we have a user signed in
        email = session.get("email")
    else:  # user is not signed-in, return to sign-in page
        return redirect(url_for("login"))
    
    # get the current user info from the database to auto-populate the form
    # get the user info
    try:
        existingUser = User.query.filter(User.email == email)
        print("user exists: " + existingUser[0].email)
        # get the links
        yt_link = existingUser[0].youtubeLink
        twitch_link = existingUser[0].instaLink   # just using an existing column (instaLink) for Twitch

    except:   # user doesn't already exist, so we can add them
        warning = "WARNING: User doesn't exist!"
        print("user doesn't exist")
        yt_link = ""
        twitch_link = ""
        

    
    return render_template('admin.html', ytlink=yt_link, t_link=twitch_link, warning=warning)

# ===== this route updates the admin information in the database
@app.route('/adminupdate')
def adminupdate():
    # set up the variables
    warning = ""
    result = ""

    # get the session information we set at sign-in
    if not session.get("email") is None:  # we have a user signed in
        email = session.get("email")
    else:  # user is not signed-in, return to sign-in page
        return redirect(url_for("login"))
    
    # capture the form info
    yt_link = request.args.get('yt')
    twitch_link = request.args.get('twitch')
    
    # get the current user info from the database to update
    try:
        existingUser = User.query.filter(User.email == email)
        print("user exists: " + existingUser[0].email)
        # update the links
        existingUser[0].youtubeLink = yt_link
        existingUser[0].instaLink = twitch_link  # just using an existing column (instaLink) for Twitch
        db.session.add(existingUser[0])
        db.session.commit()
        print("user admin info updated: " + existingUser[0].email)
        result = "Your information has been updated"
    except:   # user doesn't already exist, so we can add them
        warning = "WARNING: User doesn't exist!"
        print("user doesn't exist")
        yt_link = ""
        twitch_link = ""
        result = ""
    
    return render_template('admin.html', ytlink=yt_link, t_link=twitch_link, result=result, warning=warning)

@app.route('/test')
def test():
    return render_template('test.html')

# ===== this route is used to generate the chat page.  It is initially generate on sign-in
@app.route('/chat')
def chat():
    # set-up variables
    name = ""
    warning = ""
    email = ""
    # get the session information we set at sign-in, and ensure user is signed-in
    if not session.get("email") is None:  # we have a user signed in
        email = session.get("email")
    else:  # user is not signed-in, return to sign-in page
        return redirect(url_for("login"))
    
    # get the current user info from the database to auto-populate the form
    try:
        existingUser = User.query.filter(User.email == email)
        print("user exists: " + existingUser[0].email)
        # get the links
        yt_link = existingUser[0].youtubeLink
        print(yt_link)
        twitch_link = existingUser[0].instaLink   # just using an existing column (instaLink) for Twitch
        name = existingUser[0].firstName
    except:   # user doesn't already exist, so we can add them
        warning = "WARNING: User doesn't exist!"
        print("user doesn't exist")
        yt_link = ""
        twitch_link = ""
        
    return render_template('integrated_chat.html', name=name, ytlink=yt_link, t_link=twitch_link, warning=warning)

@app.route('/logout')
def logout():
    session["email"] = None
    return render_template('index.html')
    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# following route for testing
@app.route('/all')
def all():
    all_users = User.query.all()
    return render_template('all_users.html', all_users=details)



if __name__ == '__main__':
    #app.run()
    app.run(debug=True)

# Note: for this error: AssertionError: The sqlalchemy extension was not registered to the current application. Please make sure to call init_app() first.
# the following links might be helpful:
    # https://stackoverflow.com/questions/62147037/assertionerror-the-sqlalchemy-extension-was-not-registered-to-the-current-appli
    # https://stackoverflow.com/questions/30764073/sqlalchemy-extension-isnt-registered-when-running-app-with-gunicorn


