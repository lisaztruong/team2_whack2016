from bs4 import BeautifulSoup
import urllib2
import re
import requests
import time

def CleanUpString(string):
    """Cleans up a string by getting rid of '\\t', '\\r', '\\n', and double spaces (i.e. '  ').
    Input: string
    Returns: String
    """
    return string.replace('\t', '').replace('\r', '').replace('\n', '').replace('  ', '')

def GetCurrentSemester():
    return "201610"

def GetTextBookInfo(url):
    """
    Gets ISBN and Textbook info from Notre Dame bookstore


    """
    try:
        response = requests.get(url, timeout = 8.0)
        soup = BeautifulSoup(response.content, "lxml")
        isbn_info = [i.text for i in soup.find_all('span', attrs = {'id': 'materialISBN'})]
        isbns = [str(isbn.split("ISBN: ")[1]) for isbn in isbn_info]

        author_info = [i.text for i in soup.find_all('span', attrs = {'id':'materialAuthor'})]
        authors = [str(author.split("Author: ")[1]) for author in author_info]

        Titles_info = [str(i.text) for i in soup.find_all("h3", attrs = {'class':'material-group-title'})]
        choice_of_titles_index = -1
        for i in xrange(len(Titles_info)):
            Titles_info[i] = Titles_info[i].replace("Edition", " Edition")
            if "Choice of Titles" in Titles_info[i]:
                choice_of_titles_index = i

        if choice_of_titles_index != -1:
            Titles_info.pop(choice_of_titles_index)

        Textbooks = []
        for i in xrange(len(authors)):
            new_textbook = {}
            new_textbook['author'] = CleanUpString(authors[i])
            new_textbook['isbn'] = CleanUpString(isbns[i])
            new_textbook['title'] = CleanUpString(Titles_info[i])
            Textbooks.append(new_textbook)

        required_books = soup.find_all("li", attrs = {"id":"material-group_REQUIRED"})
        if len(required_books):
            textbook_info  = required_books[0].find_all("div", attrs = {"class":"material-group-table"})
        else:
            textbook_info = []



        Headers = ["Type", "Buy/Rent", "Option", "Rental Period", "Provider"]
        Required_Textbook_Info = []
        for textbook in textbook_info:
            new_textbook = []
            textbook_options = textbook.find_all("tr", attrs = {"class": "print_background"})
            for i in xrange(len(textbook_options)):
                new_option = {}
                info = textbook_options[i].find_all("td", attrs = {'class':None})
                for j in xrange(len(info)):
                    new_option[Headers[j]] = info[j].text
                price = textbook_options[i].find_all("td", attrs = {'class': 'align_right right_border'})
                new_option["Price"] = price[0].text
                new_textbook.append(new_option)
            Required_Textbook_Info.append(new_textbook)


        Recommended_books = soup.find_all("li", attrs = {"id":"material-group_RECOMMENDED"})
        if len(Recommended_books):
            textbook_info  = Recommended_books[0].find_all("div", attrs = {"class":"material-group-table"})
        else:
            textbook_info = []

        Recommended_Textbook_Info = []
        for textbook in textbook_info:
            new_textbook = []
            textbook_options = textbook.find_all("tr", attrs = {"class": "print_background"})
            for i in xrange(len(textbook_options)):
                new_option = {}
                info = textbook_options[i].find_all("td", attrs = {'class':None})
                for j in xrange(len(info)):
                    new_option[Headers[j]] = info[j].text
                price = textbook_options[i].find_all("td", attrs = {'class': 'align_right right_border'})
                new_option["Price"] = price[0].text
                new_textbook.append(new_option)
            Recommended_Textbook_Info.append(new_textbook)
        return Textbooks, Required_Textbook_Info, Recommended_Textbook_Info
    except requests.exceptions.Timeout:
        return [], [], []


