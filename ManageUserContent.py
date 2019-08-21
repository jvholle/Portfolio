# ---------------------------------------------------------------------------
# John Von Holle, 050119
# Description: Remove orphaned items from the AGOL Org. Remove any relationships to other items, then delete item.
# ---------------------------------------------------------------------------

# Import modules
import arcpy
import os
import json
import myPyUtils as ut
from datetime import datetime
# access gis from AGOL
from arcgis.gis import GIS
import time
# import csv

# import itertools
propAsJson = None
def getAppProperty(propElement):
    global propAsJson
    if not propAsJson:
        # read once & keep in memory.
        propFile = "manageAGOLuserConfig.json"
        if os.path.isfile(propFile):
            propAsJson = json.loads(open(propFile).read())
    if propAsJson:
        return ut.jsonTargetedFetch(propAsJson, propElement)
        pass
    return None
pNU = getAppProperty("portal.usr")
pPW = getAppProperty("portal.pass")

gis = GIS("https://iafc.maps.arcgis.com", pNU, pPW)  # AGOL "iafc_script"  gis = GIS()
# convert Unix epoch time to local time, 2 weeks with millisecs = 1209600000, 1 week = 604800
iafc_users = gis.users.search(query=None, max_users=1000)
'''itemid = '2a27793309f14258ae93c66497d2b90a'
groupid = 'bd1f5d8087d44e4bb2a6c1688f2ee6e3'  # '18e3876c64a64c928ba453da751ce7b3'  # Event ext '6944c81859154f4f94ca2027bc48f7c8'  # internal
spec_group = gis.groups.get(groupid)'''

# define class
class MangUserCont:

    # Defines the entry point into the script - # Using the second method pass the path to a valid connection file
    scriptpath = os.path.realpath(__file__)  # days since last mod. formula:  i.modified/1000
    # today time
    todayTime = time.time()
    cur_time = time.time()  # time without milliseconds  print(cur_time)
    # ID all of the users that logged in within a given time period.
    cnt = 0
    attr_list = []
    userList = []
    # create list of named users from the Account Req. Layer to check for existing users.
    returnUNs = {}  # []
    # Item types global list
    itemTypes = ['Feature Service', 'Form', 'Web Map', 'Mobile Application', 'Web Mapping Application', 'Code Attachment']
    doNotTouchUsers = ['jvonholle35', 'iafc_script', 'iafc.training1']

    # init statement
    def __init__(self, startswith, user):
        self.startswith = startswith
        self.user = user
        # self.fldItems = fldItems

    def createNUlist(self):  # srtswith
        user_accounts = gis.users.search(query=None, max_users=6000)  # None
        # return list of named users that starts with 'event.team'.   or acc.username.startswith('grp')
        exunList = [acc for acc in user_accounts if acc.username.startswith(self.startswith) and
                    acc.username not in doNotTouchUsers]  # != 'iafc.training1']  # event.team
        # create another list or dictionary of hold user names, to check for existing users.
        # returnUNs = {}
        for item in exunList:  #
            # returnUNs.append(item.username)
            # return a dictionary of existing users for existing user check. Org = firstName, Full name = lastName for NUs.
            returnUNs[item.username] = [item.firstName, item.lastName, item.fullName, item.email]
        print('Created list of Named Users for special task: '+str(returnUNs))   # print(returnUNs.keys())
        return returnUNs

    # Add Users to the Org from a list, excel priority, determine if add users from outside Org.
    def addUsersGrp(self):
        # Access the group, test list content
        # arcpy.AddMessage(spec_group.content())
        try:
            if len(userList) > 0:
                arcpy.AddMessage("Current Members: " + str(spec_group.get_members()))
                # Add users to group by calling add_users(List).  To invite users outside Org: use invite_users()
                # print(spec_group.remove_users(userList))  # ** Remove users
                # print(spec_group.invite_users(userList))  # ** Invite users
                arcpy.AddMessage("Members after changes: " + str(spec_group.get_members()))
        except Exception as err:
            print(err)

    # Manage item relationships. If related to another item, determine relation, and delete relate.  arg: id or title.
    def manItemRelations(self):  # item
        # check for relationships. If related, remove any relationships of item.
        if item.type in itemTypes:  # Or, if item.type == 'Feature Service':
            # Determine item dependencies - use a dictionary of dependencies: functions.
            iRelat = item.related_items('Service2Data', 'forward')  # item.dependent_to() or _upon()
            iDependto = item.dependent_to()  # item.dependent_to() or _upon()
            iDependupon = item.dependent_upon()  # print(iDependupon)
            # Loop through the depend/relate methods and attempt to remove them.
            for relate in [iDependto, iDependupon]:  # , iRelat]:
                try:
                    # if there is list of relations, loop through them and remove.
                    if len(relate['list']) > 0:
                        print(relate)
                        # Loop through the dependency values/ids, and remove dependency before delete.
                        for it in relate.values():
                            if it['dependencyType'] == 'id':  # other option is 'url' for hosted fs.
                                print("Attempt to delete relationships of item: " + str(it['id']))
                                if it.type == 'Map2Service':
                                    print(item.delete_relationship(rel_item=it['id'], rel_type='Map2Service'))  # Map2Service
                                else:
                                    print(item.delete_relationship(rel_item=it['id'], rel_type='Service2Data'))
                                # print(it.delete())
                except Exception as err:
                    print(err)
                    print("Item type was not able to be deleted: " + str(relate['list']))
                    continue
                    # item.related_items('Service2Data', 'forward')  # respond true

    def adminDelItems(self):
        print("Attempting to delete items from admin: Reassigned_Content folder")
        cntSize = 0
        # get items of user
        objUser = gis.users.get(self.user)  # get('iafc_script')
        # loop thru items in Reassigned Content Folder and delete
        fldItems = objUser.items(folder='Reassigned_Content')  # fldItems = ...
        for it in fldItems:
            try:
                print("Attempting to remove dependencies and delete: " + str(it.title))
                # pass the item to the remove relationship func. and then try to delete
                manItemRelations(it)
                # Attempt to delete the item.
                cntSize += (it.size / 1000000)  # convert from bytes to megabytes
                print("Deleted item: " + str(it.delete()))
                #
            except Exception as err:
                print(err)
                print("Item type was not able to be deleted: " + str(it.type))
                continue
        print("Size of items in folder deleted: " + str(cntSize))

    # Process items from individual folders and reassign or delete.
    def proitemfolder(self):  # fldItems
        for it in self.fldItems:  # item.types to delete: feature service and web map.
            # if needed access items from it.id = item id for deletion.
            # cnt += (it.size / 1000000)  # convert from bytes to mb.
            daysLastUpd = (todayTime - it.created / 1000) / 86400  # 86400 is seconds in one day.
            # condition to remove or reassigned if a feature service more than 60 days old.
            # itemTypes = ['Feature Service', 'Form', 'Web Map', 'Mobile Application', 'Web Mapping Application']
            print(it.type)
            if it.type in itemTypes and daysLastUpd > 14:
                print("Item to be deleted or reassigned*: " + str(it))
                # reassign content and then loop through destination folder to delete.
                if it.reassign_to(target_owner='iafc_script', target_folder='Reassigned_Content'):  # is True:
                    print("Reassigned item! " + str(it.title))
                    # Option: Directly delete the reassigned item by .get(item) - itemToDelete = gis.content.get(it.id)
                # print('Item Successfully deleted: ' + str(item) + ' - ' + str(item.size))
                else:
                    it.delete()
                    print("Deleted item: ")  # + str(it.title)

