from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

app = Flask(__name__)
app.debug=True
app.config['SECRET_KEY'] = 'secret' # to maintain sessions
# to communicate with socketIO
app.config['SESSION_TYPE'] = 'filesystem'  # reddis

# defining session
Session(app)

socketio = SocketIO(app, manage_session=False) # flask will manage our session

@app.route('/', methods=['GET','POST'])
def index():
	return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # Get username & room from login request
    if(request.method=='POST'):
        username = request.form['username']
        room = request.form['room']

        #Store the data in session
        session['username'] = username
        session['room'] = room 
        return render_template('chat.html', session = session)
    
    #reloading the page
    else:
        # user logged in already
        if(session.get('username') is not None):
            return render_template('chat.html', session = session)
        # go to login page
        else:
            return redirect(url_for('index'))


#socketio route definitions
@socketio.on('join', namespace='/chat')  # namespace to execute on a given page
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg':  session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)

if __name__ == '__main__':
	# app.run()
	socketio.run(app) # to run the app from socketio
