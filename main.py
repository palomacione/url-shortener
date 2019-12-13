from flask import Flask, jsonify, request, render_template, Response
import dataset
app = Flask(__name__)

db = dataset.connect('postgresql://postgres:postgres@localhost:5432/mydatabase')
users = db['users']

@app.route("/")
def main_page():
    return {"hello": "world"}

@app.route("/users", methods=["POST"])
def add_user():
    id = request.json['id'] 
    if users.find_one(username = id):
        result = {'id': id}
        return jsonify(result), 409
    else:
        users.insert(dict(username = id))
        result = {'id': id}
        return jsonify(result), 201

if __name__ == '__main__':
    app.run(debug=True)