from MessBrd_Postgres_V2 import app
from MessBrd_Postgres_V2 import models
from MessBrd_Postgres_V2 import forms
from flask import current_app
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, Blueprint, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_table import Table, Col, LinkCol
from flask_wtf import FlaskForm as form
from wtforms import StringField, SelectField, HiddenField, DateField, DateTimeField, PasswordField
from wtforms.validators import DataRequired, InputRequired
import sqlite3
import psycopg2
import datetime
import time
import json


sqlLoc = r'C:\sqllite\webdev.db'
# items list
items = []
# get values from config: api_key =  str(app.config.get('API_KEY'))

def connPgres():
    """ Create PostGreSQL connection """
    try:
        un, pw = str(app.config.get('USERNAME')), str(app.config.get('PASSWORD'))
        conn = psycopg2.connect(host="127.0.0.1", database="webdev", user=un, password=pw, port="5432")
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error while conn to PostGreSQL", error)
    '''finally:
        if conn:
            cursor.close()'''

def addUserdb(userObj):
    """ Add user to DB """
    try:
        print(userObj[4])
        # create a new user, - create connection object to db
        conn = connPgres()
        #conn = sqlite3.connect(sqlLoc)
        c = conn.cursor()  # client_id, firstname, lastname, city, state, age, gender, xCoord, yCoord, date
        # insert or replace is for Sqlite; Postgres use the upsert statement with INSERT ON CONFLICT
        sql = '''INSERT INTO Users (firstname, lastname, city, state, email, xCoord, yCoord, date, password) 
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
             #ON CONFLICT (email) DO UPDATE
            #SET lastname = %s, email = %s, import ts = now();'''  # (lastname, email) = (EXCLUDED.lastname, EXCLUDED.email);'''
        #val = userObj
        c.execute(sql, userObj)
        # WHERE userObj.email = Users.email AND userObj.lastname <> Users.lastname;
        # get the generated user_id back
        #user_id = c.fetchone()[0]
        conn.commit()
        flash('User inserted successfully!')
        # if user was created/updated, perform second query to get newly created user id. #if createUser:
        time.sleep(2)
        email = userObj[5]
        user_id = (queryDB(email, Users=True))[0][0]
        return user_id
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)

def strTime(dateObj):
    #return datetime.datetime.fromtimestamp(seconds).strftime("%Y-%m-%d")
    # convert date obj. into string with am/pm.
    return dateObj.strftime("%Y-%m-%d %H:%M%p")

#  query database, return rows from a table: args= id, name. Else will return all rows.
def queryDB(fldVals, Users=True):
    # Postgres DB conn
    conn = connPgres()
    c = conn.cursor()
    # return one row for editing
    if fldVals:
        v = (fldVals,)
        if Users:
            c.execute('SELECT * FROM users WHERE email=%s', v)  # rowid
        # query only responses that match user
        elif isinstance(fldVals, datetime.date):  # or datetime.datetime
            c.execute('SELECT * FROM comments WHERE date=%s', v)
        else:  # select by rowid for queries
            c.execute('SELECT * FROM comments WHERE comm_id=%s', v)  # %(int)s
            # Client and Claim table join to show attributes from both tables.
            # c.execute('SELECT Clients.firstname AS client_fname, Clients.lastname AS client_lname, claim_id, condition, status, hospital, doctor, Claims.date AS dateadded, Claims.client_id AS cl_id '
            #          'FROM Claims INNER JOIN Clients '
            #          'ON Clients.client_id = Claims.client_id WHERE Clients.client_id = %s', v)  #
        # results = c.fetchall()  #print('correct query'+ str(results))
    # return all rows
    else:
        c.execute('SELECT * FROM comments ORDER BY date DESC;')  # Ordered by date descending
        # print(c.fetchall())
    results = c.fetchall()
    # print('results: ' + str(results))
    if not results:
        return None
    conn.close()
    return results

