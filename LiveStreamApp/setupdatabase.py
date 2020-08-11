# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:41:10 2020

@author:
"""

from main_sql_schema import db, User

db.create_all()

user1 = User("LastName1", "FirstName1", "email1@uab.edu", "password1")



db.session.add_all([user1])
db.session.commit()






