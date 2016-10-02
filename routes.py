# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 16:22:03 2016

@author: libbyaiello
"""
from flask import Flask, render_template, request
app = Flask(__name__)
import sqlite3
conn = sqlite3.connect('schoolratings')
c1 = conn.cursor()

'''Functions that interface with database'''

#don't call this unless you want to reset all the databases!!
def set_up():
    c1.execute('DROP TABLE t1_schools;')
    c1.execute('DROP TABLE t2_ratings;')
    c1.execute('CREATE TABLE t1_schools (school_id INTEGER PRIMARY KEY AUTOINCREMENT, school_name TEXT);')
    c1.execute('CREATE TABLE t2_ratings (rating_id INTEGER PRIMARY KEY AUTOINCREMENT, school_id, overall INTEGER, physical INTEGER, academic INTEGER, resources INTEGER, rating TEXT, FOREIGN KEY (school_id) REFERENCES t1_schools(school_id));')

def number_of_schools():
    for item in c1.execute('SELECT COUNT(*) FROM t1_schools'):
        return item[0]
    return 0

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
categories_reverse = {0:'overall', 1:'physical', 2:'academic', 3:'resources'}


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

def get_random_school():
    rankings = get_rankings('physical')
    import random
    rand = random.randint(0,len(rankings))
    return rankings[rand]

'''Now interfacing with javascript'''

'''Lists of pages:
-- '/' = home
-- '/search/<query>/' = search result page --> query might pull up multiple schools (if not finished, or might say not found, or forwards to schoolname page)
-- '/<schoolname>' = school homepage --> shows averages of ratings on top, and all ratings below
-- '/bestSchoolsFor/<page>' = list of rankings of schools for specific category (page is an integer 0 - 3)
-- '/schoolReviewForm/' = page where you can fill out a review for a school.
'''

@app.route('/')
def home():
    #get_random_school returns (school_name, [overall_average, physical_average, academic_average, resources_average, ratings])
    featured_school = get_random_school()
    school_name = featured_school[0]
    overall_rating = featured_school[1][0]
    physical_rating = featured_school[1][1]
    academic_rating = featured_school[1][2]
    resources_rating = featured_school[1][3]
    num_of_schools = number_of_schools()
    return render_template('home.html', num_of_schools = num_of_schools, school_name = school_name, overall_rating = overall_rating,
        physical_rating = physical_rating, academic_rating = academic_rating, resources_rating = resources_rating)

@app.route('/search/<query>/', methods=['POST'])
def Search(query):
    
    ratings = get_ratings(query.lower())
    return render_template('search.html', query.lower(), ratings) #ratings is a list with overall, physical, academic, resources, rating_id

@app.route('/<schoolname>/')
def School(schoolname):
    schoolname = schoolname.lower()
    #should return all reviews, and have a header with the average reviews.
    avg_ratings = get_avg_ratings(schoolname)
    all_ratings = get_ratings(schoolname)
    return render_template('school_info.html', schoolname, avg_ratings, all_ratings) #avg_ratings/all_ratings good have size 0 if no reviews yet

@app.route('/bestSchoolsFor/<page>', methods=['GET', 'POST']) #is this how i add the page value?
def bestSchoolsFor(page):
    category = categories_reverse[page]
    rankings = get_rankings(category) # formatted as schoolname, value for specific category
    return render_template('bestSchoolsFor.html', category, rankings) #category name should go on the top of the page, rankings should be displayed in table (schoolname is a link to school page)

@app.route('/schoolReviewForm/', methods=['GET', 'POST'])
def SchoolReview():
    #def SchoolReview(schoolname):
    #for posting school review
    if request.method == 'POST':
        #get info from form
        schoolname = request.form['schoolname']
        overall = request.form['overall']
        physical = request.form['physical']
        academic = request.form['academic']
        resources = request.form['resources']
        rating = request.form['rating']
        
        #add to database!
        add_rating(schoolname, overall, physical, academic, resources, rating)

        return render_template('PostSubmissionForm.html', test=' ')
        
    #for getting school review
    return School(schoolname)    

if __name__ == '__main__':
    app.run()
# commits (updates the database) then closes the connection
c1.close()
conn.commit()
conn.close()