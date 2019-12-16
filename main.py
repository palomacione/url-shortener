from flask import Flask, jsonify, request, redirect
import dataset
import os
import markdown
from algorithm import *
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
db = dataset.connect('postgresql://postgres:postgres@localhost:5432/my_database')
users = db.query("CREATE TABLE IF NOT EXISTS public.users (id serial, username text,  CONSTRAINT users_pkey PRIMARY KEY (id))")
users = db.get_table('users')
urls = db.query("CREATE TABLE IF NOT EXISTS public.users (id serial, CONSTRAINT urls_pkey PRIMARY KEY (id))")
urls = db.get_table('urls')
urls.create_column('url', db.types.text)
urls.create_column('shorturl', db.types.text)
urls.create_column('hits', db.types.integer)
urls.create_column('user_fk', db.types.integer)
db.query("ALTER TABLE urls ADD FOREIGN KEY (user_fk) REFERENCES users(id) ON DELETE SET NULL;")
@app.route("/")
def main_page():
    with open(os.getcwd() + '/README.md', 'r') as markdown_file:
        content = markdown_file.read()
        return markdown.markdown(content)

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

@app.route("/urls/<id>", methods=["GET", "DELETE"])
def get_redirect(id):
    results = urls.find_one(shorturl = str(id))
    if results == None:
            result = {'':''}
            return jsonify(result), 404
    else:
        if request.method == "GET":
            data = dict(id = results['id'], hits = results['hits'] + 1, shorturl = str(id))
            urls.update(data, ['id'])
            return redirect('https://{}'.format(results['url'])), 301
        else:
            urls.delete(shorturl = results['shorturl'])
            result = {'':''}
            return jsonify(result)

@app.route("/stats/<id>", methods=["GET"])
def get_stats_id(id):
    results = urls.find_one(shorturl = str(id))
    if results == None:
        result = {'':''}
        return jsonify(result), 404
    else:
        result = {'id': results['id'], "hits": results['hits'], "url": results['url'], "shortUrl": "http://localhost:5000/urls/{}".format(results['shorturl'])}
        return jsonify(result)

@app.route("/users/<userid>/stats", methods=["GET"])
def get_stats_user(userid):
    if users.find_one(username = userid) == None:
        result = {'':''}
        return jsonify(result), 404
    else:
        username_to_id = users.find_one(username = userid)
        results = db.query("SELECT SUM(hits), COUNT(id) FROM urls WHERE urls.user_fk = {}".format(username_to_id['id']))
        result_list = []
        for r in results:
            result_list.append(r)
        top10 = db.query("SELECT id, hits, url, shorturl FROM urls WHERE urls.user_fk = {} ORDER BY hits DESC LIMIT 10".format(username_to_id['id']))
        top10_list = []
        for url in top10:
            top10_list.append(url)
        result = {"hits": result_list[0]['sum'], "urlCount": result_list[0]['count'], "topUrls": top10_list}
        return jsonify(result)

@app.route("/stats", methods=["GET"])
def get_stats():
    results = db.query("SELECT SUM(hits), COUNT(id) FROM urls")
    result_list = []
    for r in results:
        result_list.append(r)
    top10 = db.query("SELECT id, hits, url, shorturl FROM urls ORDER BY hits DESC LIMIT 10")
    top10_list = []
    for url in top10:
        url['shorturl'] = 'http://localhost:5000/urls/{}'.format(url['shorturl'])
        top10_list.append(url)

    result = {"hits": result_list[0]['sum'], "urlCount": result_list[0]['count'], "topUrls": top10_list}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False)