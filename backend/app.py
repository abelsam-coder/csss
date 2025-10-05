from flask import Flask,request,session,jsonify
from flask_bcrypt import Bcrypt,generate_password_hash,check_password_hash
from flask_session import Session
from flask_mail import Mail,Message
from flask_dance.contrib.google import google,make_google_blueprint
from flask_socketio import SocketIO,emit
from flask_cors import CORS
from datetime import datetime
import sqlite3
import uuid
import mimetypes
import base64
app = Flask(__name__)
CORS(app,supports_credentials=True)
app.config["SESSION_TYPE"] = 'filesystem'
app.secret_key = "secret"
Session(app)
bcrypt = Bcrypt(app)
@app.route('/logout',methods=["POST","GET"])
def logout():
    username = session.get("username")
    if username:
        session.pop("username")
        return jsonify({"status":"success","message":f"{username} out from session"})
    else:
        return jsonify({"status":"error","message":"no session found"})

@app.route('/signup',methods=["POST","GET"])
def signup():
    try:
        date = request.get_json()
        username = date.get("username")
        password = date.get("password")
        hash = bcrypt.generate_password_hash(password).decode()
        db = sqlite3.connect("../database/database.db")
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username,password) VALUES(?,?)",(username,hash))
            db.commit()
            session["username"] = username
            return jsonify({"status":"Success","message":f"Welcome user {username}"})
        except sqlite3.IntegrityError:
            return jsonify({"status":"error","message":f"username {username} is already exists"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})

@app.route('/delete/account',methods=["POST","GET"])
def delete_account():
    username = session.get("username")
    if username:
        db = sqlite3.connect("../database/database.db")
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?",(username,))
        db.commit()
        return jsonify({"status":"success","message":f"{username} is deleted"})
    else:
        return jsonify({"status":"error","message":"no session found"})    

@app.route('/login',methods=["POST","GET"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        db = sqlite3.connect("../database/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?",(username,))
        fetch = cursor.fetchone()
        if fetch and fetch[0]:
            check = bcrypt.check_password_hash(fetch[0],password)
            if check:
                session["username"] = username
                return jsonify({"status":"success"})
            else:
                return jsonify({"status":"error","message":"incorrect password"})
        else:
            return jsonify({"status":"error","message":"no user found"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})        
    
@app.route('/post',methods=["POST","GET"])
def post():
    try:
        username = session.get("username")
        if username:
            data = request.get_json()
            title = data.get("username")
            caption = data.get("caption")
            file = data.get("file")
            date = datetime.now().strftime("%B %A %y")
            filetype,_  = mimetypes.guess_extension(file.filename)
            encode = base64.b64encode(file.reade()).decode()
            html = f"data:{filetype};base64,{encode}"
            id = str(uuid.uuid4())
            db = sqlite3.connect("../database/database.db")
            cursor = db.cursor()
            cursor.execute("INSERT INTO post (title,caption,file,date,id,username) VALUES(?,?,?,?,?,?)",(title,caption,html,date,id,username))
            db.commit()
            return jsonify({"status":"success"})
        else:
            return jsonify({"status":"error","message":"you are not in session"}) 
          
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})      
@app.route('/delete/<string:id>',methods=["POST","GET"])
def delete_post(id):
    db = sqlite3.connect("../database/database.db")
    cursor = db.cursor()  
    try:
        cursor.execute("DELETE FROM post WHERE id = ?",(id,))
        db.commit()
        return jsonify({"status":"success"}) 
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})     
            
@app.route('/edit/<string:id>',methods=["POST","GET"])
def edit(id):
    db = sqlite3.connect("../database/database.db")
    cursor = db.cursor()  
    try:
        data = request.get_json()
        title = data.get("title")
        caption = data.get("caption")
        cursor.execute("UPDATE post SET title = ? AND caption = ? WHERE id = ?",(title,caption,id))
        db.commit()
        return jsonify({"status":"success"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)})   
    

                    
if  __name__ == "__main__":
    app.run()        