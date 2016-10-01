from flask import Flask, render_template, request, jsonify, url_for, redirect, make_response, session

from class_search_web_scrapping import GetTextBookInfo,GetCoursesTaught, GetAllProfessors, GetOptions, Sort_dict, GetClasses, GetSubjectsInDepartments, GetClassDescriptionAndAll, GetAllProfessorDepartments, Professors_No_Repeats
from database_functions import *
from TextbookDB import *

from password import create_user, validate_user
import requests
import datetime

app = Flask(__name__)
app.secret_key = 'This is a secret'



Options = GetOptions()
Sorted_Profs_No_Repeats = Professors_No_Repeats()
Professors = GetAllProfessors()
ProfDepartments = GetAllProfessorDepartments()




def GetCurrentSemester():
    return '201610'

@app.route('/internal_tooling', methods=["GET", "POST"])
def internal_tooling():
    login = True
    error = None
    if request.method == "post":
        login, error = validate_user("zjanicki@nd.edu", request.form["password"], True)
        if login:
            return render_template('internal_tooling.html', login = login, error = error)
    prof_reviews = getAllProfReviews()
    num_prof_reviews = len(prof_reviews)
    class_reviews = getAllClassReviews()
    num_class_reviews = len(class_reviews)
    return render_template('internal_tooling.html', login = login, error = error, prof_reviews = prof_reviews, num_prof_reviews = num_prof_reviews,
        class_reviews = class_reviews, num_class_reviews = num_class_reviews)


def isEmail(email):
    return bool('@' in email)

def cleanCourseFromReview(review):
    end = review.find("Course:::")
    review = review[0:end]
    return review

@app.route('/')
def home():
    Featured_prof = get_random_prof()
    prof_name = Featured_prof[1] + " " + Featured_prof[0].replace(',', '')
    workload_rating = convert_num_to_letter_grade(round(float(Featured_prof[3]),2))
    grading_rating = convert_num_to_letter_grade(round(float(Featured_prof[4]),2))
    quality_rating = convert_num_to_letter_grade(round(float(Featured_prof[5]),2))
    accessibility_rating = convert_num_to_letter_grade(round(float(Featured_prof[6]),2))
    review_count = count_reviews()
    last_name = prof_name.split(" ")[-1] + ', '
    first_name = ' '.join(i for i in prof_name.split(" ")[:-1] if i != '' and i != ' ')
    recent_reviews = [list(i) for i in recentReviews()]
    prof_names = [prof[1] + " " + prof[0].split(',')[0] for prof in recent_reviews]
    num_recent_reviews = len(prof_names)
    for review in recent_reviews:
        review[2] = cleanCourseFromReview(review[2])
        review[3] = convert_num_to_letter_grade(review[3])
        review[4] = convert_num_to_letter_grade(review[4])
        review[5] = convert_num_to_letter_grade(review[5])
        review[6] = convert_num_to_letter_grade(review[6])


    return render_template('home.html',last_name = last_name, first_name = first_name,
        prof_name = prof_name, workload_rating = workload_rating, grading_rating = grading_rating,
        quality_rating = quality_rating, accessibility_rating = accessibility_rating, review_count = review_count,
        prof_names = prof_names, recent_reviews = recent_reviews, num_recent_reviews = num_recent_reviews
        )


@app.route('/class_search/quick-search=<ATTR>', methods=["POST", "GET"])
def QuickSearch(ATTR):
    if request.method == "POST":
        Term = request.form['TermOptions']
        Subject = request.form.getlist('SubjectOptions')
        Credit = request.form['CreditsOptions']
        Attribute = request.form['AttributeOptions']
        Division = request.form['DivisionOptions']
        Campus = request.form['CampusOptions']
        return DisplayClasses(Term, Subject, Credit, Attribute, Division, Campus)
    Attributes = {'University Seminar (freshman)':"USEM",'1st Theology': 'THEO' , '1st Philosophy': 'PHIL','2nd Theology':'THE2', '2nd Philosophy':'PHI2', 'Social Science': 'SOSC', 'Natural Science (req)': 'NASC', 'Fine Arts':'FNAR', 'Literature':'LIT', 'History': 'HIST', "University Seminar":"USEM", "Sophomore Business Courses":"BA02", "Junior Business Courses": "BA03"}

    Subjects = GetOptions()[3].values()
    Semester = GetCurrentSemester()
    Attribute = Attributes[ATTR]
    return DisplayClasses(Semester, Subjects, Options[5]["All"], Attribute, "A", Options[2]["Main"])