def GetOptions():
    """
    Gets the options for the 6 categories (Term, Division, Campus, Subject, Attribute, and Credits)
    Gets both the option that is displayed on class-search.nd.edu as well as the option_key
    that is neccessary to submit the post request in order to navigate to the correct page
    Returns: dictionary of option_descriptions (what is displayed on class-search.nd.edu)
        that point to option_keys{option_description: option_key}
    """

    url = 'https://class-search.nd.edu/reg/srch/ClassSearchServlet'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    data = soup.find_all('select')

    # Dictionaries used to store both option description and the form
    # data value required for post requests
    TermOptions = {}
    DivisionOptions = {}
    CampusOptions = {}
    SubjectOptions = {}
    AttributeOptions = {}
    CreditsOptions = {}

    OptionCategories = [TermOptions, DivisionOptions, CampusOptions,
                        SubjectOptions, AttributeOptions, CreditsOptions]

    for i, category in zip(data, OptionCategories):
        options = i.find_all('option')
        for option in options:
            # check if option is selected. If so, then use 4th item in list
            option_split = str(option).split('"')
            if 'selected' in option_split[0]:
                category[CleanUpString(str(option.text))] = str(option).split('"')[3]
            else:
                category[CleanUpString(str(option.text))] = str(option).split('"')[1]

    # Get rid of all Year entries for TermOptions
    New_Term_Options = OptionCategories[0].copy()
    for entry in New_Term_Options:
        if 'Year' in entry:
            del OptionCategories[0][entry]
    for key in OptionCategories[3]:
        if "/" in key:
            OptionCategories[3][key.replace("/", " and ")] = OptionCategories[3][key]
            del OptionCategories[3][key]
    return OptionCategories

def GetClasses(term, subj, credit, Attr, divs, campus):
    """
    Given the inputs, function will find the class data from class-search.nd.edu.
    Inputs: Academic term, Academic subject, number of credits, Attribute type,
       Academic division, and finally campus.
       All should be in the form of strings
    Returns: A list of dictionaries, with each dictionary being a specific class at Notre Dame
       Each dictionary has the same keys and gives the same information for each class
    """
    url = 'https://class-search.nd.edu/reg/srch/ClassSearchServlet'

    # stores data for the post request
    FormData = {'TERM': term, 'SUBJ': subj, 'CREDIT':credit, 'ATTR':Attr,
                'DIVS':divs, 'CAMPUS' : campus}

    response = requests.post(url, data=FormData)
    soup = BeautifulSoup(response.content, "lxml")
    ClassTable = soup.find_all('table', {'id':'resulttable'})

    # If no classes listed on class search, return an empty []
    if len(ClassTable) == 0:
        return []
    else:
        ClassTable = ClassTable[0].find_all('tr')

        Headers = ClassTable[0].find_all('th')

        # Class_Headers stores the column headers for the class data
        Class_Headers = []
        for header in Headers:
            Class_Headers.append(str(header.text))

        Classes = ClassTable[1:]

        Classlist = []

        # Temporary counting variable
        Num_Classes = 0
        URLS = []
        for Class in Classes:
            Classlist.append({})
            Info = Class.find_all('td')
            URLS.append([])
            for i, header in zip(Info, Class_Headers):
                url = ''
                url = i.find_all('a')
                if url:
                    URLS[Num_Classes].append(url)
                try:
                    if header == 'Instructor':
                        names = i.find_all('a')
                        professors = []
                        for name in names:
                            try:
                                x = CleanUpString(str(name.text).replace('\t', ''))
                                if x[-1] == ' ':
                                    x = x[:-1]
                                professors.append(x)
                            except:
                                x = CleanUpString(name.text.replace('\t', ''))
                                if x[-1] == ' ':
                                    x = x[:-1]
                                professors.append(x)
                            Classlist[Num_Classes][header] = professors
                    else:
                        Classlist[Num_Classes][header] = CleanUpString(str(i.text).replace('\t', ''))
                except UnicodeEncodeError:
                    Classlist[Num_Classes][header] = CleanUpString(i.text.replace('\t', ''))
            Classlist[Num_Classes]['Campus'] = campus
            Classlist[Num_Classes]['Term'] = term
            Classlist[Num_Classes]['Attribute'] = Attr
            Num_Classes += 1

        # Reassign temporary counting variable
        Num_Classes = 0
        for url in URLS:
            ClassUrlData = url[0]
            ClassDescriptionUrl = ClassUrlData[0].get('href')
            BookStoreUrlData = ClassUrlData[1]
            BookStoreUrl = BookStoreUrlData.get('href')
            ClassUrlExtension = CleanUpString(ClassDescriptionUrl.split("'")[1])

            baseUrl = 'https://class-search.nd.edu/reg/srch/'
            Classlist[Num_Classes]['Course_Info'] = baseUrl + ClassUrlExtension
            Classlist[Num_Classes]['View_Books'] = BookStoreUrl

            # Some classes have no teacher yet announced.
            # If they do not have a teacher, then len(url) == 1.
            # If the teacher is announced, len(url) == 2
            if len(url) == 2:
                url_data = []
                for i in range(len(url[1])):
                    InstructorUrlData = url[1][i].get('href')
                    TeacherUrlExtension = CleanUpString(InstructorUrlData.split("'")[1])
                    url_data.append(TeacherUrlExtension)
                baseUrl = 'https://class-search.nd.edu/reg/srch/'
                Classlist[Num_Classes]['Teacher_Info'] = [(baseUrl + i) for i in url_data]
            else:
                Classlist[Num_Classes]['Teacher_Info'] = 'NONE'
            Num_Classes += 1

        # Clean up Course - sec in Classlist
        for i in Classlist:
            i["Title"] = i["Title"].replace('/', ' and ')
            i["Title"] = i["Title"].replace("?", "")
            i['Course - Sec'] = i['Course - Sec'].replace('*View Books', '').replace('View Books', '')

        return Classlist

