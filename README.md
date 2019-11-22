Recent Development Portfolio:
1.  ReusableAnalysis: The script returns a State’s fire departments from the HIFLD API, and groups fire departments by a variable such as City or Zip Code.   The Pandas and Mathplotlib libraries are used to group departments by the selected variable and plot them in a graph.  The example displays the top five Mississippi cities with the highest number of fire departments.    
2.  ManageUserContent:  The script manages ArcGIS Online user content.  Temporary accounts in ArcGIS Online accumulate orphaned maps, layers, and other content.  The script iterates through a list of users and their content, and attempts to remove relationships between groups, layers, and apps in order to delete items.  If relationships are not removed and items cannot be directly deleted, the content is reassigned to an admin and deleted.  
3.   DataFinishing: The data finishing script is used to clean and augment datasets.  Use Regular Expressions and dictionaries to find and replace abbreviations and punctuation.  Use APIs to add County FIPs codes from FCC API, geocode addresses from ESRI world geocoder API, and fill in missing address fields with reverse geocoder.   
4.  Conference_Session_Info:  The application uses Javascript to provide real-time updates of conference sessions and their locations.  The app uses ESRI Javascript 3.5 API and several feature services to provide a conference map and upcoming and current sessions at a conference.  
FlaskApp_MessageBrd_V2: The application was created in Flask, a web framework written in Python. The App is a message board where users can post and delete comments, and login for more features. Users credentials are written to a PostGreSQL database. The App serves as a way to keep my skills up, shows I can write larger scale Python applications, and as a little fun. 