@app.route('/search/<query>/', methods=['POST'])
def Search(query):
    unicode_profs = {}
    for prof in Sorted_Profs_No_Repeats:
        prof_name = unicode(prof, "utf-8")
        if query.lower() in prof_name.lower():
            unicode_profs[prof_name] = '/instructor_info/' + prof_name
    return jsonify(unicode_profs)


@app.route('/Department-search/<query>/', methods = ["POST"])
def Department_Search(query):
    unicode_subjects = {}
    for subject_key, subject_value in Options[3].items():
        subject_key = unicode(subj, "utf-8")
        if query.lower() in subject_key.lower():
            unicode_subjects[subject_key] = subject_value
    return jsonify(unicode_subjects)

@app.route('/class_search/', methods=['GET', 'POST'])
def ClassSearch():
    if request.method == 'POST':
        Term = request.form['TermOptions']
        Subject = request.form.getlist('SubjectOptions')
        if Subject[0] == "All":
            Subject = Options[3].values()
        Credit = request.form['CreditsOptions']
        Attribute = request.form['AttributeOptions']
        Division = request.form['DivisionOptions']
        Campus = request.form['CampusOptions']

        return DisplayClasses(Term, Subject, Credit, Attribute, Division, Campus)
    return render_template('class_search.html', TermOptionKeys=Sort_dict(Options[0], True), TermOptions=Options[0],
                           DivisionOptionKeys=Sort_dict(Options[1], False), DivisionOptions=Options[1],
                           CampusOptionKeys=Sort_dict(Options[2], False), CampusOptions=Options[2],
                           SubjectOptionKeys=Sort_dict(Options[3], False), SubjectOptions=Options[3],
                           AttributeOptionKeys=Sort_dict(Options[4], False), AttributeOptions=Options[4],
                           CreditsOptionKeys=Sort_dict(Options[5], False), CreditsOptions=Options[5])

@app.route('/instructor_eval/')
def eval():
    return render_template('instructor_eval.html', DepartmentKeys=Sort_dict(GetOptions()[3], False), DepartmentOptions=GetOptions()[3])

@app.route('/class_search/')
def DisplayClasses(term, subject, credit, attr, divs, campus):
    global Professors
    global ProfDepartments
    ClassList = GetClasses(term, subject, credit, attr, divs, campus)
    didAddProf = False
    didAddDept = False
    # Checks to see if every instructor is is Professors dictionary. If they
    # are not, we add their names to the text file, and recalculate the Professors dictionary
    ProfsAdded = []
    for course in ClassList:
        try:
            profs = course['Instructor']
            Department = ''.join([char for char in course['Course - Sec'].split(' ')[0] if char.isalpha()])
            P = [course['Teacher_Info'][i].split('P=')[-1] for i in range(len(course['Teacher_Info']))]
            for i in range(len(profs)):
                if profs[i] not in Professors:
                    f = open('TeacherList.txt', 'a')
                    f.write('<OPTION VALUE="' + str(P[i]) + '">' + str(profs[i]) + '\n')
                    f.close()
                    didAddProf = True
                if P[i] not in ProfDepartments and (P[i], Department) not in ProfsAdded:
                    f = open('ProfessorDepartments.txt', 'a')
                    #f.write(str(profs[i]) + '; Departments:'+ Department + '\n')
                    f.write(str(P[i]) + '; Departments:' + Department + '\n')
                    f.close()
                    didAddDept = True
                    ProfsAdded.append((P[i], Department))
                if Department not in ProfDepartments[P[i]] and (P[i], Department) not in ProfsAdded:
                    f = open('ProfessorDepartments.txt', 'a')
                    #f.write(str(profs[i]) + '; Departments:'+ Department + '\n')
                    f.write(str(P[i]) + '; Departments:' + Department + '\n')
                    f.close()
                    didAddDept = True
                    ProfsAdded.append((P[i], Department))

        except KeyError:
            pass
    if didAddProf:
        Professors = GetAllProfessors()
        didAddProf = False
    if didAddDept:
        ProfDepartments = GetAllProfessorDepartments()
        didAddDept = False
    # Keys specifies what exactly we want to show up on our class search

    Keys = ['Title', 'Course - Sec','Instructor', 'View_Books', 'Cr', 'Max', 'Opn', 'CRN', 'Teacher_Info', 'When', 'Begin', 'End', 'Where']
    return render_template('DisplayClassData.html', TermOptionKeys=Sort_dict(Options[0], True),
                           TermOptions=Options[0],
                           DivisionOptionKeys=Sort_dict(Options[1], False), DivisionOptions=Options[1],
                           CampusOptionKeys=Sort_dict(Options[2], False), CampusOptions=Options[2],
                           SubjectOptionKeys=Sort_dict(Options[3], False), SubjectOptions=Options[3],
                           AttributeOptionKeys=Sort_dict(Options[4], False), AttributeOptions=Options[4],
                           CreditsOptionKeys=Sort_dict(Options[5], False),
                           CreditsOptions=Options[5], ClassList=ClassList, Keys=Keys)

