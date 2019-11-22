from flask_table import Table, Col, LinkCol
import sqlite3
import datetime
import time

# class format the Flask table.
class ClientTable(Table):
    client_id = Col('Client ID')
    firstname = Col('First Name')
    lastname = Col('Last Name')
    city = Col('City')
    state = Col('State')
    age = Col('Age')
    gender = Col('Gender')
    date = Col('Late Updated')
    #edit = LinkCol('Edit', 'updateDB', url_kwargs=dict(id='client_id'))

# class format the Flask table.
class CommTable(Table):
    comment = Col('Comment')
    date = Col('Date')
    user_id = Col('User_id')
    firstname = Col('Name')
    responseto = Col('Response Comment')
    responsedate = Col('Response Date')
    edit = LinkCol('Delete', 'deleteComm', url_kwargs=dict(id='user_id'))

class Comment(object):
    argComm = ['claim_id', 'condition', 'status', 'hospital', 'doctor', 'date', 'client_id']

    def __init__(self, comm_id, comment, date, user_id, firstname, responseto, responsedate):  #
        self.comm_id = comm_id
        self.comment = comment
        self.date = date
        self.user_id = user_id
        self.firstname = firstname
        self.responseto = responseto
        self.responsedate = responsedate

class User(object):
    login = None
    workerN = []
    argNames = ['client_id', 'firstname', 'lastname', 'city', 'state', 'age', 'gender', 'xCoord', 'yCoord', 'date']
    userD = {}

    def __init__(self, firstname, lastname, city, state, email, xcoord, ycoord, date, password):  # user_id,
        #self.user_id = user_id
        self.firstname = firstname
        self.lastname = lastname
        self.city = city
        self.state = state
        self.email = email
        self.xCoord = xcoord
        self.yCoord = ycoord
        self.date = date
        self.password = password

    def addUserD(self):
        # create dict from query pass to form, if user exists, use existing id, if not create.
        #rowdict = {}
        for attr, value in User.__dict__.items():
            # for no existing claims
            userD[attr] = val

    # return names from table in tuple to feed table method.
    def tabnames(self):
        return self.firstname + " " + self.lastname

    # return values
    def userAttr(self):
        return self.user_id, self.firstname, self.lastname, self.city, self.state, self.age, self.gender, self.xCoord, self.yCoord, \
               self.date