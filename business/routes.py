from flask import session, jsonify
from app import app
from business.models import Business

@app.route('/user/signup', methods=["POST"])
def signup():
    return Business().signup()


@app.route('/user/signout')
def signout():
    return Business().signout()

@app.route('/user/login', methods=["POST"])
def login():
    return Business().login()