@app.route('/class_info/Textbook_info/<Term>-<Department>-<Course_number>-<section>', methods = ["POST"])
def get_textbook_info(Term, Department, Course_number, section):
    url = 'http://www.bkstr.com/webapp/wcs/stores/servlet/booklookServlet?bookstore_id-1=700&term_id-1='+ Term + '&div-1=&dept-1='+ Department + '&course-1='+ Course_number + '&section-1=' + section
    Textbooks, Required_textbook_info, Recommended_textbook_info = GetTextBookInfo(url)
    return jsonify({ "Textbooks" : Textbooks, "Required_textbook_info":Required_textbook_info, "Recommended_textbook_info":Recommended_textbook_info})

@app.route('/class_info/<Class>-<CRN>-<Term>', methods = ["GET"])
def DisplayClassPage(Class, CRN, Term):

    CourseName = Class
    Descriptions = GetClassDescriptionAndAll(CRN, Term)
    CourseDescription = Descriptions[0]
    Reviews = getClassReviews('', Class)
    CourseRatings = calculateClassRatings(Reviews)

    Individual_Reviews = [list(review) for review in Reviews[0] if review[3] != '']

    Semester_formatting = { value:key for key,value in Options[0].items()}
    month_formatting_dictionary = {1:'January', 2:"February", 3:'March', 4:"April",5:'May', 6:"June",7:'July', 8:"August",9:'September', 10:"October",11:'November', 12:"December"}
    for i in xrange(len(Individual_Reviews)):
        date = Individual_Reviews[i][12].split(" ")
        formatted_date = str(month_formatting_dictionary[int(date[1])]) + " " + str(date[2]) + ", " + str(date[0])
        Individual_Reviews[i][12] = formatted_date
        Individual_Reviews[i][9] = Semester_formatting[Individual_Reviews[i][9]]
        Individual_Reviews[i][4] = convert_num_to_letter_grade(Individual_Reviews[i][4])
        Individual_Reviews[i][5] = convert_num_to_letter_grade(Individual_Reviews[i][5])

    toughness = CourseRatings[3]
    interest = CourseRatings[4]
    Textbook = CourseRatings[5]

    if type(toughness) == str:
        Overall_Rating = ''
    else:
        Overall_Rating = convert_num_to_letter_grade(round((toughness + interest) / 2.0, 2))

    # Round numbers
    if type(toughness) == float:
        toughness = convert_num_to_letter_grade(round(toughness, 2))
    if type(interest) == float:
        interest = convert_num_to_letter_grade(round(interest, 2))
    if type(Textbook) == float:
        Textbook = round(Textbook, 2)
    Prerequisites = 'None listed'
    Corequisites = 'None listed'
    if Descriptions[1] == "Corequisite Only":
        Corequisites = Descriptions[2]
        Attributes = Descriptions[3]
        Restrictions = Descriptions[4]
        Registration = Descriptions[5]
        CrossListed = Descriptions[6]
        Department = Descriptions[7]
        Course_number = Descriptions[8]
        section = Descriptions[9]
    elif Descriptions[1] == "Both":
        Prerequisites = Descriptions[2]
        Corequisites = Descriptions[3]
        Attributes = Descriptions[4]
        Restrictions = Descriptions[5]
        Registration = Descriptions[6]
        CrossListed = Descriptions[7]
        Department = Descriptions[8]
        Course_number = Descriptions[9]
        section = Descriptions[10]
    elif  Descriptions[1] == 'Prerequisite Only':
        Prerequisites = Descriptions[2]
        Attributes = Descriptions[3]
        Restrictions = Descriptions[4]
        Registration = Descriptions[5]
        CrossListed = Descriptions[6]
        Department = Descriptions[7]
        Course_number = Descriptions[8]
        section = Descriptions[9]
    else:
        Attributes = Descriptions[2]
        Restrictions = Descriptions[3]
        Registration = Descriptions[4]
        CrossListed = Descriptions[5]
        Department = Descriptions[6]
        Course_number = Descriptions[7]
        section = Descriptions[8]
    Restrictions = ["Must " + i for i in Restrictions.split("Must")[1:]]
    Remaining = Registration.split("TOTAL")[1]
    Remaining = Remaining.split("\n")[1:-1]

    return render_template('class_info.html', Individual_Reviews=Individual_Reviews, Term = Term, Department = Department,
                        Course_number = Course_number, section = section,
                        CrossListed= CrossListed, Registration=Remaining,
                        Restrictions=Restrictions, Overall_Rating=Overall_Rating,
                        Prerequisites=Prerequisites, Corequisites=Corequisites,
                        CourseName=CourseName, CourseDescription=CourseDescription,
                        Textbook=Textbook, interest=interest,
                        toughness=toughness, Attributes=Attributes, crn=CRN
                        )

