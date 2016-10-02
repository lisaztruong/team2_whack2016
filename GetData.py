# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 16:22:03 2016

@author: libbyaiello
"""

import sqlite3
conn = sqlite3.connect('schoolratings')
c1 = conn.cursor()

#don't call this unless you want to reset all the databases!!
def set_up():
    c1.execute('DROP TABLE t1_schools;')
    c1.execute('DROP TABLE t2_ratings;')
    c1.execute('CREATE TABLE t1_schools (school_id INTEGER PRIMARY KEY AUTOINCREMENT, school_name TEXT);')
    c1.execute('CREATE TABLE t2_ratings (rating_id INTEGER PRIMARY KEY AUTOINCREMENT, school_id, overall INTEGER, physical INTEGER, academic INTEGER, resources INTEGER, rating TEXT, FOREIGN KEY (school_id) REFERENCES t1_schools(school_id));')

# For the schoolname inputted by the user, this function calculates the average ratings for each category for this school
def get_ratings(schoolname):
    command = 'SELECT school_id FROM t1_schools WHERE school_name = \"'+schoolname+'\";'
    for schooldata in c1.execute(command):
        school_id = schooldata[0]
    count = 0.0
    overall_total   = 0
    physical_total  = 0
    academic_total  = 0
    resources_total = 0
    ratings = {}
    command = 'SELECT overall, physical, academic, resources, rating_id, rating FROM t2_ratings WHERE school_id = '+str(school_id)+';'
    for data in c1.execute(command):
        count             +=  1            
        overall_total     +=  data[0]
        physical_total    +=  data[1]
        academic_total    +=  data[2]
        resources_total   +=  data[3]
        rating_id          =  data[4]
        rating             =  data[5]
        ratings[rating_id] =  rating
    if count == 0:
        return None
    overall_average   = overall_total/count
    physical_average  = physical_total/count
    academic_average  = academic_total/count
    resources_average = resources_total/count
    return [overall_average, physical_average, academic_average, resources_average, ratings]
    
categories = {'overall':0, 'physical':1, 'academic':2, 'resources':3}


#this function takes in a category to sort by and returns a list of schools in descending order of their rankings in this category
def get_rankings(category):
    rankings = []
    #get all of the rankings
    for schooldata in c1.execute('SELECT school_name FROM t1_schools;'):
        schoolname = schooldata[0]
        rankings.append((schoolname, get_ratings(schoolname)[categories[category]]))
    #use lambda function to sort in descending order by x[1]
    return sorted(rankings, key = lambda x: x[1], reverse = True)
    

# Defaults scores below 0 to be 0 and scores higher than 10 to be 10 so that all scores are
# within the range 0-10
def put_in_range(score):
    if score > 10:
        return 10
    if score < 0:
        return 0
    return score    

# Interacts with the gui to allow users to input ratings for a school
def add_rating(schoolname, overall, physical, academic, resources, rating):
    overall = put_in_range(overall)
    physical = put_in_range(physical)
    academic = put_in_range(academic)
    resources = put_in_range(resources)
    school_id = 0
    #if the school already exists in t1_schools, pull up it's school_id
    for schooldata in c1.execute('SELECT school_id FROM t1_schools WHERE school_name = "'+schoolname+'";'):
        school_id = schooldata[0]
    c2 = conn.cursor()
    #if the school does not exist in the database, add it to t1_schools
    if school_id == 0:
        command = 'INSERT INTO t1_schools (school_name) VALUES (\"'+schoolname+'\")'
        c2.execute(command)
        for schooldata in c1.execute('SELECT school_id FROM t1_schools WHERE school_name = "'+schoolname+'";'):
            school_id = schooldata[0]
    #add this rating into t2_ratings
    c1.execute('INSERT INTO "t2_ratings" (school_id, overall, physical, academic, resources, rating) VALUES (?,?,?,?,?,?)',
               (school_id, overall, physical, academic, resources, rating))

# commits (updates the database) then closes the connection
c1.close()
conn.commit()
conn.close()