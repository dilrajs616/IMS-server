from flask import session, jsonify
from app import app
from employee.models import Employee

@app.route("/user_info")
def user_info():
    return Employee().user_info()


@app.route('/user/add_employee', methods=["POST"])
def create():
    return Employee().add_employee()


@app.route("/business/fetch_employees")
def fetch_employees():
    return Employee().fetch_employees()
    

@app.route("/user/edit_details", methods=["POST"])
def change_password():
    return Employee().edit_employee_info()
    

@app.route('/user/remove', methods=["POST"])
def delete():
    return Employee().remove_employee()

