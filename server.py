
from flask import Flask, flash, request, redirect, url_for,render_template,session
from flask_pymongo import PyMongo
import os,os.path
import bcrypt
import socket
from tkinter import *
from tkinter.filedialog import askopenfilenames
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_addr=s.getsockname()[0]
s.close()
app = Flask(__name__, static_url_path='/static')
app.secret_key = '?&Kjhd$^ljm>x21'
app.config['MONGO_DBNAME'] = 'FacultyLogin'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/FacultyLogin'
mongo = PyMongo(app)  

import db as db
import db as ab

@app.route('/', methods=['POST','GET'])
def home():
    if 'username' in session:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user['username']==login_user['username']:
            return render_template('/admin/admin.html',username=name)
        
        return render_template('details.html',username=name)
    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if 'username' in session:
        return """<center><h2>Please logout to login as another user...<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        alert="alert"
        if request.method == 'POST':
            users = mongo.db.users
            login_user = users.find_one({'username' : request.form['UserName']})
            login_mail=users.find_one({'mailid': request.form['UserName']})
            if login_user:
                if bcrypt.hashpw(request.form['Password'].encode('utf-8'), login_user['password']) == login_user['password']:
                    user = login_user['username']
                    session['username'] = user
                    return redirect(url_for('home'))
            elif login_mail:
                if bcrypt.hashpw(request.form['Password'].encode('utf-8'), login_mail['password']) == login_mail['password']:
                    user = login_mail['username']
                    session['username'] = user
                    return redirect(url_for('home'))
            flash("Username or Password is invalid")
        return render_template("login.html",failed=alert)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return """<center><h2>Please logout to register as a new user...<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        alert="alert"
        if request.method == 'POST':
            users = mongo.db.users
            OTPS = mongo.db.OTPS
            Admin = users.find_one({'username' : 'ADMIN'})
            if(Admin):
                Admin_mailid = Admin['mailid']
                passcode = OTPS.find_one({'mailid': Admin_mailid})
            existing_user = users.find_one({'username' : request.form['UserName']})
            existing_mail= users.find_one({'mailid': request.form['Mailid']})
            # if request.form['UserName']== "ADMIN" or (passcode and (bcrypt.hashpw(request.form['passcode'].encode('utf-8'), passcode['OTP'])) == passcode['OTP']):
            if existing_user is None and existing_mail is None:
                hashpass = bcrypt.hashpw(request.form['Password'].encode('utf-8'), bcrypt.gensalt())
                users.insert_one({'username' : request.form['UserName'], 'password' : hashpass , 'firstname' : request.form['First_Name'] , 'lastname' : request.form['Last_Name'], 'mailid': request.form['Mailid']})
                flash('successfully registered ...')
                return render_template("login.html",passed=alert)
            flash('Username or Mailid is already exist')
            return render_template('register.html')
            # flash('Invalid Passcode')
        return render_template('register.html')

@app.route("/forgot",methods=['POST','GET'])
def forgot():
    if 'username' in session:
        return """<center><h2>Unautnorised Access found please logout and try again...<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        if request.method == 'POST':
            users = mongo.db.users
            OTPS = mongo.db.OTPS
            mailid = request.form['mailid']
            valid_mailid = users.find_one({'mailid' : request.form['mailid']})
            existing_mail = OTPS.find_one({'mailid' : request.form['mailid']})
            if valid_mailid:
                OTPO = mail(mailid,1)
                OTP = bcrypt.hashpw(OTPO.encode('utf-8'), bcrypt.gensalt())
                if existing_mail:
                    OTPS.update_one({'mailid' : request.form['mailid']},{"$set" : {"OTP": OTP}})
                else:
                    OTPS.insert_one({'OTP' : OTP , 'mailid' : request.form['mailid']})
                return render_template("resetpassword.html",mailid = mailid)
            flash('Invalid Mail id')
        return render_template("forgot.html")


@app.route("/resetpassword",methods=['POST','GET'])
def reset():
    if 'username' in session:
        return """<center><h2>Unautnorised Access found...<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        alert="alert"
        if request.method == 'POST':
            users = mongo.db.users
            OTPS = mongo.db.OTPS
            User_mail = OTPS.find_one({'mailid': request.form['mailid']})
            if User_mail:
                if(bcrypt.hashpw(request.form['OTP'].encode('utf-8'), User_mail['OTP'])) == User_mail['OTP']:
                    newpassword = bcrypt.hashpw(request.form['Password'].encode('utf-8'), bcrypt.gensalt())
                    users.update_one({'mailid':request.form['mailid']},{"$set":{"password":newpassword}})
                    OTPS.remove({'mailid':request.form['mailid']},True)
                    flash('Password reset successfull')
                    return render_template("login.html",passed=alert)
                flash('Invalid OTP')
            return render_template("resetpassword.html",mailid = User_mail['mailid'])
        else:
            return """<center><h2>Unautnorised Access found...<br><br> Click <a href="/">here</a> to Go back</h2></center>"""

