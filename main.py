from flask import Flask, jsonify, request, redirect
import dataset
from algorithm import *
app = Flask(__name__)

db = dataset.connect('postgresql://postgres:postgres@localhost:5432/mydatabase')
users = db['users']
urls = db['urls']
urls.create_column('url', db.types.text)
urls.create_column('hits', db.types.integer)
urls.create_column('user_fk', db.types.integer)
db.query("ALTER TABLE urls ADD FOREIGN KEY (user_fk) REFERENCES users(id);")
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
    results = users.find_one(username = userId)
    if results == None:
        result = {'':''}
        return jsonify(result), 404
    else:
        long_url = request.json["url"]
        short_url = ''
        [n] = db.query("INSERT INTO urls (url,hits, user_fk) VALUES (:long_url, 0, :user_fk) RETURNING id", long_url=long_url, user_fk= results['id'])
        short_url = encode(n['id'])
        data = dict(id = n['id'], shorturl = short_url)
        urls.upsert(data, ['id'])
        result = {'id':"{}".format(n['id']), "hits": 0, "url": long_url, "shortUrl": "http://localhost:5000/urls/{}".format(short_url)}
        return jsonify(result), 201

@app.route("/urls/<id>", methods=["GET"])
def get_redirect(id):
    results = urls.find_one(shorturl = str(id))
    if results == None:
        result = {'':''}
        return jsonify(result), 404
    else:
        data = dict(id = results['id'], hits = results['hits'] + 1, shorturl = str(id))
        urls.update(data, ['id'])
        return redirect(results['url']), 301

@app.route("/stats/<id>", methods=["GET"])
def get_stats_id(id):
    results = urls.find_one(shorturl = str(id))
    if results == None:
        result = {'':''}
        return jsonify(result), 404
    else:
        result = {'id': results['id'], "hits": results['hits'], "url": results['url'], "shortUrl": "http://localhost:5000/urls/{}".format(results['shorturl'])}
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)