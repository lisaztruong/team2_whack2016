'''
from flask import Flask, render_template, request, jsonify, url_for, redirect, make_response, session

from class_search_web_scrapping import GetTextBookInfo,GetCoursesTaught, GetAllProfessors, GetOptions, Sort_dict, GetClasses, GetSubjectsInDepartments, GetClassDescriptionAndAll, GetAllProfessorDepartments, Professors_No_Repeats
from database_functions import *
from TextbookDB import *

from password import create_user, validate_user
import requests
import datetime
'''

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
def get_avg_ratings(schoolname):
    schoolname = schoolname.lower()
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
    
def get_ratings(schoolname):
    schoolname = schoolname.lower()
    command = 'SELECT school_id FROM t1_schools WHERE school_name = \"'+schoolname+'\";'
    school_id = 0
    for schooldata in c1.execute(command):
        school_id = schooldata[0]
    if school_id == 0:
        return []
    ratings = []
    command = 'SELECT overall, physical, academic, resources, rating_id, rating FROM t2_ratings WHERE school_id = '+str(school_id)+';'
    for data in c1.execute(command):
        ratings.append(data)
    return ratings
    
categories = {'overall':0, 'physical':1, 'academic':2, 'resources':3}

#this function takes in a category to sort by and returns a list of schools in descending order of their rankings in this category
def get_rankings(category):
    category = category.lower()
    rankings = []
    #get all of the rankings
    for schooldata in c1.execute('SELECT school_name FROM t1_schools;'):
        schoolname = schooldata[0]
        rankings.append((schoolname, get_ratings(schoolname)[categories[category]]))
    #use lambda function to sort in descending order by x[1]
    return sorted(rankings, key = lambda x: x[1], reverse = True)
  

# Interacts with the gui to allow users to input ratings for a school
def add_rating(schoolname, overall, physical, academic, resources, rating):
    schoolname = schoolname.lower()
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

def get_random_school():
    rankings = get_rankings(physical)
    import random
    rand = random.randint(0,len(rankings))
    return rankings[rand]

@app.route('/')
def home():
    #get_random_school returns (school_name, [overall_average, physical_average, academic_average, resources_average, ratings])
    featured_school = get_random_school()
    school_name = featured_school[0]
    overall_rating = featured_school[1][0]
    physical_rating = featured_school[1][1]
    academic_rating = featured_school[1][2]
    resources_rating = featured_school[1][3]
    return render_template('home.html', school_name = school_name, workload_rating = workload_rating,
        overall_rating = overall_rating, physical_rating = physical_rating, academic_rating = academic_rating,
        resources_rating = resources_rating)

@app.route('/search/<query>/', methods=['POST'])
def Search(query):
    return get_ratings(query.lower()) #we can format it from the javascript file
    #OR SHOULD THIS FORWARD TO A SCHOOL PAGE?


@app.route('/schoolname/')
def School(schoolname):
    #need to determine from templates
    return render_template('instructor_info.html', Individual_Reviews = Individual_Reviews,Courses=RevisedCoursesTaught,
                               ProfessorName=ProfessorName,num_reviews = num_reviews,
                                workload=convert_num_to_letter_grade(workload), grading=convert_num_to_letter_grade(grading), quality=convert_num_to_letter_grade(quality),
                               accessibility=convert_num_to_letter_grade(accessibility))


