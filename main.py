from flask import Flask, jsonify, request, render_template, Response
import dataset
from algorithm import *
app = Flask(__name__)

db = dataset.connect('postgresql://postgres:postgres@localhost:5432/mydatabase')
users = db['users']
urls = db['urls']
urls.create_column('url', db.types.text)
urls.create_column('hits', db.types.integer)
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

@app.route("/users/<userId>", methods=["DELETE"])
def delete(userId):
    if users.find_one(username = userId):
        users.delete(username = userId)
        result = {'':''}
        return jsonify(result), 200
    else:
        result = {'':''}
        return jsonify(result), 404

@app.route("/users/<userId>/urls", methods=["POST"])
def post(userId):
    if not users.find_one(username = userId):
        result = {'':''}
        return jsonify(result), 404
    else:
        long_url = request.json["url"]
        short_url = ''
        [n] = db.query("INSERT INTO urls (url,hits) VALUES (:long_url, 0) RETURNING id", long_url=long_url)
        short_url = encode(n['id'])
        data = dict(id = n['id'], shortUrl = short_url)
        urls.upsert(data, ['id'])
        result = {'id':"{}".format(n['id']), "hits": 0, "url": long_url, "shortUrl": "http://localhost:5000/urls/{}".format(short_url)}
        return jsonify(result), 201

@app.route("/urls/<id>", methods=["GET"])
def get_redirect(id):
        if not urls.find_one(id = str(id)):
            result = {'':''}
            return jsonify(result), 404


if __name__ == '__main__':
    app.run(debug=True)