var samplecollegesDict = {
  wellesley: {name: "Wellesley", overall: '6.5/10', physicalrating: '4/10', academicsupport: '6/10', resources: '8/10'},
  mit: {name: "MIT", overall: '9/10', physicalrating: '8/10', academicsupport: '10/10', resources: '9/10'},
  olin: {name: "Olin", overall: '6/10', physicalrating: '4/10', academicsupport: '6/10', resources: '8/10'},
  babson: {name: "Babson", overall: '7/10', physicalrating: '7/10', academicsupport: '6/10', resources: '8/10'},
  northeastern:{name: "Northeastern", overall: '5/10', physicalrating: '4/10', academicsupport: '6/10', resources: '5/10'},
  tufts: {name: "Tufts", overall: '9/10', physicalrating: '8/10', academicsupport: '10/10', resources: '9/10'}
};

var samplecolleges = [{name: "Wellesley", overall: '6.5/10', physicalrating: '4/10', academicsupport: '6/10', resources: '8/10'},
  {name: "MIT", overall: '9/10', physicalrating: '8/10', academicsupport: '10/10', resources: '9/10'},
  {name: "Olin", overall: '6/10', physicalrating: '4/10', academicsupport: '6/10', resources: '8/10'},
  {name: "Babson", overall: '7/10', physicalrating: '7/10', academicsupport: '6/10', resources: '8/10'},
  {name: "Northeastern", overall: '5/10', physicalrating: '4/10', academicsupport: '6/10', resources: '5/10'},
  {name: "Tufts", overall: '9/10', physicalrating: '8/10', academicsupport: '10/10', resources: '9/10'}]


function setFeaturedCollege(college){
	var featuredName = document.getElementById('featNAME');
	var featuredOverall = document.getElementById('featCLGOVRL');
	var featuredCLGPHYS = document.getElementById('featCLGPHYS');
	var featuredCLGAC = document.getElementById('featCLGAC');
	var featuredCLGRES = document.getElementById('featCLGRES');

	featuredName.innerHTML = college.name;
	featuredOverall.innerHTML = college.overall;
	featuredCLGPHYS.innerHTML = college.physicalrating;
	featuredCLGAC.innerHTML = college.academicsupport;
	featuredCLGRES.innerHTML = college.resources;
};

function newFeaturedCollege() {
	//Gets current featured college
	//sets the object variables to that of one of the sample
	//while (ranIdx == 0){
		var ranidx = Math.abs(Math.floor((Math.random() * 10) - 4));
	//}
	console.log('index : ' + ranidx);
	var featuredCollege = samplecolleges[ranidx];
	console.log('name : ' + featuredCollege.name);

	setFeaturedCollege(featuredCollege);
};

function addCollegeTB(college){
	var table = document.getElementById('recent');
	var row = table.insertRow();
	var name = row.insertCell();
	var overall = row.insertCell();
	var phys = row.insertCell();
	var ac = row.insertCell();
	var res = row.insertCell();


	name.innerHTML = (college.name);
	overall.innerHTML = (college.overall);
	phys.innerHTML = (college.physicalrating);
	ac.innerHTML = (college.academicsupport);
	res.innerHTML = (college.resources);
}

function makeTable(){
 console.log('make table opened');
	for (i = 0; i < 6; i++){
		console.log('adding ' + samplecolleges[i].name)
		addCollegeTB(samplecolleges[i]);
	}
}

dialog = $( "#dialog-form" ).dialog({
      autoOpen: false,
      height: 400,
      width: 350,
      modal: true,
      /*buttons: {
        "New Review": addUser,
        Cancel: function() {
          dialog.dialog( "close" );
        }
      },*/
      close: function() {
        form[ 0 ].reset();
        allFields.removeClass( "ui-state-error" );
      }
    });
 
    form = dialog.find( "form" ).on( "submit", function( event ) {
      event.preventDefault();
      //addUser();
    });
 
    $( "#newReviewNAV" ).button().on( "click", function() {
      dialog.dialog( "open" );
    });



newFeaturedCollege();
makeTable();