@app.route("/logout",methods=["POST","GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route('/admin_page',methods=['GET','POST'])
def admin_page():
    if 'username' in session:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user["username"] == login_user["username"]:
            return render_template('/admin/admin.html',username=name)
        else:
            return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""


@app.route('/Delete_Notes_page',methods=['GET','POST'])
def Delete_Notes_page():
    if 'username' in session:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user["username"] == login_user["username"]:
            from pymongo import MongoClient
            client = MongoClient("mongodb://localhost:27017/")
            usrnm=login_user["username"]
            db = client[usrnm]
            collection = db["notes"]
            documents = collection.find()
            for doc in documents:
                print(doc)
                string="\n"+str(doc)
            try:
                flash("Notes available:"+string)
            except:
                flash("No Notes available  for user"+login_user["username"])
            return render_template('/admin/Delete_Encodes.html',username=name)
        else:
            return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""


@app.route("/Delete_Note",methods=['GET','POST'])
def Delete_Note():
    dep=request.form["department"]
    try:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        from pymongo import MongoClient
        from bson.objectid import ObjectId
        client = MongoClient("mongodb://localhost:27017/")
        usrnm=login_user["username"]
        db = client[usrnm]
        collection = db["notes"]
        doc_id=str(dep)
        collection.delete_one({"_id": ObjectId(doc_id)})
        flash("Note Deleted successfully for ID"+dep)
        return redirect(url_for("Delete_Notes_page") )
    except Exception as e:
        flash(e)
        return redirect(url_for("Delete_Notes_page") )


@app.route('/Search_Notes_page',methods=['GET','POST'])
def Search_Notes_page():
    if 'username' in session:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user["username"] == login_user["username"]:
            return render_template('/admin/Generate_Encodes.html',username=name)
        else:
            return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""


@app.route('/Search_Notes',methods=['GET','POST'])
def Search_Notes():
    try:
        keyword=request.form["department"]
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        from pymongo import MongoClient
        from bson.objectid import ObjectId
        client = MongoClient("mongodb://localhost:27017/")
        usrnm=login_user["username"]
        db = client[usrnm]
        collection = db["notes"]
        documents = collection.find({"Note": {"$regex": keyword}})
        for doc in documents:
            print(doc)
            srchwd="\n"+str(doc)
        return render_template('/admin/Generate_Encodes.html',Srchwrd=srchwd)
    except:
        return render_template('/admin/Generate_Encodes.html',Srchwrd="No such note found with entered keyowrd")

@app.route("/Save_Note",methods=['GET','POST'])
def Save_Note():
    note=request.form["content"]
    try:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        usrnm=login_user["username"]
        content=note
        db.dbforusr(usrnm,content)
        return redirect(url_for("admin_page") )
    except Exception as e:
        flash(e)
        return redirect(url_for("admin_page") )

@app.route('/Update_Notes_page',methods=['GET','POST'])
def Update_Notes_page():
    if 'username' in session:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user["username"] == login_user["username"]:
           
            return render_template('/admin/Update_Encodes.html',username=name)
        else:
            return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""


@app.route('/Update_Note',methods=['GET','POST'])
def Update_Note():
    if 'username' in session:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        from pymongo import MongoClient
        from bson.objectid import ObjectId
        client = MongoClient("mongodb://localhost:27017/")
        usrnm=login_user["username"]
        db = client[usrnm]
        collection = db["notes"]
        ID=request.form["department"]
        content=request.form["Message"]
        content=str(content)
        new_data = {"$set": {"Note": content}}
        collection.update_one({"_id": ObjectId(ID)}, new_data)
        try:
            flash("Note Updates successfully for ID"+ID)
            return redirect(url_for("Update_Notes_page") )
        except:
            flash("No note found for ID"+ID)
            return redirect(url_for("Update_Notes_page") )


@app.route('/Share_Notes_page',methods=['GET','POST'])
def Share_Notes_page():
    if 'username' in session:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        name=login_user["firstname"]+" "+login_user["lastname"]
        if login_user["username"] == login_user["username"]:
           
            return render_template('/admin/Share_Notes.html',username=name)
        else:
            return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""
    else:
        return """<center><h2>Unautnorised Access found... You are not an admin<br><br> Click <a href="/">here</a> to Go back</h2></center>"""


@app.route('/Share_Note',methods=['GET','POST'])
def Share_Note():
    if 'username' in session:
        users = mongo.db.users
        login_user = users.find_one({'username' : session['username']})
        from pymongo import MongoClient
        from bson.objectid import ObjectId
        client = MongoClient("mongodb://localhost:27017/")
        usrnm=login_user["username"]
        db = client[usrnm]
        collection = db["notes"]
        ID=request.form["department"]
        documents = collection.find_one({"_id": ObjectId(ID)})
        plug=documents["Note"]
        usrid=request.form["Message"]
        usrid=str(usrid)
        ab.dbforshr(usrid,plug)
    try:
        flash("Note Shared successfully for ID"+usrid)
        return redirect(url_for("Share_Notes_page") )
    except:
        flash("No User found for ID"+usrid)
        return redirect(url_for("Share_Notes_page") )
        
if __name__ == "__main__":
    app.run(host=ip_addr,port="5000",use_reloader=True,debug=True)