def main():
    # init the manage user class args: startswith, user
    manUsers = MangUserCont('iafc.training', 'iafc_script')
    # run create NU list to populate returnUN dictionary.  # startswith='iafc.training' old: createNUlist(startswith)
    manUsers.createNUlist()

    # Remove all content. If the user owns content, reassigned to gen. folder, then delete.
    for user in returnUNs.keys():   # for user in userList:
        try:
            cnt = 0
            # get items of user
            objUser = gis.users.get(username=user)  # (user)
            # // Potential Issue: Script has be be run twice to delete items in root dir.//

            ''' 1. Start with the items in the root folder and pass them to func. for reassign/deletion. '''
            rootItems = objUser.items()  # for items in root folder only, if folder is not specified.
            # call function to reassign/delete items in folder.
            print(rootItems)
            proitemfolder(rootItems)

            ''' 2. Continue to search thru the items in the Users' Other folders. '''
            # loop through folders of users and list items in each folder. object.items() only contents of root fld.
            userFldList = objUser.folders  # depedDict = {}
            for fld in userFldList:
                try:
                    # print(objUser.items(folder=fld))
                    fldItems = objUser.items(folder=fld)
                    # call function to process reassign/delete items in folder.
                    proitemfolder(fldItems)
                    # Once items removed, try to delete folder itself **
                    if not fldItems:
                        fld.delete()
                except Exception as err:
                    print(err)
                    continue
                if cnt > 0:
                    print('Size of items to be deleted for user: ' + str(cnt) + ' mb')
        except Exception as err:
            print(err)
            continue
    # Delete items from Reassigned content folder.
    manUsers.adminDelItems()

# ---------------------Call Functions------------------
if __name__ == '__main__':
    main()