# insert new comment
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    """ Post comment from users """
    user_id = 1  # for anonymous users
    form = forms.AddComment()  #(formdata=request.form, obj=rowdict)
    if form.validate_on_submit():  # request.method == 'POST' and form.validate():
        # if user is logged in pass user id to comment.  #user_id = models.User.login
        if request.form['user_id']:
            user_id = request.form['user_id']
        else:
            user_id = 1
        # save edits - define edits from form.
        inForm = [request.form['comment'], request.form['date'], int(user_id), request.form['firstname']]
        # if the name is blank assign the name = anonymous
        if inForm[3] is None or inForm[3] is '':
            inForm[3] = 'Anonymous'
        tuple(inForm)
        print("Update DB: " + str(tuple(inForm)))
        # create connection object to db
        #conn = sqlite3.connect(sqlLoc)
        # Postgres DB conn
        conn = connPgres()
        c = conn.cursor()  # client_id, firstname, lastname, city, state, age, gender, xCoord, yCoord, date
        #c.execute('''INSERT INTO Comments (comment,date,user_id,given_name) VALUES(%(str)s,%(date)s,%(int)s,%(str)s)''', inForm)
        c.execute('''INSERT INTO comments (comment,date,user_id,given_name) VALUES(%s,%s,%s,%s)''', inForm)
        conn.commit()
        flash('Comment Added!')
        return redirect('/')

    # if user logged in, input the session data into form
    firstname = None
    if 'email' in session:
        user_id = queryDB(session['email'], Users=True)[0][0]
        firstname = session['user']
    # ='GET' to input form. Preload form fld. with vals. Define form.fld.data vals from sel. row to pass to form.
    # form.date.data = datetime.date
    form.user_id.data = user_id
    form.firstname.data = firstname
    if form.errors:
        print(form.errors)
    return render_template('addcomm.html', form=form)  # name=mD[0][0])

# response to comment
@app.route('/respond/<int:id>', methods=['GET', 'POST'])
def respond(id):
    date = datetime.datetime.today()
    # if user is logged in pass user id to comment.
    #if userObj is None:  #  if request.form['user_id']:   #user_id = models.User.login
    comm_id = id
    q = queryDB(id, Users=False)[0]
    # query comment id to pop form
    form = forms.RespComment()  #(formdata=request.form, obj=rowdict)
    if form.validate_on_submit():
        # comment, date, user_id, given_name, responseto, responsedate
        # save edits - define edits from form.
        inForm = [request.form['comment'], request.form['date'], request.form['firstname'],
                  request.form['responseto'], request.form['responsedate']]
        # if the name is blank assign the name = anonymous,
        if not inForm[4]:  # is None or inForm[4] is '':
            inForm[4] = 'Anonymous'
        #tuple(inForm)
        print("Update DB: " + str(tuple(inForm)))
        # create connection object to db
        #conn = sqlite3.connect(sqlLoc)
        # Postgres DB conn
        conn = connPgres()
        c = conn.cursor()  # client_id, firstname, lastname, city, state, age, gender, xCoord, yCoord, date
        c.execute('''INSERT INTO comments (comment,date,given_name,responseto,responsedate) 
        VALUES(%s,%s,%s,%s,%s)''', inForm)
        conn.commit()
        flash('Response inserted successfully!')
        return redirect('/')
        #return redirect(url_for('vCards', OrigComment=OrigComment[0]))

    # ='GET' to input form. Preload form fld. with vals. Define form.fld.data vals from sel. row to pass to form.
    #form.user_id.data = q[3]
    form.origcomment.data = q[1]  # Original Comment
    form.responseto.data = q[4]  #
    # convert datetime string back to datetime object
    '''dtObj = datetime.datetime.strptime(q[2], '%Y-%m-%d %H:%M%p')
    #dtObj = datetime.datetime.strptime(q[2], '%Y-%m-%d %H:%M:%S')
    print(dtObj)'''
    form.responsedate.data = q[2]  # dtObj
    if form.errors:
        print(form.errors)
    return render_template('respcomm.html', form=form)  # name=mD[0][0])

