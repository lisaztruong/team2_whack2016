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
c2 = conn.cursor()

def get_ratings(schoolname):
    for schooldata in c1.execute('SELECT school_id FROM t1_schools WHERE school_name = '+schoolname+';'):
        school_id = schooldata[0]
    count = 0.0
    overall_total = 0
    physical_total = 0
    academic_total = 0
    resources_total = 0
    ratings = {}
    for data in c2.execute('SELECT overall, physical, academic, resources, rating_id, rating FROM t2_ratings WHERE school_id = '+school_id+';'):
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
    
def add_rating(schoolname, overall, physical, academic, resources, rating):
    overall = put_in_range(overall)
    physical = put_in_range(physical)
    academic = put_in_range(academic)
    
    
def put_in_range(score):
    if score > 10:
        return 10
    if score < 0:
        return 0
        

