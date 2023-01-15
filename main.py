import os
FAUNA_SECRET = os.environ.get('FAUNA_SECRET')

import flask
from flask import request

import faunadb
from faunadb import query as q
from faunadb.client import FaunaClient

# from autoscraper import AutoScraper


app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/signup', methods=['POST'])
def signup():

    body = request.json
    client = FaunaClient(secret=FAUNA_SECRET)

    try:
        result = client.query(
            q.create(
                q.collection("Users"),
                {
                    "data": {
                        "username": body["username"]
                    },
                    "credentials": {
                        "password": body["password"]
                    }
                }
            )
        )

        return {
            "userId": result['ref'].id()
        }

    except faunadb.errors.BadRequest as exception:
        error = exception.errors[0]
        return {
            "code": error.code,
            "description": error.description
        }, 409

@app.route('/login', methods=['POST'])
def login():

    body = request.json
    client = FaunaClient(secret=FAUNA_SECRET)

    try:
        result = client.query(
            q.login(
                q.match(
                    q.index("Users_by_username"),
                    body["username"]
                ),
                {"password": body["password"]}
            )
        )

        return {
            "secret": result['secret']
        }

    except faunadb.errors.BadRequest as exception:
        error = exception.errors[0]
        return {
            "code": error.code,
            "description": error.description
        }, 401

@app.route('/things', methods=['GET'])
def things():

    userSecret = request.headers.get('fauna-user-secret')
    client = FaunaClient(secret=userSecret)

    try:
        result = client.query(
            q.map_(
                q.lambda_("ref", q.get(q.var("ref"))),
                q.paginate(q.documents(q.collection("Things")))
            )
        )

        things = map(
            lambda doc: {
                "id": doc["ref"].id(),
                "name": doc["data"]["name"],
                "color": doc["data"]["color"]
            },
            result["data"]
        )

        return {
            "things": list(things)
        }

    except faunadb.errors.Unauthorized as exception:
        error = exception.errors[0]
        return {
            "code": error.code,
            "description": error.description
        }, 401

# @app.route('/meir_test', methods=['GET'])
# def things():

#     url = 'https://www.etsy.com/search?q=macbook'

#     wanted_dict = {
#         'title': [
#             'Apple MacBook Pro i9 32GB 500GB Radeon 560X 15.4 2018 Touch Bar 2.9GHz 6-Core', 
#             'Laptop MacBook Premium Ergonomic Wood Stand Holder Computer Gift Nerd Tech Geek Mens, woodworking gift, Home office workspace accessories',
#         ],
#         'price': ['1,500.00', '126.65'],
#         'url': ['851553172']
#     }

#     scraper = AutoScraper()
#     scraper.build(url=url, wanted_dict=wanted_dict)

#     # get results grouped per rule so we'll know which one to use 
#     scraper.get_result_similar(url, grouped=True)

#     try:
#         return {
#             "get_result_similar": scraper.get_result_similar(url, grouped=True)
#         }

#     except faunadb.errors.Unauthorized as exception:
#         error = exception.errors[0]
#         return {
#             "code": error.code,
#             "description": error.description
#         }, 401

# app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))


# curl -i -d '{"username":"meir", "password": "secretmeir"}' -H 'Content-Type: application/json' -X POST http://0.0.0.0:8080/signup

# curl -i -d '{"username":"meir", "password": "secretmeir"}' -H 'Content-Type: application/json' -X POST http://0.0.0.0:8080/login

# curl -i -H 'fauna-user-secret: fnEE6TTSaJAA1wTpMxKkEAjXiN6anK8BcKfYNLGGP2Icct00Xpg' -X GET http://0.0.0.0:8080/things


# curl -i -H 'fauna-user-secret: fnEE6TTSaJAA1wTpMxKkEAjXiN6anK8BcKfYNLGGP2Icct00Xpg' -X GET http://0.0.0.0:8080/meir_test

meir_test


# vi ~/.bash_profile  
# alias python='/opt/homebrew/bin/python3'