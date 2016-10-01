# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 16:22:03 2016

@author: libbyaiello
"""

import sqlite3
conn = sqlite3.connect('schoolratings')
#t1_schools (school_id INTEGER, school_name TEXT)
#t2_ratings (rating_id INTEGER, school_id INTEGER, overall INTEGER, physical INTEGER, academic INTEGER, resources INTEGER, rating TEXT)
c1 = conn.cursor()

def set_up():
    c1.execute('DROP TABLE t1_schools;')
    c1.execute('DROP TABLE t2_ratings;')
    c1.execute('CREATE TABLE t1_schools (school_id INTEGER PRIMARY KEY AUTOINCREMENT, school_name TEXT);')
    c1.execute('CREATE TABLE t2_ratings (rating_id INTEGER PRIMARY KEY AUTOINCREMENT, school_id, overall INTEGER, physical INTEGER, academic INTEGER, resources INTEGER, rating TEXT, FOREIGN KEY (school_id) REFERENCES t1_schools(school_id));')

def get_ratings(schoolname):
    for schooldata in c1.execute('SELECT school_id FROM t1_schools WHERE school_name = "'+str(schoolname)+'";'):
        school_id = schooldata[0]
        print(school_id)
        break
    count = 0.0
    overall_total = 0
    physical_total = 0
    academic_total = 0
    resources_total = 0
    ratings = {}
    for data in c1.execute('SELECT overall, physical, academic, resources, rating_id, rating FROM t2_ratings WHERE school_id = '+school_id+';'):
        count             +=  1            
        overall_total     +=  data[0]
        physical_total    +=  data[1]
        academic_total    +=  data[2]
        resources_total   +=  data[3]
        rating_id          =  data[4]
        rating             =  data[5]
        ratings[rating_id] =  rating
    overall_average   = overall_total/count
    physical_average  = physical_total/count
    academic_average  = academic_total/count
    resources_average = resources_total/count
    return [overall_average, physical_average, academic_average, resources_average, ratings]
    
#print(get_ratings("MIT"))
    
def put_in_range(score):
    if score > 10:
        return 10
    if score < 0:
        return 0
    return score    
    
def add_rating(schoolname, overall, physical, academic, resources, rating):
    overall = put_in_range(overall)
    physical = put_in_range(physical)
    academic = put_in_range(academic)
    resources = put_in_range(resources)
    for schooldata in c1.execute('SELECT school_id FROM t1_schools WHERE school_name = "'+schoolname+'";'):
        school_id = schooldata[0]
    c1.execute('INSERT INTO "t2_ratings" (school_id, overall, physical, academic, resources, rating) VALUES (?,?,?,?,?,?)',
               (school_id, overall, physical, academic, resources, rating))
    
    
add_rating("MIT", 10, 10, 10, 10, "it rocks")
    
c1.close()
conn.commit()
conn.close()