# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:26:29 2020

@author:
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRAC_MODIFICATIONS']=False

db=SQLAlchemy(app)
Migrate(app,db)

class User(db.Model):
    __tablename__="user_login"
    
    id = db.Column(db.Integer, primary_key=True)
    lastName = db.Column(db.Text)
    firstName = db.Column(db.Text)
    email = db.Column(db.Text)
    pwd = db.Column(db.Text)
    numAttempts = db.Column(db.Integer)
    youtubeLink = db.Column(db.Text)
    youtubeKey = db.Column(db.Text)
    facebookLink = db.Column(db.Text)
    facebookKey = db.Column(db.Text)
    instaLink = db.Column(db.Text)
    instaKey = db.Column(db.Text)
    
    def __init__(self, l, f, e, p):
        self.lastName = l
        self.firstName = f
        self.email = e
        self.pwd = p
        self.numAttempts = 0
        self.youtubeLink = ""
        self.youtubeKey = ""
        self.facebookLink = ""
        self.facebookKey = ""
        self.instaLink = ""
        self.instaKey = ""
        
    def __repr__(self):
        return f"{self.id}: {self.lastName}, {self.firstName}, email: {self.email},  pwd: {self.pwd} || {self.youtubeLink} | {self.instaLink}"