@app.route('/BestClassesFor/', methods=['GET', 'POST'])
def BestClassesFor(page=1):
    # Dummy list until we can access classes from database
    if page == 1:
        Attributes = {'2nd Theology':'THE2', '2nd Philosophy':'PHI2', 'Social Science': 'SOSC', 'Natural Science (req)': 'NASC'}
    elif page == 2:
        Attributes = {'Fine Arts':'FNAR', 'Literature':'LIT', 'History': 'HIST'}
    ClassList = []
    if page == 1:
        SubjectsSorted = ['2nd Theology', '2nd Philosophy', 'Social Science', 'Natural Science (req)']
    elif page == 2:
        SubjectsSorted = ['Fine Arts', 'Literature', 'History']
    Indexs = range(len(SubjectsSorted))
    for attr in SubjectsSorted:
        courses = GetClasses('201510', Options[3].values(), 'A', Attributes[attr], 'A', 'M')
        course_container = []
        for i in courses:
            course_container.append([i['Title'], i['CRN'], i['Term']])
        ClassList.append(course_container)

    return render_template('BestClassesFor.html', Subjects=Attributes, SubjectsSorted=SubjectsSorted, Courses=ClassList, Indexs=Indexs)

@app.route('/ProfessorReviewForm/<ProfessorName>', methods=['GET', 'POST'])
def ProfessorReview(ProfessorName):
    #do i need all of these?
    if request.method == 'POST':
        # Instructor evaluation
        CourseName = ' '.join(request.form['CoursesTaughtID'].split(' ')[:-3])
        CRN = ''.join(request.form['CoursesTaughtID'].split(' ')[-3])
        Term = ''.join(request.form['CoursesTaughtID'].split(' ')[-2])
        department = [request.form['CoursesTaughtID'].split(' ')[-1]]
        Grading = int(request.form['GradingID'])
        Quality = int(request.form['QualityID'])
        Workload = int(request.form['WorkloadID'])
        Accessibility = request.form['AccessibilityID']
        Syllabus = int(request.form['SyllabusID'])
        OptionalDescriptionProfessor = str(request.form['OptionalResponseProfessor']) + "Course:::" + str(CourseName)


        # Course Evaluation
        CourseToughness = int(request.form['ToughnessID'])
        CourseInterest = int(request.form['InterestID'])
        TextbookNeeded = int(request.form['TextbookNeeded'])
        OptionalDescriptionCourse = str(request.form['OptionalResponseCourse'])

        # Add to database
        last_name = str(ProfessorName.split(',')[0]) + ','
        first_name = str(ProfessorName.split(',')[1])


        date = datetime.datetime.now()
        date_string = str(date.year) + " " + str(date.month) + " " + str(date.day)

        if session.get('username'):
            username = session['username']
        else:
            username = "Unknown user"
        addProfReview(last_name, first_name, OptionalDescriptionProfessor, Workload, Grading, Quality, Accessibility, Syllabus, department, Professors[last_name + first_name], username, date_string)
        addClassReview(last_name, first_name, CourseName, OptionalDescriptionCourse, CourseToughness, CourseInterest, TextbookNeeded, department, CRN, Term, Professors[last_name + first_name], username, date_string)
        return render_template('PostSubmissionForm.html', test=' ')

    try:
        CoursesTaught = GetCoursesTaught(Professors[ProfessorName])
    except KeyError:
        CoursesTaught = ["No courses listed"]

    num_items = len(CoursesTaught[0]) - 1
    RevisedCoursesTaught = []
    for i in xrange(len(CoursesTaught)):
        if i != 0:
            if (CoursesTaught[i][2] != CoursesTaught[i-1][2]) or (CoursesTaught[i][num_items] != CoursesTaught[i-1][num_items]):
                RevisedCoursesTaught.append(CoursesTaught[i])
        else:
            RevisedCoursesTaught.append(CoursesTaught[i])
    return render_template('ProfessorReviewForm.html' ,ProfessorName=ProfessorName, CoursesTaught=RevisedCoursesTaught, num_items = num_items)

@app.route('/SubmitReviewMain/')
def SubmitReviewMain():
    ProfessorKeys = Sorted_Profs_No_Repeats
    ProfessorKeys = [i.decode('utf-8') for i in ProfessorKeys]
    return render_template('SubmitReviewMain.html',
                           DepartmentKeys=Sort_dict(Options[3], False),
                           DepartmentOptions=Options[3],
                           Professors=Professors, ProfessorKeys=ProfessorKeys)

if __name__ == '__main__':
    app.run()