def GetClassDescriptionAndAll(CRN, Term):
    """Gets the class description, the course prerequisites, and the course corequisites
    Input: a url of a class specific page
    returns: A list with the course description, a string that reveals the contents of the rest of the list,
            the prerequisites (if any), and corequisites (if a
            String options: 'Both', 'Neither', 'Prerequisote Only', or 'Corequisite Only'
    """
    url = 'https://class-search.nd.edu/reg/srch/ClassSearchServlet?CRN=' + str(CRN) + '&TERM=' + str(Term)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    # Get department, section, and course number for textbook scrapping
    Course_Info = soup.find_all("th", attrs = {"class":"ddlabel"})[0]
    course_section = CleanUpString(Course_Info.text).replace(u'\xa0','')
    Department_Index = 0
    while not course_section[Department_Index].isnumeric():
        Department_Index += 1
    Department = str(course_section[0:Department_Index])
    Course_Num_Index = Department_Index
    while course_section[Course_Num_Index] != '-':
        Course_Num_Index+= 1
    Course_Num = str(course_section[Department_Index:Course_Num_Index])
    section = str(course_section.split("Section")[1][0:2])

    Data = soup.find_all('td')[2].text.split('Restrictions:')
    DataText = Data[0]
    Restrictions = CleanUpString(Data[1]).replace(u"\xa0", '').split("Course Attributes")[0].split("Cannot")[0].split(".syllabus")[0]
    try:
        # Catch Department_Index error if class has no attributes
        AttributeText = CleanUpString(Data[1].split("Course Attributes:")[1].split(".syllabus")[0])
        AttributeText = [str(i) for i in AttributeText.split(u"\xa0")]
    except IndexError:
        AttributeText = []

    Course_Description = DataText.split('Associated Term:')[0]

    EnrollmentData = soup.find_all("table", {"class":"datadisplaytable"})
    if len(EnrollmentData) == 4:
        Registration = EnrollmentData[1].text
        CrossListed = EnrollmentData[2].text
    elif len(EnrollmentData) == 3:
        Registration = EnrollmentData[1].text
        CrossListed = None

    if 'Prerequisites' in DataText:
        if 'Corequisites' in DataText:
            Temporary = DataText.split('Prerequisites:')[1].split('Corequisites:')
            Prerequisites = CleanUpString(str(Temporary[0].replace(u'\xa0', '')))
            Corequisites = CleanUpString(str(Temporary[1].replace(u'\xa0', '')))
            return [Course_Description, 'Both', Prerequisites, Corequisites, AttributeText, Restrictions, Registration, CrossListed, Department, Course_Num, section]
        else:
            Prerequisites = CleanUpString(DataText.split('Prerequisites:')[1].replace(u'\xa0', ''))
            return [Course_Description, 'Prerequisite Only', Prerequisites, AttributeText, Restrictions, Registration, CrossListed, Department, Course_Num, section]
    elif 'Corequisites' in DataText:
            Corequisites = CleanUpString(DataText.split('Corequisites:')[1].replace(u'\xa0', ''))
            return [Course_Description, 'Corequisite Only', Corequisites, AttributeText, Restrictions, Registration, CrossListed, Department, Course_Num, section]
    else:
        return [Course_Description, 'Neither', AttributeText, Restrictions, Registration, CrossListed, Department, Course_Num, section]