@app.route('/DepartmentsMain/')
def DepartmentsMainPage():
    DepartmentsByCollege = GetSubjectsInDepartments()
    Colleges = ['College of Arts & Letters', 'College of Engineering', 'College of Science', 'Mendoza College of Business', 'First Year of Studies', 'The Law School', "St. Mary's College", 'Other', 'School of Architecture']
    return render_template('DepartmentsMain.html', DepartmentsByCollege=DepartmentsByCollege, Colleges=Colleges)

@app.route('/InstructorByCollege/<College>')
def InstructorByCollege(College):
    Departments = [i for i in GetSubjectsInDepartments() if College in i[0]][0][1:]
    return render_template('InstructorByCollege.html', College=College, Departments=Departments, Teachers=Teachers)

@app.route('/Department/<Department>')
def InstructorByDepartment(Department):
    Teachers = []

    ID_dict = {}

    Department_Name = Options[3][Department]
    for prof, ID in Professors.items():
        department = ProfDepartments.get(ID)
        if department and  Department_Name in department and ID not in ID_dict:
            Teachers.append(prof)
            ID_dict[ID] = 1

    Teachers = sorted(Teachers)
    Teachers_Sorted = Sort_dict(Teachers, False)
    Best_Teachers, Best_Teachers_Sorted = bestProf(Options[3][Department])
    Easiest_Teachers, Easiest_Teachers_Sorted = easiestProf(Options[3][Department])
    Best_Classes, Best_Classes_Sorted = bestClass(Options[3][Department])

    for course in Best_Classes:
        Best_Classes[course][0] = convert_num_to_letter_grade( Best_Classes[course][0])
    for course in Easiest_Teachers:
        Easiest_Teachers[course] = convert_num_to_letter_grade( Easiest_Teachers[course])
    for course in Best_Teachers:
        Best_Teachers[course] = convert_num_to_letter_grade( Best_Teachers[course])
    Crn_and_Term = {}
    for course in Best_Classes_Sorted:
        Course = getClassReviews('', course)[0][0]
        Crn_and_Term[Course[2]] = ((Course[-2], Course[-1]))

    Easiest_Classes, Easiest_Classes_Sorted = easiestClass(Options[3][Department])
    for course in Easiest_Classes:
        Easiest_Classes[course][0] = convert_num_to_letter_grade( Easiest_Classes[course][0])

    DepartmentOptions = Options[3]
    for option in DepartmentOptions:
        if DepartmentOptions[option] == Department:
            Department = option

    number_of_courses = len(Easiest_Classes_Sorted)
    number_of_teachers = len(Best_Teachers_Sorted)
    return render_template('Department.html', number_of_teachers = number_of_teachers, number_of_courses = number_of_courses, Teachers_Sorted=Teachers_Sorted,
                           Best_Teachers_Sorted=Best_Teachers_Sorted, Best_Teachers=Best_Teachers,
                           Easiest_Teachers=Easiest_Teachers, Easiest_Teachers_Sorted=Easiest_Teachers_Sorted,
                           Department=Department, Teachers=Teachers, Best_Classes=Best_Classes,
                           Best_Classes_Sorted=Best_Classes_Sorted, Easiest_Classes=Easiest_Classes,
                           Easiest_Classes_Sorted=Easiest_Classes_Sorted,
                           Crn_and_Term=Crn_and_Term)