# display from database and ask to edit table values.
@app.route('/', methods=['GET', 'POST'])
def vCards():
    if 'user' in session:
        flash("A session is open to: "+str(session['user']))
    #OrCo = request.args.get('comment')
    # remove any existing items. List to pass to table
    values = []
    # process the items from the db to the Table digestible format
    dbRes = queryDB(None)
    # loop and add all of clients to items list as objects
    if dbRes:
        for i, it in enumerate(dbRes):
            #  instantiate the Item class with individual item objects. Ignore comment responses for now.
            if not it[5]:
                tabValues = models.Comment(it[0], it[1], strTime(it[2]), it[3], it[4], it[5], it[6])
                values.append(list(tabValues.__dict__.values()))
                # loop comments, add any resp. to list. Nest a loop to pull out assc. resp.
                for rp in dbRes:  #Cond. = name+date  set up a sql query
                    if rp[5]:
                        if it[4] + str(it[2]) == rp[5] + str(rp[6]):
                            rpValues = models.Comment(rp[0], rp[1], rp[2], rp[3], rp[4], rp[5], strTime(rp[6]))
                            values.append(list(rpValues.__dict__.values()))
    #print(values)
    # load the form for init user:
    form = forms.InitLogin(formdata=request.form)
    return render_template('index.html', values=values, form=form)

