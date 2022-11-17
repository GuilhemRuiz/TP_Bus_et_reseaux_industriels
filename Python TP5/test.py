from flask import Flask, jsonify, render_template, request
import json
import serial
import sqlite3

bddTemp = '''CREATE TABLE IF NOT EXISTS HISTOTEMP (
                id INTEGER NOT NULL PRIMARY KEY,
                temperature FLOAT);'''


def insererValTab(value):
        try:
                conn = sqlite3.connect('bdd.db')
                cur = conn.cursor()
                cur.execute(bddTemp)
                addvalues = "INSERT INTO HISTOTEMP (bddTemp) VALUES (?)"
                values = (value)
                cur.execute(addvalues, values)
                conn.commit()
                cur.close()
                conn.close()
                print("valeur insérée dasn la bdd !")
        except sqlite3.Error as error:
            print("Erreur lors de l'insertion dans la table HISTOTEMP", error)


app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def hello_world():
    return 'Hello, World!\n'

welcome = "Welcome to 3ESE API!"

""" @app.route('/api/welcome/', methods=['GET','POST'])
def api_welcome():
    return welcome """
    
""" @app.route('/api/welcome/<int:index>', methods=['GET','POST'])
def api_welcome_index(index):
    return json.dumps({"index": index, "val": welcome[index]}), {"Content-Type": "application/json"} """


@app.route('/api/welcome/', methods=['GET', 'POST','DELETE'])
def api_welcome():
        global welcome
        if request.method=='POST':
                welcome = request.get_json()['data']
                return "", 202
        if request.method=='DELETE':
                welcome = ''
                return "", 205
        return jsonify({"text": welcome})

@app.route('/api/welcome/<int:index>', methods=['GET', 'PUT','PATCH', 'DELETE'])
def api_welcome_index(index):
        global welcome
        if request.method == 'GET':
                return jsonify({"index": index, "val": welcome[index]})
        if request.method == 'PUT':
                welcome = welcome[:index]+ " " + request.get_json()['data'] + " " +  welcome[index+1:]
                return "", 202
        if request.method == 'PATCH':
                welcome = welcome[:index]+ request.get_json()['data'] + welcome[index+1:]
                return "", 202
        if request.method == 'DELETE':
                welcome = welcome[:index] + welcome[index+1:]
                return "", 205


@app.route('/api/request/', methods=['GET', 'POST'])
@app.route('/api/request/<path>', methods=['GET','POST'])
def api_request(path=None):
    resp = {
            "method":   request.method,
            "url" :  request.url,
            "path" : path,
            "args": request.args,
            "headers": dict(request.headers),
    }
    if request.method == 'POST':
        resp["POST"] = {
                "data" : request.get_json(),
                }
    if request.method == 'GET':
        resp = request.url

    return jsonify(resp)

@app.route('/api/request/temp/', methods=['GET', 'POST'])
def request_temp():
        if request.method == 'GET':
                ser = serial.Serial('/dev/ttyAMA0')
                ser.baudrate = 115200
                ser.close()   
                ser.open()
                ser.write(5)
                test = ser.write(5)
                print(test)
                temp = ser.read()
                insererValTab(temp)
                return temp, 205




@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

