from flask import Flask, jsonify, render_template, request
import json

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def hello_world():
    return 'Hello, World!\n'

welcome = "Welcome to 3ESE API!"

@app.route('/api/welcome/', methods=['GET','POST'])
def api_welcome():
    return welcome
    
@app.route('/api/welcome/<int:index>', methods=['GET','POST'])
def api_welcome_index(index):
    return json.dumps({"index": index, "val": welcome[index]}), {"Content-Type": "application/json"}

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


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
