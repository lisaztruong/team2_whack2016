$(".button-collapse").sideNav();
$('.modal-trigger').leanModal();

function DefaultSelect(element_ID,value){
	var option = document.getElementById(element_ID);
	for (var i = 0; i < option.options.length; i = i + 1){
		if (option.item(i).value == value){
			option.selectedIndex = i;
		}
	}
}

function QuickSearch(){
	var selected_attribute = document.getElementById('QuickSearch').value;
	location.href = ''.concat('/class_search/quick-search=', selected_attribute);
}

function SearchClasses(DataPresent){
	if (DataPresent){
		var term_element = document.getElementById('TermOptionsTwo');
		var term = term_element.options[term_element.selectedIndex].value;
		var subject_element = document.getElementById('SubjectOptionsTwo');
		var subject = subject_element.options[subject_element.selectedIndex].value;
		for (var i = 0; i < subject_element.options.length; i++){
			if (subject_element.options[i].selected == true){
				alert(subject_element.options[i].value)
			}
		}
		var credit_element = document.getElementById('CreditsOptionsTwo');
		var credit = credit_element[credit_element.selectedIndex].value;

		var attribute_element = document.getElementById('AttributeOptionsTwo');
		var attribute = attribute_element.options[attribute_element.selectedIndex].value;
		var division_element = document.getElementById('DivisionOptionsTwo');
		var division = division_element.options[division_element.selectedIndex].value;
		var campus_element = document.getElementById('CampusOptionsTwo');
		var campus = campus_element.options[campus_element.selectedIndex].value;
		var url = ''.concat('www.ndreviews.com/class_search/Term=', term,'/Subject=',subject,'/Credit=',credit, '/Attr=', attribute, '/Division=' , division, '/Campus=', campus);
		location.replace(url)
	}
	else {
		var term_element = document.getElementById('TermOptions');
		var term = term_element.options[term_element.selectedIndex].value;
		var subject_element = document.getElementById('SubjectOptions');
		var subject = subject_element.options[subject_element.selectedIndex].value;
		var credit_element = document.getElementById('CreditsOptions');
		var credit = credit_element[credit_element.selectedIndex].value;

		var attribute_element = document.getElementById('AttributeOptions');
		var attribute = attribute_element.options[attribute_element.selectedIndex].value;
		var division_element = document.getElementById('DivisionOptions');
		var division = division_element.options[division_element.selectedIndex].value;
		var campus_element = document.getElementById('CampusOptions');
		var campus = campus_element.options[campus_element.selectedIndex].value;
		var url = ''.concat('www.ndreviews.com/class_search/Term=', term,'/Subject=',subject,'/Credit=',credit, '/Attr=', attribute, '/Division=' , division, '/Campus=', campus);
		location.replace(url)
	}
}

function SearchInstructorByCollege() {
	var instr_element = document.getElementById('College');
	var instr = instr_element.options[instr_element.selectedIndex].value;
	var url = ''.concat('www.ndreviews.com/InstructorByCollege/', instr);
	document.getElementById('TeacherInfoFrame').src = url
}

function SearchInstructorByDepartment(){
	var instr_element = document.getElementById('Department');
	var instr = instr_element.options[instr_element.selectedIndex].value;
	var url = ''.concat('../Department/', instr);
	document.getElementById('TeacherInfoFrame').src = url
}

function GoToDepartment(element) {
	var department = element.options[element.selectedIndex].value;
	location.href = "".concat("../Department/" + department);
}

function GoToURL(element){
	var course = element.options[element.selectedIndex].value;
	location.href = "".concat("../class_info/", course);
}

function CreateRatingsSelect(elementID){
	element = document.getElementById(elementID);
	var opt = document.createElement('option')
	opt.value = '-- select an option --';
	opt.innerHTML = '-- select an option --';
	element.appendChild(opt);
	for (var i = 0; i<=10; i++){
    		var opt = document.createElement('option');
   		opt.value = i;
  		opt.innerHTML = i;
  		element.appendChild(opt);
	}
}

function CheckSellerInfoBeforeSubmitting(){

	if (document.getElementById('TextbookName').value == '' || document.getElementById('TextbookName').value == ' '){
		alert("Please fill out all fields")
		return false;
	}
	if (document.getElementById('price').value == '' || document.getElementById('price').value == ' '){
		alert("Please fill out all fields")
		return false;
	}
	if (document.getElementById('course').value == '' || document.getElementById('course').value == ' '){
		alert("Please fill out all fields")
		return false;
	}
	if (document.getElementById('Email').value == '' || document.getElementById('Email').value == ' '){
		alert("Please fill out all fields")
		return false;
	}
	if (document.getElementById('TextbookDescription').value == '' || document.getElementById('TextbookDescription').value == ' '){
		alert("Please fill out all fields")
		return false;
	}
	if (document.getElementById('DepartmentSelect').value == '' ){
		alert("Please fill out all fields")
		return false;
	}
	return true;
}

function Check_Buyer_info(){
	if (document.getElementById('name').value == '' || document.getElementById('name').value == ' '){
		alert("Please fill out all fields")
		return false;
	}
	if (document.getElementById('email').value == '' || document.getElementById('email').value == ' '){
		alert("Please fill out all fields")
		return false;
	}
	if (document.getElementById('message').value == '' || document.getElementById('message').value == ' '){
		alert("Please fill out all fields")
		return false;
	}
	return true;
}

function CheckBeforeSubmitting(){
	alert('fsd');
	var CourseElement = document.getElementById('CoursesTaughtID');
	var course = CourseElement.options[CourseElement.selectedIndex].value;
	if (course === 'No course choosen'){
		alert('Please fill out all required forms');
		return true;
	}
	return false;
}
