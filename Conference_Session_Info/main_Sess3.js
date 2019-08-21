var map, image1, image2; 
require([
"esri/map", "esri/dijit/Search", "esri/layers/FeatureLayer", "esri/layers/GraphicsLayer", "esri/layers/ArcGISDynamicMapServiceLayer", "esri/geometry/webMercatorUtils",
"esri/dijit/Popup", "esri/dijit/PopupTemplate", "esri/tasks/query", "esri/tasks/QueryTask", "esri/geometry/Circle", "esri/arcgis/utils", "esri/dijit/LayerList", "esri/tasks/GeometryService",
"esri/graphic", "esri/InfoTemplate", "esri/renderers/UniqueValueRenderer", "esri/symbols/SimpleMarkerSymbol", "esri/SnappingManager", "esri/dijit/editing/Editor", "esri/urlUtils",
"esri/symbols/SimpleLineSymbol", "esri/symbols/SimpleFillSymbol", "esri/renderers/SimpleRenderer", "esri/symbols/PictureMarkerSymbol", "esri/layers/LabelClass", "esri/Color",
"esri/config", "esri/Color", "dojo/dom", "esri/dijit/Scalebar", "dojo/_base/array", "esri/arcgis/utils", "esri/request", "esri/symbols/TextSymbol",
"dojo/parser", "dojo/dom-class", "dojo/dom-construct", "dojo/_base/array", "dijit/form/Button", "esri/lang", "dijit/TooltipDialog", "dijit/popup",
"esri/geometry/Point", "esri/geometry/Extent", "esri/tasks/AddressCandidate", "dojo/_base/connect", "dojo/on", "dojo/domReady!"
], function(
Map, Search, FeatureLayer, GraphicsLayer, ArcGISDynamicMapServiceLayer, webMercatorUtils,
Popup, PopupTemplate, Query, QueryTask, Circle, utils, LayerList, GeometryService,
Graphic, InfoTemplate, UniqueValueRenderer, SimpleMarkerSymbol, SnappingManager, Editor, urlUtils,
SimpleLineSymbol, SimpleFillSymbol, SimpleRenderer, PictureMarkerSymbol, LabelClass, Color,
esriConfig, Color, dom, Scalebar, arrayUtils, arcgisUtils, esriRequest, TextSymbol,
parser, domClass, domConstruct, array, Button, esriLand, TooltipDialog, dijitPopup,
Point, Extent, AddressCandidate, connect, on
) { 
var fill = new SimpleFillSymbol("solid", null, new Color("#A4CE67"));
var popup = new Popup({
	fillSymbol: fill,
	titleInBody: false
}, domConstruct.create("div"));

//load the map
map = new Map("map", { 
  basemap: "streets", // topo
  center: [-84.3950, 33.7603],  // -77.304, 38.853
  zoom: 17,
  slider: true, 
  sliderPosition: "bottom-left",
  showLabels : true //
  //infoWindow: popup
});

// Session Hall list
var sessHallx = [];
var infoTemplate = new InfoTemplate();  // "<img src='"+images/WestMeetingWing.png+"'>"
infoTemplate.setTitle("Map of ${Area}");
//
infoTemplate.setContent("<b> Meeting Wing <b>");  // "<img src='" images\EastMeetingWing.png "'>"  // "images\EastMeetingWing.png"

//Create a scale bar
var scalebar = new Scalebar({
  map: map,
  // "dual" displays both miles and kilmometers // use "metric" for kilometers, // "english" is the default, which displays miles       
  scalebarUnit: "dual",
  showLabels : true //
});		

//Add search widget
 var search = new Search({
	enableButtonMode: true, //this enables the search widget to display as a single button
	enableLabel: false,
	enableInfoWindow: true,
	showInfoWindowOnSelect: false,
	zoomScale: 4000000,
	map: map
 }, "search");
 var sources = search.get("sources");
 //Push the sources used to search, by default the ArcGIS Online World geocoder is included. In addition there is a feature layer of US congressional districts. The districts search is set up to find the "DISTRICTID". Also, a feature layer of senator information is set up to find based on the senator name. 
 sources.push({
	featureLayer: new FeatureLayer("https://gis.iafc.org/arcgis/rest/services/CountyAndState/MapServer/0"),
	searchFields: ["NAME"],
	displayField: "NAME",
	exactMatch: false,
	outFields: ["NAME"],
	name: "States",
	placeholder: "Virginia",
	maxResults: 6,
	maxSuggestions: 6,
	//Create an InfoTemplate and include three fields
	infoTemplate: new InfoTemplate("States","State: ${NAME}</br>"), //"Zip Codes",
	enableSuggestions: true,
	minCharacters: 0
 });
 sources.push({
	featureLayer: new FeatureLayer("https://atlas.resources.ca.gov/arcgis/rest/services/Location/ZipCodes/MapServer/0"),
	searchFields: ["ZCTA5CE"],
	displayField: "ZCTA5CE",
	exactMatch: false,
	outFields: ["ZCTA5CE"],
	name: "Zips",
	placeholder: "22033",
	maxResults: 6,
	maxSuggestions: 6,
	//Create an InfoTemplate and include three fields
	infoTemplate: new InfoTemplate("Zips","Zip: ${ZCTA5CE}</br>"), //"Zip Codes",
	enableSuggestions: true,
	minCharacters: 0
 });
 //Set the sources above to the search widget
 search.set("sources", sources);
 search.startup();

var charConvCtr = new FeatureLayer("https://gis.iafc.org/arcgis/rest/services/MembershipMarketing/MembershipPackage_Unsecured/MapServer/7", { 
  mode: FeatureLayer.MODE_ONDEMAND,  //ONDEMAND, 
  infoTemplate: infoTemplate,
  //new InfoTemplate("Fire Hydrants:  ", "Status: ${HYDRCOND}<br> Last Update: ${LASTUPDATE}"),
  outFields: ["Area"],
  visible: true,
  opacity: 0.7,
  //showInfoWindowOnClick: true
});
var charHotels = new FeatureLayer("https://gis.iafc.org/arcgis/rest/services/MembershipMarketing/MembershipPackage_Unsecured/MapServer/10", { 
  infoTemplate: new InfoTemplate("Hotel:  ", "Hotel: ${Name}<br> Address: ${Address} <br>"),
  //new InfoTemplate("Fire Hydrants:  ", "Status: ${HYDRCOND}<br> Last Update: ${LASTUPDATE}"),
  outFields: ["Name", "Address", "City", "State", "Zip"],
  mode: FeatureLayer.MODE_ONDEMAND,  //ONDEMAND, 
  visible: true,
  opacity: 0.7,
  showInfoWindowOnClick: true
});
// load image for each West and East Meeting halls
var sessionTable = new FeatureLayer("https://gis.iafc.org/arcgis/rest/services/MembershipMarketing/MarketingMembership_Unsecured/MapServer/11", { 
  mode: FeatureLayer.MODE_ONDEMAND,  //SNAPSHOT, 
  //infoTemplate: new InfoTemplate("Fire Hydrants:  ", "Status: ${HYDRCOND}<br> Last Update: ${LASTUPDATE}"),
  //outFields: ["OBJECTID", "Session_Title_1", "Room_Name_1", "Session_Date_1", "Session_Start_Time_1", "Session_End_Time_1"]
  outFields: ["OBJECTID", "Event_Title", "Starts_OnDate", "StartsTime", "EndsTime", "Room"]
  //showInfoWindowOnClick: true
});
var hifldPnts = new FeatureLayer("https://gis.iafc.org/arcgis/rest/services/Editable_Layers/EditableLyrPackage/FeatureServer/0", {
  infoTemplate: new InfoTemplate("Emergency Services Repository:  ", "Department: ${NAME}<br> Address: ${ADDRESS}, ${CITY}, ${STATE}, ${ZIP} <br>"+
  "Department Description: ${NAICSDESCR}<br> Total Personnel: ${TOTALPERS} <br> Number of Stations: ${NBR_STA} <br> Phone: ${TELEPHONE}"), //<br> Email: ${Email_Adx}
  mode: FeatureLayer.MODE_ONDEMAND, 
  outFields: ["NAME"],
  // ["OBJECTID", "OWNER", "NBR_STA", "NAME", "ADDRESS", "CITY", "STATE", "ZIP", "NAICSDESCR", "NAICSCODE", "TOTALPERS", "TELEPHONE", 'CONTACT_TITLE', 'CONTACT_FIRST_NAME', 'CONTACT_LAST_NAME'], //, "Email_Adx"]
  visible: true,
  //id: "Emergency Departments"
  //showInfoWindowOnClick: false
});

// selection symbol used to draw the selected points within the polygon
var symbol = new SimpleMarkerSymbol(
  SimpleMarkerSymbol.STYLE_CIRCLE, 
  5, 
  new SimpleLineSymbol(
	SimpleLineSymbol.STYLE_SOLID, 
	new Color([36, 36, 36, 1]), //   168, 56, 0
	1  //0.4
  ),
  new Color([230, 0, 169, 0.8])  //173, 173, 173    0, 92, 230
);
// Create graphic symbol for the selected polygon.
var polySymb = new SimpleFillSymbol(
  SimpleFillSymbol.STYLE_NULL,
  new SimpleLineSymbol(
	SimpleLineSymbol.STYLE_SHORTDASHDOT,
	new Color([230, 0, 169]),  //0, 92, 230
	2
  ), new Color([0, 92, 230, 0.4]) // 168, 56, 0, 0.4
);

// symbols for fire incidents
symbolFire = new PictureMarkerSymbol({ "url" : 'http://static.arcgis.com/images/Symbols/Animated/EnlargeRotatingRedMarkerSymbol.png', "height" : "10", "width" : "10" }); 
symbolHotel = new PictureMarkerSymbol({ "url" : ' http://static.arcgis.com/images/Symbols/Transportation/esriBusinessMarker_74.png', "height" : "14", "width" : "14" }); 
symbolFS = new PictureMarkerSymbol({ "url" : 'http://static.arcgis.com/images/Symbols/SafetyHealth/FireStation.png', "height" : "12", "width" : "12" }); 

// function to create total count the FF types for the depts. from three fields and pass it to the renderer to symbolized by class. 
function addStaff(feature){
  // a number field representing total population
  var fulltimestaff = feature.attributes.fulltimestaff; 
  var volstaff = feature.attributes.volstaff; 
  var parttimestaff = feature.attributes.parttimestaff; 
  // var used to classify features by population
  return fulltimestaff + volstaff + parttimestaff;
}
//

//create renderer
var renderer = new UniqueValueRenderer(symbolFS, "NAME"); //first parameter is default symbol
var renderer2 = new UniqueValueRenderer(symbolHotel, "Name"); //first parameter is default symbol
//add symbol for each possible value 
hifldPnts.setRenderer(renderer);  // **
charHotels.setRenderer(renderer2);
// create a text symbol to define the style of labels
var hotelsColor = new Color("#666");
var hotelsLabel = new TextSymbol().setColor(hotelsColor);
hotelsLabel.font.setSize("9pt");
hotelsLabel.font.setFamily("arial");
//this is the very least of what should be set within the JSON  
var json = {
  "labelExpressionInfo": {"value": "{Name_Label}"},
  "labelPlacement":"above-center"
};

//create instance of LabelClass (note: multiple LabelClasses can be passed in as an array)
var labelClass = new LabelClass(json);
labelClass.symbol = hotelsLabel; // symbol also can be set in LabelClass' json
charHotels.setLabelingInfo([ labelClass ]);
map.addLayers([hifldPnts, charConvCtr, sessionTable, charHotels]); //graphicslayer, epaSites, epaSites2, zipLayer

// capture text of selected session halls
sessHall = []; 
// reset the infoTemplate  - For user click on the meeting hall return a map of the rooms in hall. 
// close the dialog when the mouse leaves the highlight graphic
on(charConvCtr, "click", function(evt){  // "click"
	sessHall = [];
	map.graphics.clear();  //console.log(evt.graphic.attributes.Area);
	sessHall.push(evt.graphic.attributes.Area);
	//console.log(sessHall[0]);
	changeInfoTemplate();
}); 
function changeInfoTemplate() {
	console.log("changed");
	map.infoWindow.hide();
	//map.infoWindow.resize(300, 400);
	var templateContent = "";  
	if (sessHall[0] == "West Meeting Wing"){  // data.Area, "   <img src='" + result + "'>"   style="width:304px;height:228px;
		templateContent = "<img src=   images/WestMeetingWing.png   >";  // "   <img src='"images/WestMeetingWing.png"'>"   "images/WestMeetingWing.png"
	} else if (sessHall[0] == "Richardson Ballroom") {
		templateContent = "<img src=   images/RichardsonBallroom.png   >";  // "images/EastMeetingWing.png"  -- 
	} else {
		templateContent = "<img src=   images/EastMeetingWing.png   >";  // "images/EastMeetingWing.png"  -- 
	}
    charConvCtr.infoTemplate.setContent(templateContent);
	map.infoWindow.resize(500, 600);
}

// Below are time functions to either convert time to total seconds or format time in a spec. way. 
var myDays= ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
//window.startTime = function startTime(){	
function startTime(){	
    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    var s = today.getSeconds();
	var d = today.getDay();
    m = checkTime(m);
    s = checkTime(s);
	if (h >= 13){ h = h - 12 }  // Convert 24 hour time to singe digits use with AM PM function  
    //document.getElementById('time').innerHTML = myDays[d] + " - " + h + ":" + m + ampmTime();  // datetime[1] + ":" datetime[2] + datetime[4];
	//console.log(myDays[d], h, m, s, ampmTime());  // Tuesday 10 34 19 AM
	//var min5 = m.slice(-1);
    //if (min5 == "5"){ refresh(); } 
	//alert("Page was Refreshed!");
	return [myDays[d], h, m, s, ampmTime()];  
}

// get the day from time, formatted: Day, Month, Day#, Year. 
var myMonths= ["January","February","March","April","May","June","July","August","September","October","November","December","January"];
window.startDay = function startDay(){	
	// Additions to func.  var secondsX = Math.round(new Date() / 1000); // seconds since the start of time
    var today = new Date();
    var d = today.getDay();
    var m = today.getMonth();
    var y = today.getFullYear();
	var dOfMonth = today.getUTCDate();
	//if (h >= 13){ h = h - 12 }  // Convert 24 hour time to singe digits use with AM PM function  //return [myDays[d], myMonths[m], dOfMonth, y]; // ["Monday", "April", 3, 2017]
	//return myDays[d] +", "+ myMonths[m] +" "+ dOfMonth +", "+ y  // .toString  // dateday=Thursday, July 12, 2018
	return myDays[d] 
	//console.log(y.toString);
}

// add leading zero to single digit times. 
function checkTime(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
    return i;
}
function ampmTime(){  // return AM or PM to 24 time
	var today = new Date();
	var h = today.getHours();
	if (h >= 1 && h <= 11){
		return "AM";
	} else{ return "PM"; }
}
// convert 3:15pm format to total seconds for session status update
function convTimeToSec(time){  // str.slice(1, 5);  Don't need to feed func. an indexed item, it's indexed in the call. 
	var hr = time.slice(0, 2); // first two char.
	//console.log(time.length)
	if (time.length == 7) { var min = time.slice(2, 4); }  // change length from 6 to 7 when changed session lists. **
	else if (time.length == 8) { var min = time.slice(3, 5); }
	//var min = time.slice(-4,-2);  // 3rd and 4th char. from the right. 
	var ampm = time.slice(-2);
	if (hr.slice(1, 2) == ":"){ // if the time hour position is only one digit
		hr = time.slice(0, 1);
	}
	if (ampm == "PM" && hr != "12"){
		hr = Number(hr) + 12 
	} else{ hr = Number(hr)}
	//console.log(min);
	totalSecs = (hr * 60 * 60) + ( Number(min) * 60 )
	return totalSecs  //console.log(totalSecs)
}

// function indicate Session Status in table
var datetime = startTime(); // ["Friday", 16, "06", "08", "AM"]
var dateday = startDay(); 
function sessionStatus(chartInfo){  
	var Status = [];  // string.charAt(index) and num.toString(); and var keys = Object.keys( obj );
	var statusType = ["Next", "Now", "Done", "Later Today"]; //features[0].attributes["REGISTRY_ID"]
	var curTime = datetime[1] +":"+ datetime[2]+" "+datetime[4] // current time formated as 10:12 AM etc. -- .toString
	//console.log( "Tuesday, April 4, 2017" +" = "+ dateday);   

	//if(chartInfo[3] == startDay[0] +", "+ startDay[1] +" "+ startDay[2].toString +", "+ startDay[3].toString && // for final with July dates
	if( convTimeToSec(chartInfo[4]) <= convTimeToSec(curTime) && convTimeToSec(chartInfo[5]) >= convTimeToSec(curTime) ) { // sess. date=chartInfo[3] - Now: sTime <= curTime & eTime >= curTime (might need to subtract one second)
		return statusType[1];  // 
	} // changed from 1 hr - 3600 to 1.5 hr 
	else if( (convTimeToSec(chartInfo[4]) - convTimeToSec(curTime)) <= 5400 && convTimeToSec(chartInfo[4]) >= convTimeToSec(curTime) ) { // Next: startT - currentT <= 1.5hr && sTime >= cT
		return statusType[0]
	}
	else if( convTimeToSec(chartInfo[5]) <= convTimeToSec(curTime) ) { 
		return statusType[2]
	}
	else{ return statusType[3]; }
}

//call Street View with double click
map.on("dbl-click", function(evt){ 
  map.disableDoubleClickZoom(true);
  map.reposition();
  // mapPoint coordinates are in Map Units, need to be converted to geographic coordinates 4832
  var mp = webMercatorUtils.webMercatorToGeographic(evt.mapPoint);  // map.infoWindow.setContent("lat/lon : " + evt.mapPoint.y + ", " + evt.mapPoint.x);
  //alert("lat/lon : " + mp.y.toFixed(3) + ", " + mp.x.toFixed(3));
  initPano(mp.y.toFixed(3), mp.x.toFixed(3));
}); 

var gl = new GraphicsLayer();
//  refresh the page every 5 mins.
function refresh() {
	//if (dateTime[2].slice(-1) == "5"){ }
	window.location.reload(true); 
}
setInterval(refresh, 300000); // refresh every 5 minutes - 300000
// current time from browser to document. 
(function () {
  var DayTimeElement = document.getElementById( "DayTime" );  // "clock"
  function updateClock ( DayTime ) {
    DayTime.innerHTML = new Date().toLocaleTimeString();
  }
  setInterval(function () {
      updateClock( DayTimeElement );
  }, 1000); // refresh every second
}());

var chartInfo = [];
//
google.charts.load('current', {'packages':['table']}); // Need to load google package before use api or software
// Events: Query of all sessions for spec. day
map.on("update-end" && "extent-change", function(evt) {  // "zoom-end" &&  && "unload"  update-end, load, unload, complete
	var query = new Query();
	//query.geometry = map.extent; // evt.graphic.geometry;
	query.where = "1=1";  // query all features
	query.returnGeometry = false;
	query.outFields = ["OBJECTID", "Event_Title", "Starts_OnDate", "StartsTime", "EndsTime", "Room"]; // ["OBJECTID", "HYDRCOND", "OPERABLE", "LASTUPDATE", "EditDate"];  
	// Use query.where condition with a SQL expression to filter as shown. 
	sessionTable.selectFeatures(query, FeatureLayer.SELECTION_NEW, function(results, chartInfo) { // hifldPnts
		//console.log(results.length); 
		chartInfo = []; // remove contents of array after each call to global variable. 
		var len = results.length;
		//Function: loop session list, return list of selected features, sessions for the day, to a table for public view. 
		for (var x = 0; x < len; x++) {  // Test: one week out, subtract one week from current date.  
			var str = results[x].attributes['Starts_OnDate']; 	//console.log(str.split(",", 1).slice(0)); // .replace(20, 27)
			// convert UTC time to just day of week for script. 
			var n = new Date(str);   
			var weekday = myDays[n.getUTCDay()]
			//var dayX = str.getDay(); // convert seconds to day to compare
			console.log(weekday + " == "+ dateday) // The Str is not formated the same as dateday. **
			//console.log(str.slice(0,2)); 
			//if (str.slice(0,2) == dateday.slice(0,2)) {  // Had to slice out 1st two characters of the strings to get a match due to a bug on Thursday sessions. 
			if (weekday == dateday) {  // (weekday == dateday) - str=totalsecs & dateday=Thursday, July 12, 2018 format. Slice out 1st two char of strings to match due to bug Thursday sess. 
				multiArray(results, x, chartInfo);  // x, -- calling multiArray here populates the ChartInfo array. 
				//console.log(str.slice(0,2) +" = "+ dateday.slice(0,2));
			}
		}
		google.charts.load('current', {'packages': ['corechart'], 'callback': drawTable(chartInfo)});
		google.charts.load('current', {'packages': ['corechart'], 'callback': drawTable2(chartInfo)});
		google.charts.load('current', {'packages': ['corechart'], 'callback': drawTable3(chartInfo)});
		//google.charts.setOnLoadCallback( drawTable(chartInfo) );
		//drawChart(results);
	});	
});	

// function to build an array for each org. selected, and add it to the primary array. 
function multiArray(features, x, chartInfo){
	z = [];
	var date = new Date(features[x].attributes["Award_Date"]);
	console.log(date);
	var len = features.length;
	//if("Tuesday, April 4, 2017" == dateday) {  // Add curDay ==
	z[0] = features[x].attributes['OBJECTID'];
	z[1] = features[x].attributes['Event_Title'];
	z[2] = features[x].attributes['Room'];
	z[3] = features[x].attributes['Starts_OnDate'];
	z[4] = features[x].attributes['StartsTime']; //date.getFullYear();
	z[5] = features[x].attributes['EndsTime']; //
	z[6] = assignMeetWing(z[2])  //
	chartInfo.push(z); 
	console.log(z);
	//}  console.log(z[6]);
	return chartInfo;
	//return [chartInfo, orgAwards]
}

// Assign Session Meeting Location - add to chartInfo Array. For session info tables. 
function assignMeetWing(v){ //set up to add to chartInfo.
	var len = chartInfo.length;
	//var wmWing = [201, 202, 203, 204, 205, 206, 207, 208, 209, 210];
	//var emWing = [211, 212, 213, 214, 215, 216, 217, 218, 219];
	//var roomNum = Number(chartInfo[i][2].slice(3));
	//var All Levels = ["A115", "A117", "A130", "A131/132", "Arena", "Ballroom A1", "Ballroom A2", "Ballroom A3", "Ballroom A4",
	//"Ballroom C1", "Ballroom C2", "Ballroom C3", "Ballroom C4", "Ballroom D1", "Ballroom D2", "Ballroom D3", "Ballroom D4"]
	var Rooms = { 
	GrdLevel : ["Exhibit Hall", "A117", "A130", "A131/132", "Arena", "C140", "C142", "C143", "C144", "C146", "C148"], 
	ExhLevel : ["Ballroom A1", "Ballroom A2", "Ballroom A3", "Ballroom A4", "Ballroom C1", "Ballroom C2", "Ballroom C3", "Ballroom C4", "BallroomD2&3"],
	MezLevel : ["Arena", "Ballroom D1", "Ballroom D2", "Ballroom D3", "Ballroom D4"]
	};
	//console.log(Rooms.GrdLevel[0])
	//var roomNum = Number(v.slice(0, 3));  //console.log(v.slice(0, 3));
	var roomNum = v;  
	console.log(Rooms.GrdLevel.includes(roomNum));
	//for (var x = 0; x < len; x++){
		if (Rooms.GrdLevel.includes(roomNum)){  // ['GrdLevel']
			return "Ground Level"; // 0
		} else if (Rooms.ExhLevel.includes(roomNum)) {  // ['ExhLevel']
			return "Exhibit Hall";  // 1
			//console.log(Rooms.ExhLevel[0]); 
		} else if (Rooms.MezLevel.includes(roomNum)) {
			return "Mezzanine"; // Added for new Session list with Hotel Sessions **
		}
}
//
var numDept;
// function to collect an array based on the user input. "agencyname", "address1", "city", "state", "zip5", "Phone", "fulltimestaff", "parttimestaff", "volstaff"
function qFeatures(features) { 
  var deptName = []; 
  if (features.length > 1) { // set series of conditions to query more than one member, one member, and zero members returned. 
	for (var x = 0; x < features.length; x++) { 
	deptName = deptName + "<br />- ID: " + features[x].attributes["REGISTRY_ID"] +", Facility Name: "+ features[x].attributes["PRIMARY_NAME"] +", Address: "+ 
	features[x].attributes["LOCATION_ADDRESS"]+", Facility Type: "+ features[x].attributes["INTEREST_TYPE"]+"<br />";
	  //numDept = features.length;
	  //countyName = features[0].attributes["County"];
	  }
  } else if (features.length == 1) { 
	  var myString = "<br />- ID: " + features[0].attributes["REGISTRY_ID"] +", Facility Name: "+ features[0].attributes["PRIMARY_NAME"] +", Address: "+ 
		features[0].attributes["LOCATION_ADDRESS"]+", Facility Type: "+ features[0].attributes["INTEREST_TYPE"]+"<br />"
	  deptName.push(myString);
  } else {
	  var myStr = "<br /><b>No sites were returned from selected area.<b/>"
	  deptName.push(myStr);
  }
  return deptName; 
};

// Add Google Street View to side panel
var panorama;
//var y; //var x; 
function initPano(y, x) {
	// Note: constructed panorama objects have visible: true set by default.
	var panorama = new google.maps.StreetViewPanorama(
		document.getElementById('stView'), {
		  position: {lat: parseFloat(y), lng: parseFloat(x)},
		  pov: {heading: 0, pitch: 0},
		  zoom: 1
	});
};

function selNatdirpts(polygraphic, query, results){
  var deptArray = [];
  var poiData = qFeatures(results, deptArray);
  //r = "<b>All Departments in "+ results[0].attributes["County"]+" (Count - "+ results.length + "):</b> <br />" +poiData; //
  r = "<b> Departments</b> in <b>"+ polygraphic.attributes["STATE_ABBR"] + "</b> District <b>" + polygraphic.attributes["CD113FIPS"] // " +results.length+ "
  + ":</b><br><b> Representative:</b> "  + polygraphic.attributes["NAME"] + "<br/>" +poiData[0]; // getContent()
  //dom.byId("messages").innerHTML = r;
  //info to be inserted into the 2nd info pane.
  var tDept = qStats(results); 
  s = "<b>Depts.</b> in <b>"+ polygraphic.attributes["STATE_ABBR"] + "</b> District <b>" + polygraphic.attributes["CD113FIPS"] +":</b> " +results.length+ "<br><b> Average Pop. Served:</b> " 
  + tDept[0] + "<br><b> Volunteer Depts.:</b> " + tDept[1] + "<br><b>Combo Depts.:</b> "+tDept[2]+ "<br><b>Paid Depts.:</b> "+tDept[3]+ "<br><b>Dept. Type Not Listed:</b> "+tDept[4];
  dom.byId("messages2").innerHTML = s;
  //call the chart here after the 'data' has been generated!!
  drawChart(tDept); //
  drawTable(poiData[1])
};

// add Google pie chart for side panel
google.charts.load('current', {'packages':['corechart']});
// For Hydrant Chart
function drawChart(features) {
	var Stats = qStats(features);
	var data = google.visualization.arrayToDataTable([
	['Task', 'Hours per Day'], 
	['Assigned', Stats[0]], 
	['Completed', Stats[1]], 
	['Unassigned',  Stats[2]],
	]);
	var options = {
	  title: 'Hydrants Status Distributions',
	  titleTextStyle: {color: 'black', fontName: null, fontSize: 14, bold: true, italic: false}, //'Lato, sans-serif'
	  backgroundcolor: '#F2F2F2',
	  is3D: true,
	  chartArea:{left:10,top:30,width:'85%',height:'100%'},
	  //slices: { 0: {offset: 0.2}, },
	};
	var chart = new google.visualization.PieChart(document.getElementById('piechart'));
	chart.draw(data, options);
};

// Add Google chart/tables for side panel (for West Wing Session only) - Use the google visualization data table instead of the array to table.
function drawTable(chartInfo) { // ***results.features[i].attributes;  Show courses from table next-yellow, now-green, and done-red. 
	// var date = new Date(features[x].attributes["Award_Date"]); and ", Award Date: "+ date.getFullYear()+ "
	console.log(chartInfo);  
	var data = new google.visualization.DataTable(); 
	// add columns to table, 2st column is title. 
	data.addColumn('string', 'Status');
	data.addColumn('string', 'Title');
	data.addColumn('string', 'Room');
	data.addColumn('string', 'Start Time'); //  ** double check column type!**
	data.addColumn('string', 'End Time');  
	//data.addColumn('date', 'Last Edit Date');
	var rows = 0;
	// now add rows by iterating through the sel. orgs. in 2 dimensional array, use indexes to add data to table.  
    for (var i = 0; i < chartInfo.length; i++) { // Condition: Add sessions with status Now and Next & Ground Level only.  
		console.log(sessionStatus(chartInfo[i]) +" = Now  " + sessionStatus(chartInfo[i]) + " =  Next &" + chartInfo[i][6] +" = Ground Level");
		if ((sessionStatus(chartInfo[i]) == "Now" || sessionStatus(chartInfo[i]) == "Next") && chartInfo[i][6] == "Ground Level") {  // "Next" || 
			//console.log(sessionStatus(chartInfo[i]));
			data.addRow([sessionStatus(chartInfo[i]), chartInfo[i][1], chartInfo[i][2], chartInfo[i][4], chartInfo[i][5]], {style: 'height:6px; font-size:8px;'});  // , datetime, dateday
			rows += 1;
		} //else if (rows == 0){ // at lunch time there are not sessions id as Next or Now. This will display Later Today Sessions.
	} 	//if (rows == 0){z = "<b> Current or Upcoming Sessions - </b>"+ startDay();} else {
	z = "<b>Convention Center Ground Level Events </b>"+ startDay()  // +" - "+ datetime[1] +":"+ datetime[2] + datetime[4] // "+rows+ "  
	dom.byId("messages").innerHTML = z; 	
	var table = new google.visualization.Table(document.getElementById('sessionTable'));  //visualization.BarChart
	var formatter = new google.visualization.ColorFormat();
	//formatter.addRange("Done", "Next", 'black', 'red');
	formatter.addRange("Next", "Now", 'black', 'yellow');
	formatter.addRange("Now", null, 'black', '#33ff33');  // 'green'
	//formatter.addRange("Later Today", null, 'black', 'orange');
	formatter.format(data, 0); // Apply formatter to second column
	table.draw(data, {allowHtml: true, showRowNumber: false, width: '100%', height: '100%'}); 
};

// Tables for side panel (for East Wing Session only) - Shows Hydrants not inspected in the last 12 months. 
function drawTable2(chartInfo) {
	//create a data google vis. table 
	var data = new google.visualization.DataTable(); 
	// add columns to table, 2st column is title. 
	data.addColumn('string', 'Status');
	data.addColumn('string', 'Title');
	data.addColumn('string', 'Room');
	data.addColumn('string', 'Start Time'); //  ** double check column type!!!!!!! **
	data.addColumn('string', 'End Time');
	//data.addColumn('date', 'Last Edit Date');
	var rows = 0;
	// now add rows by iterating through the sel. orgs. in 2 dimensional array, use indexes to add data to table.  sessionStatus(datetime, i)
    for (var i = 0; i < chartInfo.length; i++) {  // Condition: Add sessions with status Now and Next & East Wing only.  
		if ((sessionStatus(chartInfo[i]) == "Now" || sessionStatus(chartInfo[i]) == "Next") && chartInfo[i][6] == "Exhibit Hall") {  // "Next" ||
			//console.log(sessionStatus(chartInfo[i]));
			data.addRow([sessionStatus(chartInfo[i]), chartInfo[i][1], chartInfo[i][2], chartInfo[i][4], chartInfo[i][5]], {style: 'height:6px; font-size:9px;'});  // , datetime, dateday
			rows += 1;
		} 
	}
	w = "<b>Convention Center Exhibit Hall Events </b>"  //" +rows+ "
	dom.byId("messages2").innerHTML = w; 	
	var table = new google.visualization.Table(document.getElementById('sessionTable2'));  //visualization.BarChart
	var formatter = new google.visualization.ColorFormat();
	//formatter.addRange("Done", "Next", 'black', 'red');
	formatter.addRange("Next", "Now", 'black', 'yellow');
	formatter.addRange("Now", null, 'black', '#33ff33');  // 'green'
	//formatter.addRange("Later Today", null, 'black', 'orange');
	formatter.format(data, 0); // Apply formatter to second column
	table.draw(data, {allowHtml: true, showRowNumber: false, width: '100%', height: '100%'});
};

//
function drawTable3(chartInfo) {
	// var date = new Date(features[x].attributes["Award_Date"]); and ", Award Date: "+ date.getFullYear()+ "
	//create a data google vis. table 
	var data = new google.visualization.DataTable(); 
	//console.log(chartInfo[0]);
	// add columns to table, 2st column is title. 
	data.addColumn('string', 'Status');
	data.addColumn('string', 'Title');
	data.addColumn('string', 'Room');
	data.addColumn('string', 'Start Time'); //  ** double check column type!!!!!!! **
	data.addColumn('string', 'End Time');
	//data.addColumn('date', 'Last Edit Date');
	var rows = 0;
	// now add rows by iterating through the sel. orgs. in 2 dimensional array, use indexes to add data to table.  sessionStatus(datetime, i)
    for (var i = 0; i < chartInfo.length; i++) {  // Condition: Add sessions with status Now and Next & East Wing only.  
		if ((sessionStatus(chartInfo[i]) == "Now" || sessionStatus(chartInfo[i]) == "Next") && chartInfo[i][6] == "Mezzanine") {  // "Next" ||
			//console.log(sessionStatus(chartInfo[i]));
			data.addRow([sessionStatus(chartInfo[i]), chartInfo[i][1], chartInfo[i][2], chartInfo[i][4], chartInfo[i][5]], {style: 'height:6px; font-size:9px;'});  // , datetime, dateday
			rows += 1;
		} 
	}
	w = "<b>Mezzanine Events</b>"  //" +rows+ "
	dom.byId("messages3").innerHTML = w; 	
	var table = new google.visualization.Table(document.getElementById('sessionTable3'));  //visualization.BarChart
	var formatter = new google.visualization.ColorFormat();
	//formatter.addRange("Done", "Next", 'black', 'red');
	formatter.addRange("Next", "Now", 'black', 'yellow');
	formatter.addRange("Now", null, 'black', '#33ff33');  // 'green'
	//formatter.addRange("Later Today", null, 'black', 'orange');
	formatter.format(data, 0); // Apply formatter to second column
	table.draw(data, {allowHtml: true, showRowNumber: false, width: '100%', height: '100%'});
};

// function of return basic info and statistics
function qStats(features) {
	var Assigned = Completed = Unassigned = Other = 0;
	//var nonlisted = 0;
	var total = features.length;
	console.log(features[0].attributes["INSSTATUS"]);
		//var sumTotal = 0;
		len = features.length;  // ["AMBULANCE AND FIRE SERVICE COMBINED", "FIRE AND RESCUE SERVICE", "FIRE DEPARTMENTS (E.G., GOVERNMENT, VOLUNTEER (EXCEPT PRIVATE))", "FIRE FIGHTER TRAINING SCHOOLS", "OTHER"]
		for (var i = 0; i < len; i++) {
			if (features[i].attributes["INSSTATUS"] == "Assigned") {
				Assigned += 1; 
			} else if (features[i].attributes["INSSTATUS"] == "Completed"){
				Completed += 1;
			} else if (features[i].attributes["INSSTATUS"] == "Unassigned"){
				Unassigned += 1;
			} else {
				Other += 1;
			}				
		}
	return [Assigned, Completed, Unassigned, Other];  //, nonlisted]; //[sumTotal, vol, combo, paid];
};
});