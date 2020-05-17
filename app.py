import os

from collections import deque

from flask import Flask, render_template, request, session, redirect
from time import localtime, strftime
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret"
socketio = SocketIO(app, manage_session=False)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#keep track of logged in users
usersLogged =[]

#keep track of rooms and it's users
roomsCreated = []

#store all the rooms
list_of_rooms = []

#store the messages of a channel in a key-value form
roomMessages = dict()

#-----------login---------------
@app.route("/")
def login():
    return render_template("login.html")

#-----------logout---------------
@app.route("/logout", methods=["GET"])
def logout():
    
    usersLogged.remove(session.get("name"))

    session.clear()
    print("logged out")
    return redirect("/")

#----------create new room----------
@app.route("/join", methods=["POST", "GET"])
def join():

    name = request.form.get("name")
    session["name"] = name

    # if name in usersLogged:
    #     return "User already exists!"
    
    usersLogged.append(name)

    session.permanent = True
    return render_template("join.html", user=session.get("name"))

@app.route("/checkjoin", methods=["POST"])
def checkjoin():

    room = request.form.get("room")
    session["current_room"] = room

    # if room in roomsCreated:
    #     return redirect("/chat")
    # else:
    #     return "Room does not exist!"

    if room in roomsCreated:
        return "Room already exists!"

    roomsCreated.append(session.get("current_room"))
    return redirect("/chat")

    


#---------when a user creates a new room, check if the room already exixts-------------------
@app.route("/create", methods=["POST", "GET"])
def create():

    new_room = request.form.get("new_room")
    session["current_room"] = new_room

    if request.method == "POST":
        if new_room in roomsCreated:
            return "That room already exists!"

    roomsCreated.append(session.get("current_room"))

    return redirect("/chat")


#------------chat page---------------
@app.route("/chat", methods=["POST", "GET"])
def chat():

    
    user = session.get("name")

    # if room in roomsCreated:
    #     return "room already exists!"
    
    #add users to this particular room
    
        #roomsCreated[session.get("current_room")] = [session.get("name")]


    roomMessages[session.get("current_room")] = deque()
    print('\n\n')
    print(roomsCreated)
    print('\n\n')
    return render_template("chat.html", 
                            user=user,
                            room=session.get("current_room"),
                            rooms=roomsCreated, 
                            messages=roomMessages[session.get("current_room")]
                            )


# ---------update session of channel on click--------
@app.route("/room/<string:room>")
def room_update(room):
     
     session["current_room"] = room 
     return render_template("chat.html", room=session.get("current_room"), rooms=roomsCreated, messages=roomMessages[session.get("current_room")])


@socketio.on("joined")
def joined():
    username = session.get("name")
    room = session.get("current_room")
    join_room(room)
    emit("announce join", {"username": username}, room=room)

@socketio.on("leave")
def leave():
    username = session.get("name")
    room = session.get("current_room")
    leave_room(room)
    roomsCreated[session.get("current_room")].remove(room)
    emit('left', {"username": username}, room=room)

@socketio.on("send")
def send(data):
    txt = data["txt"]
    username = session.get("name")
    room = session.get("current_room")

    if len(roomMessages[room]) >100:
        #pop the oldest messages
        roomMessages.popleft()

    roomMessages[room].append([ strftime("%b-%d %I:%M%p", localtime()), username, txt])

    emit("recieve", {"txt": txt, "username": username, "time_stamp": strftime("%b-%d %I:%M%p", localtime())}, room=room, broadcast=True) 