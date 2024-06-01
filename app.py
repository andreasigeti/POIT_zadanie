import serial
from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import MySQLdb
import time
import configparser as ConfigParser
import json

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

ser = None 
count = 0

config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)



def background_thread(args):
    global count
    innerCount = 0
    dataCounter = 0 
    dataList = []
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    while True:
#         try:
#             if ser is not None and ser.isOpen() and ser.in_waiting > 0:
#                 data = ser.readline().decode().strip()
#                 if not data:
#                     data = ""
#                 else:
#                     data = data.split(',')
# 
#                 argsData = dict(args).get('A', -1)
#                 dbData = dict(args).get('db_value', -1)
# 
#                 print(dbData)
#                 if dbData == "start":
#                     innerCount += 1
#                     dataDict = {
#                         "t": time.time(),
#                         "x": count,
#                         "data": data}
#                     dataList.append(dataDict)
#                 else:
#                     if len(dataList)>0:
#                         replacedDataList = str(dataList).replace("'", "\"")
#                         cursor = db.cursor()
#                         cursor.execute("INSERT INTO zadanieDB (senzor) VALUES (%s)", (str(replacedDataList),))
#                         db.commit()
#                         print("DataList: "+dataList)
# 
#                         replacedDataList = json.dumps(dataList)
#                         fo = open("files/hodnoty.txt","a+")    
#                         fo.write("%s\r\n" %replacedDataList)
#                     dataList = []
#                     innerCount = 0
#                     
#                     
#                     
#                 if argsData == 0:
#                     count = 0
#                 elif argsData == 1:
#                     count += 1
# 
#                 socketio.emit('my_response',
#                        {"data": data, 'count': count},
#                        namespace='/test')
#         except:
#             print("Exception occurred")

        try:
            if ser is not None and ser.isOpen() and ser.in_waiting > 0:
                data = ser.readline().decode().strip()
                if not data:
                    data = ""
                else:
                    data = data.split(',')

                argsData = dict(args).get('A', -1)
                dbData = dict(args).get('db_value', -1)

                print(dbData)
                if dbData == "start":
                    innerCount += 1
                    dataDict = {
                        "t": time.time(),
                        "x": count,
                        "data": data}
                    dataList.append(dataDict)
                else:
                    if len(dataList)>0:
                        replacedDataList = str(dataList).replace("'", "\"")
                        cursor = db.cursor()
                        cursor.execute("INSERT INTO zadanieDB (senzor) VALUES (%s)", (str(replacedDataList),))
                        db.commit()
                        print("data: %s",replacedDataList)

                        #replacedDataList = json.dumps(dataList)
                        fo = open("static/files/test.txt","a+")
                        fo.write("%s\r\n" %replacedDataList)
                        fo.close()
                    dataList = []
                    innerCount = 0
                    
                    
                    
                if argsData == 0:
                    count = 0
                elif argsData == 1:
                    count += 1

                socketio.emit('my_response',
                       {"data": data, 'count': count},
                       namespace='/test')
        except:
             print("Exception occurred")
        socketio.sleep(1)
    db.close()

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    session['A'] = message['value']
    #emit('my_response',
     #    {'data': message['value'], 'count': session['receive_count']})

@app.route('/db')
def db():
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  cursor.execute('''SELECT senzor FROM zadanieDB WHERE id=1''')
  rv = cursor.fetchall()
  return str(rv)

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print("..............")
  print(num)
  cursor.execute("SELECT senzor FROM zadanieDB WHERE id=%s",(num,))
  rv = cursor.fetchone()
  return str(rv[0])

@socketio.on('db_event', namespace='/test')
def db_message(message):
    session['db_value'] = message['value']

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    global ser, count
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    if ser is not None:
        ser.close()  
        ser = None
    count = 0  
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global ser, count
    if ser is None:
        ser = serial.Serial("/dev/ttyS0", 9600)
    count = 0 
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    global ser, thread
    if ser is not None:
        ser.close()
        ser = None
    thread = None
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