@app.route('/initLogin', methods=['GET', 'POST'])
def initLogin():
    date = datetime.datetime.today()
    # date = dt.strftime("%Y-%m-%d %H:%M:%S") #date = dt.replace(microsecond=0)

    # Add a comment with a fname and email provided. Later add elif for user register.
    if request.form['action'] == 'Make a Comment':
        # query emails from existing user table, if none, create user temp.
        userObj = models.User(None, None, None, None, None, None, None, None, None)
        # add values from form to obj.
        userObj.email, userObj.firstname, userObj.date = request.form['email'], request.form['firstname'], date
        qryRow = queryDB(userObj.email, Users=True)  # id = iTupl[6]  **** Table are not the same*** claims don't match clients tables.
        #print("query row: "+str(qryRow))
        createUser = False

        # if userVals obj contains an user_id, create user. if not, just create comments
        try:  # only insert into comments, if not email insert both user and comments.
            # create form for add comment and add user from name/email if provided.
            form = forms.AddComment(formdata=request.form, obj=userObj)
            if form.validate_on_submit():  # request.method == 'POST' and form.validate():
                # can send to comment(form)
                inForm = [request.form['comment'], request.form['date'], request.form['user_id'], request.form['firstname']]
                # if the name is blank assign the name = anonymous
                if inForm[3] is None or inForm[3] is '':
                    inForm[3] = 'Anonymous'
                tuple(inForm)
                print("Update DB: " + str(tuple(inForm)))
                # create connection object to db, Postgres DB conn # Old: conn = sqlite3.connect(sqlLoc)
                conn = connPgres()
                c = conn.cursor()  # client_id, firstname, lastname, city, state, age, gender, xCoord, yCoord, date
                c.execute('''INSERT INTO comments (comment,date,user_id,given_name) VALUES(%s,%s,%s,%s)''', inForm)
                conn.commit()
                flash('User inserted successfully!')
                return redirect('/')
            # ='GET' Load form fld. with vals. Define form.fld.data vals from sel. row to pass to form.
            # if existing user
            if not createUser:
                user_id = qryRow[0][0]
                print('Existing user: '+str(user_id))
                #form.user_id.data = user_id
            # create partial new user before comment form opened
            else:
                try:
                    # Postgres DB conn  #conn = sqlite3.connect(sqlLoc)
                    print("attempt to create new user by insert: " + str(userObj))
                    conn = connPgres()
                    c = conn.cursor()  # client_id, firstname, lastname, city, state, age, gender, xCoord, yCoord, date
                    c.execute(
                        '''INSERT INTO users (firstname,lastname,city,state,email,xcoord,ycoord,date,password) 
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''', userObj)  # user_id,
                    conn.commit()
                    flash('User inserted successfully!')
                    c.close()
                    conn.close()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
            # if user was created, perform second query to get newly created user id. #if createUser:
            time.sleep(1)
            user_id = (queryDB(userObj.email, Users=True))[0][0]
            # set the add comment form data from the initiate login form data.
            form.user_id.data, form.firstname.data, form.date.data = user_id, userObj.firstname, userObj.date
            # create cookie/session for user
            session['user'], session['email'] = userObj.firstname, userObj.email
            if form.errors:
                print(form.errors)
            return render_template('addcomm.html', form=form)  # name=mD[0][0])

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    # create a seperate condition for each button with action.
    elif request.form['action'] == 'Make Comment':
        # instantiate the form for addComment to receive post
        form = forms.AddComment()  # formdata=request.form, obj=userObj)
        if form.validate_on_submit():  # request.method == 'POST' and form.validate():
            # can send form to comment(form)
            inForm = [request.form['comment'], request.form['date'], request.form['user_id'],
                      request.form['firstname']]
            tuple(inForm)
            print("Update DB: " + str(tuple(inForm)))
            # create connection object to db Postgres DB conn  #conn = sqlite3.connect(sqlLoc)
            conn = connPgres()
            c = conn.cursor()  # client_id, firstname, lastname, city, state, age, gender, xCoord, yCoord, date
            c.execute('''INSERT INTO comments (comment,date,user_id,given_name) VALUES(%s,%s,%s,%s)''', inForm)
            conn.commit()
            flash('Comment Added!')
            return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Register/Login users. Two register options: Soft and full """
    date = datetime.datetime.today()
    # GET Method, user clicks on the sep. 'Register' button.
    if request.method == 'GET':
        form = forms.Register(formdata=request.form)  #, obj=userObj)
        return render_template('login.html', form=form)
    # Soft and full Register/Login of users.
    elif request.method == 'POST':
        # instantiate the user object and pass to form as obj
        U = models.User  # elif request.form['action'] == 'Register':
        userObj = U(None, None, None, None, None, None, None, None, None)
        # query emails from existing user table, if none, create user temp.
        # Add object elements from form
        userObj.email, userObj.firstname, userObj.date = request.form['email'], request.form['firstname'], date
        qryRow = queryDB(userObj.email, Users=True)  # id = iTupl[6]
        print([val for val in userObj.__dict__.values()])

        form = forms.Register(formdata=request.form, obj=userObj)  # formdata=request.form, obj=userObj)
        if form.validate_on_submit():  # request.method == 'POST' and form.validate():
            pw, ln = request.form['password'], request.form['lastname']
            # add hashed pw to obj.
            pw_hash = generate_password_hash(pw)  # bcrypt.generate_password_hash(pw).decode('utf-8')
            # update pw in obj  print(val for val in userObj.__dict__.values())
            setattr(userObj, 'password', pw_hash) and setattr(userObj, 'lastname', ln)
            insertTup = tuple([val for val in userObj.__dict__.values()])
            print(insertTup)
            # Check for user in DB by query database by input email, and get current password from DB
            if qryRow:
                dbPW = qryRow[0][9]  # print(dbPW)
            # check db for existing users. if user does not exist, create user from form data.
            if not qryRow:
                # createUser = True - addUserdb((keys, values) for (keys, values) in userObj.__dict__.items())
                addUserdb(insertTup)
                print("user was added: " + str(insertTup[1] +" "+ str(insertTup[2])))
                flash("An account was created for: " + str(insertTup[0] +" "+ str(insertTup[1])))
                # create cookie/session for user
                session['user'], session['email'] = userObj.firstname, userObj.email
                #return redirect('/')
            # partial/soft registered user, get pw from DB, need add password and lastname
            elif userObj.email and not dbPW:  # user w email, no password
                # ** Need to change this to an update of existing user creds. **
                addUserdb(insertTup)
                flash("Password was added: " + str(insertTup[1]))
                # create cookie/session for user
                session['user'], session['email'] = userObj.firstname, userObj.email
                #return redirect('/comment')
            # there is an email and pw. Check pw. If incorrect pw, redirect to index for login.
            elif userObj.email and dbPW:
                # check password args: hash, and original pw
                ck_hash = check_password_hash(dbPW, pw)
                if ck_hash:  # flash("You are already registered, please login.")
                    flash("Welcome {}, you are logged in!".format(userObj.firstname))
                    # set cookie for user.
                    if not session['email'] == userObj.email:
                        session['user'], session['email'] = userObj.firstname, userObj.email
                    return redirect('/')
                else:
                    # login again password is incorrect.
                    flash('Incorrect Password Entered, login again.')
                    return redirect('/')
            return redirect('/')
        # form = forms.Register(formdata=request.form)
        userObj.firstname, userObj.email = form.firstname.data, form.email.data
        return render_template('login.html', form=form)

# edit table from database
@app.route('/editComm', methods=['GET', 'POST'])
def editComm():
    if request.method == 'POST':
        if request.form['action'] == 'Filter by Name':
            print(request.form['name'])
            id = request.form['name']
            # process the items from the db to the Table digestible format
            dbRes = queryDB(id, Users=False)
    else:
        # Setup Cards for each comment with option to delete by card.
        values = []
        # process the items from the db to the Table digestible format
        dbRes = queryDB(None)
        # loop and add all of clients to items list as objects
        if dbRes:
            for i, it in enumerate(dbRes):
                #  instantiate the Item class with individual item objects. Ignore comment responses for now.
                if not it[5]:
                    tabValues = models.Comment(it[0], it[1], strTime(it[2]), it[3], it[4], it[5], it[6])
                    values.append(list(tabValues.__dict__.values()))
                    # loop comments, add any resp. to list. Nest a loop to pull out assc. resp.
                    for rp in dbRes:  #Cond. = name+date  set up a sql query
                        if rp[5]:
                            if it[4] + str(it[2]) == rp[5] + str(rp[6]):
                                rpValues = models.Comment(rp[0], rp[1], rp[2], rp[3], rp[4], rp[5], strTime(rp[6]))
                                values.append(list(rpValues.__dict__.values()))
        #print((f.given_name, f.given_name) for f in values)
        # form to ask to review all claims or submit a claim with two buttons.
        form = forms.ChooseName(formdata=request.form, obj=values)  # formdata=request.form
        # populate form dropdown with name to query. Vals are only values not object.
        form.name.choices = [(f[0], f[4]) for f in values]
        #
        if form.validate_on_submit():
            return redirect('editComment.html')
        return render_template('editComment.html', form=form, values=values)

# delete spec comments.
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    try:
        # Postgres DB conn  #conn = sqlite3.connect(sqlLoc)
        print("attempt to delete user by comment id: " + str(id))
        conn = connPgres()
        c = conn.cursor()  # client_id, firstname, lastname, city, state, age, gender, xCoord, yCoord, date
        comm_id = (id,)
        c.execute(
            '''DELETE FROM comments WHERE comm_id=%s''', comm_id)  # user_id,
        conn.commit()
        flash('Comment was deleted successfully!')
        c.close()
        conn.close()
        # confirm comment deleted
        #form = forms.ChooseName(formdata=request.form, obj=comm_id)
        if not queryDB(comm_id, Users=False):
            return editComm()  # render_template('editComment.html', form=form)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.clear()
        '''for key in session.keys():
            session.pop(key, None)'''
    flash("You have been logged out!")
    return redirect('/')