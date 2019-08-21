# ---------------------------------------------------------------------------
# John Von Holle, 062117
# Usage: SelectLayerByLocation_management (in_layer, {overlap_type}, {select_features}, {search_distance}, {selection_type})
# Description: Replace hard coded abbreviated text from text replacment dic by individual fields.
# ---------------------------------------------------------------------------
# Import arcpy module
import arcpy
import os
import re
import json
import csv
# Set the input workspaces
Input1 = r'C:\Projects\Data\FireEMS_DataInitiative\HIFLD\Firefighter_Data.gdb'  # arcpy.GetParameterAsText(0)  # Geodatabase use for env for cursor.
Input2 = r'C:\Projects\Data\FireEMS_DataInitiative\HIFLD\Firefighter_Data.gdb\IAFC\IAFCFireStations_HIFLD_test'  # arcpy.GetParameterAsText(1)  # FC or table to iterate and select feature ex. Membership. -Output directory and FDS.  where the FC will be output.
# Input3 = arcpy.GetParameterAsText(2)  # Name of FC for export.  Ex. FCs meet criteria = String

# read in the Datasource json file as a datastore for regex string substitution.  # datastore = {}
with open('ReplaceDictAll.json', 'r') as f:  # 'ProvSrceFld.json'
    datastore = json.load(f)
    # arcpy.AddMessage(datastore)