@app.route('/instructor_info/<ProfessorName>')
def Instructor(ProfessorName):
    try:
        CoursesTaught = GetCoursesTaught(Professors[ProfessorName])
        num_items = len(CoursesTaught[0]) - 1 # need this to be index of semester code
    except KeyError:
        CoursesTaught = []
    except IndexError:
        CoursesTaught = []
    RevisedCoursesTaught = []
    prev_course_id = ""
    for i in xrange(len(CoursesTaught)):
        
        current_course_id = "{} {}".format(CoursesTaught[i][0].split()[0], CoursesTaught[i][1])
        if i != 0:
            if (prev_course_id != current_course_id) or (CoursesTaught[i][num_items] != CoursesTaught[i-1][num_items]):
                RevisedCoursesTaught.append(CoursesTaught[i])
        else:
            RevisedCoursesTaught.append(CoursesTaught[i])
        prev_course_id = current_course_id

    last_name = str(ProfessorName.split(',')[0]) + ','
    first_name = str(ProfessorName.split(',')[1])
    try:
        Reviews = getProfReviews(Professors[last_name + first_name])
        num_reviews = len(Reviews)
        OverallRatings = calculateProfRatings(Reviews)

        Individual_Reviews = [list(review) for review in Reviews[::-1] if review[2] != '']

        review_courses = []
        for review in Individual_Reviews:
            course_name = ''
            description = review[2].split("Course:::")
            if len(description) > 1:
                course_name = description[-1]
                description = description[0]
            else:
                description = review[2]
            review.append(course_name)
            review[2] = description

        Semester_formatting = { value:key for key,value in Options[0].items()}
        month_formatting_dictionary = {1:'January', 2:"February", 3:'March', 4:"April",5:'May', 6:"June",7:'July', 8:"August",9:'September', 10:"October",11:'November', 12:"December"}
        for i in xrange(len(Individual_Reviews)):
            date = Individual_Reviews[i][11].split(" ")
            formatted_date = str(month_formatting_dictionary[int(date[1])]) + " " + str(date[2]) + ", " + str(date[0])
            Individual_Reviews[i][11] = formatted_date
            Individual_Reviews[i][3] = convert_num_to_letter_grade(Individual_Reviews[i][3])
            Individual_Reviews[i][4] = convert_num_to_letter_grade(Individual_Reviews[i][4])
            Individual_Reviews[i][5] = convert_num_to_letter_grade(Individual_Reviews[i][5])
            Individual_Reviews[i][6] = convert_num_to_letter_grade(Individual_Reviews[i][6])

        workload = OverallRatings[3]
        if type(workload) == float:
            workload = round(workload, 2)

        grading = OverallRatings[4]
        if type(grading) == float:
            grading = round(grading, 2)
        quality = OverallRatings[5]
        if type(quality) == float:
            quality = round(quality, 2)
        accessibility = OverallRatings[6]
        if type(accessibility) == float:
            accessibility = round(accessibility, 2)
        syllabus = OverallRatings[7]
        if type(syllabus) == float:
            syllabus = round(syllabus, 2)

        ProfReviews = OverallRatings[2]
        return render_template('instructor_info.html', Individual_Reviews = Individual_Reviews,Courses=RevisedCoursesTaught,
                               ProfessorName=ProfessorName,num_reviews = num_reviews,
                                workload=convert_num_to_letter_grade(workload), grading=convert_num_to_letter_grade(grading), quality=convert_num_to_letter_grade(quality),
                               accessibility=convert_num_to_letter_grade(accessibility))
    except KeyError:
        return render_template('instructor_info.html', Courses=RevisedCoursesTaught,num_reviews = 0,
                               ProfessorName=ProfessorName)

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

@app.route('/feature_work/')
def feature_work():
    return render_template('feature_work.html')

