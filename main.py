import os
FAUNA_SECRET = os.environ.get('FAUNA_SECRET')

import flask
from flask import request

import faunadb
from faunadb import query as q
from faunadb.client import FaunaClient

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/signup', methods=['POST'])
def signup():
    json = request.json

    client = FaunaClient(secret=FAUNA_SECRET)
    result = client.query(
        q.create(
            q.collection("Users"),
            {
                "data": {
                    "user": json["user"]
                },
                "credentials": {
                    "password": json["password"]
                }
            }
        )
    )

    return {
        "userId": result['ref'].id()
    }

@app.route('/login', methods=['POST'])
def login():
    json = request.json

    client = FaunaClient(secret=FAUNA_SECRET)

    try:
        result = client.query(
            q.login(
                q.match(
                    q.index("Users_by_user"),
                    json["user"]
                ),
                {"password": json["password"]}
            )
        )

        print(result)

        return {
            "secret": result['secret']
        }

    except faunadb.errors.BadRequest as exception:
        error = exception.errors[0]
        return {
            "code": error.code,
            "description": error.description
        }, 401

    except:
        return {
            "code": "Server error",
            "description": "An unknown error has occurred"
        }, 500

app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))