# temp dicts for CSVs of update dates and Data Providers. Read the csv to a dictionary at start of script.
UpdDateDic = {}
DataProvDic = {}
''' Populate the State for each State and state csv file to only pull the referenced State's rows. '''
State = 'XX'  # 'SC' - Change the State and csv fields for each state to insert the update dates and data provider.
''' ----- '''
fileLoc_UpdDate = r'C:\Projects\Data\FireEMS_DataInitiative\HIFLD\Excel\MA\MA_FireStations_121818.csv'
fileLoc_DataProv = r'C:\Projects\Data\FireEMS_DataInitiative\HIFLD\HIFLD_Schema\DataProvider_ProvDate\DataProvider_ProvDate.csv'
# Read both CSVs into a dictionary for data extraction.
for sfile in [fileLoc_UpdDate, fileLoc_DataProv]:
    if State not in ['XX', '']:
        with open(sfile, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:  # if line_cnt == 0:
                try:
                    if sfile == fileLoc_UpdDate:
                        # key = concate name[:5]+address[:5], value = update date.  - match to exist hifld data.
                        ''' Dept. Name, Address, Update Date fields must be updated for each State! '''
                        UpdDateDic[(row['NAME'][:5] + row['ADDRESS'][:5]).upper()] = row['Upd_Date']
                    else:  # Create dict. Prov Name and Date, use ST abbr dict. to extr/pop. ProvDate from csv
                        AbbvSt = datastore['StateAbbrev'].get(row['State'])
                        DataProvDic[AbbvSt] = [row['HIFLD Name'], row['Data Provided Date']]
                except Exception as err:
                    arcpy.AddMessage(err)
                    continue
            arcpy.AddMessage("Temp dictionaries were created for matching.")

# function to format phone number as (xxx) xxx-xxxx ext. xxxx
def formatPhone(number):
    #str(number)
    newVal = number.replace(" ", "").replace("-", "")
    print('attempt to format phone number '+newVal)
    arcpy.AddMessage(newVal[0:3])
    if len(newVal) == 10:
        areaCode = newVal[0:3]
        exchange = newVal[3:6]
        line = newVal[6:10]
        arcpy.AddMessage("({0}) {1}-{2}".format(areaCode, exchange, line))
        return "({0}) {1}-{2}".format(areaCode, exchange, line)
    else:
        arcpy.AddMessage("Number not in 10 digit format, did not process: " + str(number))
    # Sting formating method   num="0123456789"    # print("("+num[:3]+")"+num[3:6]+"-"+num[6:])

# Replace string abbreviations, upper/lower case, and other formatting issues.
def ReplaceAbbr_OneFC():
    # Make a set of the list to produce only unique values from the original list. UniqueList = set(memDB).
    replaceDic = {'Dept': 'Department',  'Dist': 'District', 'Co': 'Company', 'Svcs': 'Services', 'Vol': 'Volunteer',
                  'Prot': 'Protection', 'Twp': 'Township', 'Cnty': 'County', 'Emerg': 'Emergency', 'Serv': 'Services',
                  'Div': 'Division', 'Cty': 'County', 'VFD': 'Volunteer Fire Department', 'Fpd': 'Fire Protection District',
                  'Srvs': 'Services', 'Intl': 'International', 'assn': 'Association', 'Assoc': 'Association',
                  'Amb.': 'Ambulance', 'FPD': 'Fire Protection District', 'Govt': 'Government', 'F.D': 'Fire Department',
                  'V.F.D': 'Volunteer Fire Department', 'Assn': 'Association', 'Dis': 'District',
                  'Company Fire': 'County Fire', 'Sfty': 'Safety', 'Trng': 'Training', 'Ctr': 'Center',
                  'Grnd': 'Ground', 'Natl': 'National', 'Eqpmt': 'Equipment', 'Comm': 'Community',
                  'TWP': 'Township', 'Mfg': 'Manufacturing', 'FD': 'Fire Department', 'Resc': 'Rescue', 'Sqd': 'Squad',
                  'Svc': 'Service', 'Srvcs': 'Services', 'F.P.D': 'Fire Protection District', 'Fd': 'Fire Department',
                  'Ret': 'Retired', 'Chief-Ret': 'Chief Retired', 'ESD': 'Emergency Services Department', '\&': 'AND',
                  'RD': 'Road', 'HWY': 'Highway', 'LN': 'Lane', 'AVE': 'Avenue', 'CT': 'COURT', 'TER': 'TERRACE',
                  'TR': 'TRAIL', 'TRC': 'TRACE', 'DR': 'Drive', 'PKWY': 'Parkway', 'BLVD': 'Boulevard', 'Ct': 'COURT',
                  'CIR': 'Circle', 'STA': 'Station', 'FS': 'Fire Station', 'STATE HIGHWAY': 'SR', 'STATE ROUTE': 'SR',
                  'STATE ROAD': 'SR', 'CONSOLID': 'CONSOLIDATED', 'RVFD': 'Volunteer Fire Department',
                  'INCORPORATED': 'INC.', '\sN': 'NORTH', ' +': ' ',  # white space removal
                  '\sS': 'SOUTH', '\sE': 'EAST', '\sW': 'WEST', 'COUNTY ROAD': 'CR', ',': '',
                  'HQ': 'HEADQUARTERS', 'MTN': 'MOUNTAIN', 'FT': 'FORT', 'MT': 'MOUNT',
                  'FPS': 'Fire Protection Service', 'AFB': 'AIR FORCE BASE', 'CAPT': 'CAPTAIN'}
    # Regex expression used with func. below: r'\bDept(?:\.|\b)': 'Department'  r'\bST': 'STREET',  , '\'SOUTH': '\'S'
    # Replacement of S with South, etc.  Need a '\s' in front of the re search of 'S'. To avoid repl. "'S" with "SOUTH".
    # ** ST could mean Street, Saint, or Station.  Will need to adjust dict. for target field or Replace Manually. **

    # Dictionary to house all of the replacement. Iterate values for replacements during search.
    fields = [str(f.name) for f in arcpy.ListFields(Input2)]
    # arcpy.AddMessage(fieldTypes)
    arcpy.AddMessage("{0}\n".format(fields))
    arcpy.env.workspace = Input1
    cnt = 0

    ''' Global variable for field index of cleanup target. '''
    iVal = 4  # index val of row to be updated.  **Change dict value for ST by Field - Address VS Department

    try:  # Step 1: Loop vals remove spaces, text after carriage returns, replace vals from replace dict, remove '()'s.
        with arcpy.da.UpdateCursor(Input2, fields) as updcur:  # fields
            for row in updcur:
                try:
                    rowNew = None
                    # while looping rows remove carriage returns '\r' and remaining string.
                    if '\r' in row[iVal] or '\n' in row[iVal]:
                        arcpy.AddMessage("Attempt to remove Carriage return in String: " + str(row[iVal]))
                        if '\r' in row[iVal]:  # .split function allow multi arguments.
                            rowNew = row[iVal].rstrip().split('\r')
                        elif '\n' in row[iVal]:  # .split function allow multi arguments.
                            rowNew = row[iVal].rstrip().split('\n')
                        elif '\r\n' in row[iVal]:  # .split function allow multi arguments.
                            rowNew = row[iVal].rstrip().split('\r\n')
                        # rowNew = re.split('(\r |\n |\r\n |\n\r)', row[iVal].rstrip())  # split with multi args.
                        # splitting a string with carriage return, creates list split strs, need to retain first str.
                        row[iVal] = rowNew[0]
                        updcur.updateRow(row)
                        arcpy.AddMessage("Carriage return in String was removed: " + str(row[iVal]))
                        cnt += 1
                    # remove any leading or training white space and any parenthesis.
                    elif row[iVal].startswith(' ') or row[iVal].endswith(' '):
                        row[iVal] = row[iVal].upper().strip()
                        updcur.updateRow(row)
                        arcpy.AddMessage("Space in String was removed: " + str(row[iVal]))
                        cnt += 1
                    # remove parenthesis from Dept. Name field.
                    elif iVal == 3 and '(' in row[iVal]:
                        val = row[iVal].upper().replace('(', '').replace(')', '')  # strip() any white space.
                        arcpy.AddMessage("'()'s in String was removed: " + val)
                        row[iVal] = val
                        updcur.updateRow(row)
                        cnt += 1
                    # Fix any " 'SOUTH " or .WEST type errors. Can be removed later.
                    elif iVal == 3 and '&' in row[iVal]:
                        val = row[iVal].replace('&', 'AND')  # strip() any white space.  ('\'SOUTH', '\'S')
                        #val = row[iVal].replace('+', '')  # strip() any white space.  ('\'SOUTH', '\'S')
                        arcpy.AddMessage("& in String was removed: " + val)
                        row[iVal] = val
                        updcur.updateRow(row)
                        cnt += 1
                    # condition to replace ST with Street, use \b ST \b is a word string, avoid remove ST for Saint.
                    elif iVal == 4 and re.search(r"\b" + re.escape("ST") + r"\b", row[iVal]) and "ST" in row[iVal][-4:]:
                        val = row[iVal].replace('ST', 'STREET')  # strip() any white space.  ('\'SOUTH', '\'S')
                        #val = row[iVal].replace('+', '')  # strip() any white space.  ('\'SOUTH', '\'S')
                        arcpy.AddMessage("ST was replaced with STREET: " + val)
                        row[iVal] = val
                        updcur.updateRow(row)
                        cnt += 1
                    else:
                        continue
                except Exception as err:
                    arcpy.AddMessage(err)
                    print(str(row[4]))
                    continue
                # Use Replace Dictionary to replace any designated values.
                try:  # Change the Row[] index value depending on the update field.  *For ST repl: "ST": "Street",
                    replaceDic = datastore['GenReplace']
                    for key, value in replaceDic.items():  #  '' py 2 .iteritems() arg Lst: # re.sub(pattern, repl, str)
                        # check if any part of value in row[iVal] needs to be replaced. This will stop 'NoneType Error'
                        if key in row[iVal]:
                            # Use regular expression re.compile find sub strs where RE match, and replace with sub() method.
                            p1 = re.compile(r'\b{}(?:\.|\b)'.format(str(key)))  # (key)  # \b str \b are word boundaries
                            replace1 = p1.sub(value, row[iVal])  # returns the revised string to input into the DB.
                            if replace1 and row[iVal] != replace1 and row[8] == "NC":  # isolation by St row[8] == 'HI'
                                arcpy.AddMessage("Replacement: " + row[iVal] + " With: " + replace1)
                                row[iVal] = replace1  # row[3] update string in cell with re
                                cnt += 1
                    updcur.updateRow(row)
                    # arcpy.AddMessage("The abbreviated string has been updated!")
                except Exception as err:
                    arcpy.AddMessage(err)
                    continue
    except Exception as err:
        arcpy.AddMessage(err)  # arcpy.AddMessage

    # Step 2: replace all lower case letters to upper, phone number format function, pop. Dataprovider & UpdateDate.
    with arcpy.da.UpdateCursor(Input2, fields) as updcur2:  # fields
        cnt2 = 0
        for row in updcur2:
            # arcpy.AddMessage(str(row[3]))
            if row[iVal]:  # is not None:
                try:
                    # cond. various string replacements.
                    rowstr = row[iVal]
                    # cond. only for phone field, call phone format function. else run all caps.
                    if iVal == 15 and rowstr[0] != "(":  # if iVal == 14 and row[8] == "AK":  # rowstr[0] != "(":
                        val = formatPhone(rowstr)
                        row[iVal] = val
                        arcpy.AddMessage("updated val: " + str(formatPhone(row[15])))
                        updcur2.updateRow(row)
                        cnt2 += 1
                    # Replace all lower and mixed upper and lower values with upper characters.
                    elif not rowstr.islower() and not rowstr.isupper() or rowstr.islower():  # fieldTypes[n] == 'String'
                        # arcpy.AddMessage("row to be updated: "+ str(row[3]))
                        val = rowstr.upper()
                        row[iVal] = val
                        updcur2.updateRow(row)
                        #arcpy.AddMessage("Row updated!")
                        cnt2 += 1
                    # remove 'County' from the cty name only the county field, ignore caps letters for now.
                    elif iVal == 7 and 'COUNTY' in rowstr:
                        val = rowstr.upper().replace('COUNTY', '').strip()  # strip() any trailing white space.
                        arcpy.AddMessage("updated val: " + val)
                        row[iVal] = val
                        updcur2.updateRow(row)
                        #arcpy.AddMessage("Row updated!")
                        cnt2 += 1
                    # populate any blank value for the DataProvider field
                    elif not row[23] or not row[25] and State == row[8]:  # 8 and 23, alternative: DataProvDic[row[8]]
                        # get() function for the state key will yield the datastore value for the State.
                        #datapro = datastore['DataProvider']
                        #provVal = datapro.get(row[8])  # incl. ProvDate, make list of vals. in json, access via index.
                        provVal = DataProvDic.get(row[8])  # incl. ProvDate, make list of vals. in json, access via index.
                        row[23] = provVal[0]  # ex. with ProvDate: row[23] = provVal[0] \n row[26] = provVal[1]
                        row[25] = provVal[1]
                        updcur2.updateRow(row)
                        arcpy.AddMessage("Updated value for Source Field: " + str(provVal))
                        cnt2 += 1
                    # cond. if State is current loaded csv file, then proceed with matching update dates.
                    if State == row[8]:  # pot. match: name[3], address[4], updatedate[24], csv rows - not row[24] and
                        # assign UPDATEDATE Field to corresponding csv update date from csv dictionary.
                        row[24] = UpdDateDic.get(row[3][:5]+row[4][:5])  # might be a date formatting issue!
                        updcur2.updateRow(row)
                        # if row[3][:5]+row[4][:5] == upper(tempDic.get(row[3][:5]+row[4][:5])):
                        arcpy.AddMessage("Update Date Populated! " + str(row[24]))
                        cnt2 += 1
                    else:
                        continue
                except Exception as err:
                    arcpy.AddMessage(err)
                    print(str(row[4]))
                    continue
        arcpy.AddMessage("Rows Updated Case: "+str(cnt2))
        # del updcur2
    if cnt == 0:
        arcpy.AddMessage("No replacements occurred as part of the process!")
    else:
        arcpy.AddMessage("Number of abbreviations replaced or spec. situations fixed: " + str(cnt))
    del cnt
    # arcpy.Delete_management("NatDept_lyr")
# ---------------------Call Functions------------------
if __name__ == '__main__':
    ReplaceAbbr_OneFC()

# ----------------------------------------------------

# Dic of State: State Abbreviations
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
    'Northern Mariana Islands':'MP',
    'Palau': 'PW',
    'Puerto Rico': 'PR',
    'Virgin Islands': 'VI',
    'District of Columbia': 'DC'
}
StAbbr_States = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}
# Class format phone number:
'''class PhoneNumber:
    def __init__(self, number):
        self.areaCode = number[1:4]
        self.exchange = number[6:9]
        self.line = number[10:14]

    def __str__(self):
        return "(%s) %s-%s" % (self.areaCode, self.exchange, self.line)


newNumber = "(123) 456-7890"

phone = PhoneNumber(newNumber)
print "The phone number is:",
print phone'''