# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 14:47:00 2020

@author:
"""

# ==========
# this file used to test the database
# for example, printing all items from the database
# ++++++++++

from flask import Flask, render_template, request
from main_sql_schema import db, User

# all_users = User.query.all()  # list all users
# print(all_users)


existingUser = User.query.filter(User.email == 'email1@uab.edu')
print("user exists: " + existingUser[0].email) 
print(existingUser[0])
existingUser[0].instaKey = "free"

db.session.add(existingUser[0])
db.session.commit()
print(existingUser[0].instaKey)
db.session.commit()


all_users = User.query.all()  # list all users
print(all_users)
# the following lines used to test adding a user to the database
'''
# add user to the database
user2 = User("user2last", "user2", "user2@uab.edu", "Password1")
db.session.add(user2)
db.session.commit()

all_users = User.query.all()  # list all users
print(all_users)
'''

# the following lines to delete items from the database:
'''
user_to_delete = User.query.get(5)
db.session.delete(user_to_delete)
db.session.commit()
'''