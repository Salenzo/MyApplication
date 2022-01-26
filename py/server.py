from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.jinja_env.auto_reload = True

io = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pattern')
def pattern():
    return render_template('pattern.html')

@io.on('connect')
def connect():
    print('connect')


@io.on('disconnect')
def disconnect():
    print('disconnect')


t = 1


@io.on('update')
def update():
    global t
    t += 1
    io.emit('update', t)


if __name__ == '__main__':
    io.run(app, debug=True)