def Sort_dict(data, isTerms):
    """ Takes the keys in a dictionary, sorts them by their corresponding value, and then puts
    the keys in an ordered list. For the Terms, want highest numbers first, so need to reverse the keys list"""

    if isTerms:
        keys = sorted(data, key=data.get)
        keys.reverse()
        return keys
    else:
        return sorted(data)

def GetSubjectsInDepartments():
    Colleges = ['College of Arts & Letters', 'College of Engineering', 'College of Science', 'Mendoza College of Business', 'First Year of Studies', 'The Law School', "St. Mary's College", 'Other', 'School of Architecture']
    Colleges_with_deparments = []
    for i in Colleges:
        Colleges_with_deparments.append([])
    f = open('SubjectsInColleges.txt', 'r')
    department_Department_Index = 0
    for line in f.read().split('\n'):
        if line == '-----':
            department_Department_Index += 1
        else:
            if line == '':
                continue
            else:
                Colleges_with_deparments[department_Department_Index].append(line)
    sorted_Colleges_with_deparments = []
    for college in Colleges_with_deparments:
        new_college = [college[0]] + sorted(college[1:])
        sorted_Colleges_with_deparments.append(new_college)
    f.close()
    return sorted_Colleges_with_deparments

def GetAllProfessors():
    f = open('TeacherList.txt', 'r')
    Professors = {}

    line = f.readline()
    while line != '':
        name = line.split('>')[-1].replace('\n', '')

        # get rid of any trailing spaces
        while name[-1] == ' ':
            name = name[:-1]
        # get last name
        last_name = CleanUpString(name.split(',')[0])

        # get list of all middle and first names
        surname = [CleanUpString(string) for string in name.split(',')[1].split(' ') if string != ' ' and string != '']
        surname_combinations = []
        for i in range(1, len(surname)+1):
            surname_combinations.append(' '.join(surname[0:i]))
        name_combinations = [last_name + ', ' + surname_option for surname_option in surname_combinations]
        ID = CleanUpString(line.split('"')[1])
        for i in name_combinations:
            Professors[i] = ID
        line = f.readline()
    return Professors

def GetAllProfessorDepartments():
    f = open('ProfessorDepartments.txt', 'r')
    line = f.readline()
    ProfDepartments = {}
    while line != '':
        ID = CleanUpString(line.split('; Departments:')[0])
        Department = CleanUpString(line.split('; Departments:')[1].replace('\n', ''))
        if ID in ProfDepartments:
            ProfDepartments[ID].append(Department)
        else:
            ProfDepartments[ID] = [Department]
        line = f.readline()
    f.close()
    return ProfDepartments

def GetCoursesTaught(Prof_ID):
    url = 'https://class-search.nd.edu/reg/srch/InstructorClassesServlet?TERM=' + GetCurrentSemester() +'&P=' + str(Prof_ID)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    rows = soup.find_all('tr')[2:]
    CoursesTaught = []
    for course in rows:
        # gives string that specifies url extension for each course
        url_data = str(course.find_all('a')[0]).split("'")[1].split('P=')[0].replace('&amp;', '')
        url_data = url_data.split('CRN=')[1].split('TERM=')
        CoursesTaught.append(course.text.split('\n')[1:-1] + url_data)
    for course in CoursesTaught:
            course[2] = course[2].replace('/', ' and ')
            course[2] = course[2].replace('?', '')
            temp = []
            for letter in course[0]:
                if letter.isdigit():
                    break
                else:
                    temp.append(letter)
            course.append(''.join(temp))
    return CoursesTaught
def Professors_No_Repeats():
    f = open('TeacherList.txt', 'r')
    Professors = {}

    line = f.readline()
    while line != '':
        name = line.split('>')[-1].replace('\n', '')

        # get rid of any trailing spaces
        while name[-1] == ' ':
            name = name[:-1]
        # get last name
        last_name = CleanUpString(name.split(',')[0])

        # get list of all middle and first names
        surname = [CleanUpString(string) for string in name.split(',')[1].split(' ') if string != ' ' and string != '']
        surname_combinations = []
        for i in range(1, len(surname)+1):
            surname_combinations.append(' '.join(surname[0:i]))
        name_combinations = [last_name + ', ' + surname_option for surname_option in surname_combinations]
        ID = CleanUpString(line.split('"')[1])
        for i in name_combinations:
            Professors[ID] = i
        line = f.readline()
    return sorted(Professors.values())