@app.route('/message_board/')
def message_board():
    return render_template('message_board.html', all_posts=getPosts())

@app.route('/alert/<crn>/<number>/', methods=['POST'])
def send_alert(crn, number="void"):
    """
    Adds an entry to the class alerts texting database
    for a user with phone number @number and for the
    crn @crn
    """
    if number!='void':
        addNumber(number, crn)
        return 'Success! Keep an eye out for a text'
    else:
        return 'Error: Must include a phone number'

@app.route('/Textbooks/')
def textbook_board():
    textbook_info = Get_Textbooks()
    textbooks = []
    for i in textbook_info:
        new_textbook = {}
        new_textbook['ID'] = i[0]
        new_textbook['title'] = i[1]
        new_textbook['email'] = i[2]
        new_textbook['price'] = i[3]
        new_textbook['price'].replace("$$", "$")
        new_textbook['description'] = i[4]
        new_textbook['department'] = i[5]
        new_textbook['course'] = i[6]
        new_textbook['date'] = i[7]
        textbooks.append(new_textbook)
    return render_template('TextbooksBoard.html', textbooks = textbooks)

@app.route('/Textbooks/NewTextbook', methods = ["GET", "POST"])
def add_Textbook(error = None):

    DepartmentsByCollege = GetSubjectsInDepartments()
    Colleges = ['College of Arts & Letters', 'College of Engineering', 'College of Science', 'Mendoza College of Business', 'First Year of Studies', 'The Law School', "St. Mary's College", 'Other', 'School of Architecture']

    if request.method == "POST":
        # if error:
        #     return render_template('Add_Textbook_Form.html', SubjectOptionKeys=Sort_dict(Options[3], False), SubjectOptions=Options[3],
        #     DepartmentsByCollege = DepartmentsByCollege, Colleges = Colleges, error = error)


        seller = {}
        seller['email'] = request.form['Email']

        department = request.form.getlist('DepartmentSelect')
        if len(department) == 0:
            department = "None chosen"
        else:
            department = department[0]
        seller['textbook_department'] = department
        seller['textbook_title'] = request.form['TextbookName']
        seller['price'] = request.form['price']
        seller['textbook_description'] = request.form['TextbookDescription']
        seller['course'] = request.form['course']
        Insert_Textbook(seller)
        return redirect(url_for('textbook_board'))

    else:
        return render_template('Add_Textbook_Form.html', SubjectOptionKeys=Sort_dict(Options[3], False), SubjectOptions=Options[3],
            DepartmentsByCollege = DepartmentsByCollege, Colleges = Colleges, error = error)


@app.route('/Textbooks/ID=<ID>', methods = ["GET", "POST"])
def contact_seller(ID):
    Textbook_info = Get_Textbook(ID)
    textbook = {}
    textbook['ID'] = Textbook_info[0]
    textbook['title'] = Textbook_info[1]
    textbook['email'] = Textbook_info[2]
    textbook['price'] = Textbook_info[3]
    textbook['description'] = Textbook_info[4]
    textbook['department'] = Textbook_info[5]
    textbook['course'] = Textbook_info[6]
    textbook['date'] = Textbook_info[7]

    if request.method == "POST":
        seller = textbook
        buyer = {}
        buyer['name'] = request.form['name']
        buyer['email'] = request.form['email']
        buyer['message'] = request.form['message']
        Send_Textbook_Email(buyer, seller)
        return redirect(url_for('textbook_board'))
    return render_template('Contact_seller.html', textbook = textbook)

@app.route('/Chandelier')
def Henry_Long():
    return render_template('Chandelier.html')

def convert_num_to_letter_grade(num):
    if num == "" or num == " ":
        return num
    if type(num) == str:
        num = float(num)
    if num < 2:
        return 'F'
    elif num < 2.6:
        return 'D-'
    elif num < 3.3:
        return 'D'
    elif num < 4:
        return 'D+'
    elif num < 4.6:
        return 'C-'
    elif num < 5.8:
        return 'C'
    elif num <  6.4:
        return 'C+'
    elif num < 7.4:
        return 'B-'
    elif num < 8.2:
        return 'B'
    elif num < 8.6:
        return 'B+'
    elif num < 9:
        return 'A-'
    elif num < 9.4:
        return 'A'
    else:
        return 'A+'

if __name__ == '__main__':
    app.run()
