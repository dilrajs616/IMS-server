from flask import jsonify, request, session
from passlib.hash import pbkdf2_sha256
from app import db
from sendmail import sendEmail
import asyncio

class Employee:

    def user_info(self):
        if "logged_in" in session:
            print(session)
            return jsonify({"user_info": session, "business_id": session["business_id"]})
        else:
            return jsonify({"user_info": {"logged_in": False}})
        
    def add_employee(self):

        name = request.json["name"]
        email = request.json["email"]
        role = request.json["role"]
        password = request.json["password"]
        business_id = session.get("business_id")

        employee_id = self.get_employee_id(business_id)

        if employee_id == None:
            return jsonify({"Error": "Business Id is not correct"})

        employee = {
            "employee_id": employee_id,
            "name" : name,
            "email": email,
            "password": password,
            "role": role
        }
        
        employee["password"] = pbkdf2_sha256.encrypt(employee['password'])
        
        if db.businesses.count_documents({"_id": business_id, "employees.email": employee['email'] }):
            return "Email Already exists", 201
        else:
            if db.businesses.update_one({'_id': business_id}, {'$push': {'employees': employee}}):
                asyncio.run(main(email, password, business_id))
                return jsonify({"success" : True}), 200
            else:
                return jsonify({"success": False, "message": "Failed to create employee"}), 500
    

    def fetch_employees(self):
        employee_list = []
        business_id = session.get("business_id")
        business = db.businesses.find_one({"_id": business_id})

        if business:
            employee_list = business.get("employees", [])
            employees_info = []
            for emp in employee_list:
                employee_info = {"name": emp["name"], "employee_id": emp["employee_id"], "email": emp["email"],"role": emp["role"]}
                employees_info.append(employee_info)

            return jsonify({"success": True,"employee_list": employees_info})
        else:
            return jsonify({"success": False, "error": "Could not fetch employees"})
            
    def edit_employee_info(self):
        name = request.json.get("name")
        email = request.json.get("email")
        role = request.json.get("role")
        employee_id = request.json.get("employee_id")
        business_id = session.get("business_id")
        if not business_id:
            return jsonify({"success": False, "error": "Business ID not found in session."}), 400

        business = db.businesses.find_one({"_id": business_id})

        employee_found = False
        for employee in business.get("employees", []):
            if employee.get("employee_id") == employee_id:
                employee_found = True
                result = db.businesses.update_one(
                    {"_id": business_id, "employees.employee_id": employee_id},
                    {"$set": {"employees.$.name": name, "employees.$.email": email, "employees.$.role": role}}
                )
                if result.modified_count == 1:
                    return jsonify({"success": True, "message": "Details updated."})
                else:
                    return jsonify({"success": False, "message": "Failed to update details."}), 500

        if not employee_found:
            return jsonify({"success": False, "message": "Employee not found."}), 404

    def remove_employee(self):
        business_id = session.get("business_id")
        employee_id = request.json["employee_id"]
        if db.businesses.count_documents({"_id": business_id, "employees.employee_id": employee_id}):
            result = db.businesses.update_one(
                {"_id": business_id},
                {"$pull": {"employees": {"employee_id": employee_id}}}
            )
            
            if result.modified_count == 1:
                return jsonify({"success": "Employee has been removed"})
            
            else:
                return jsonify({"error": "Could not remove employee"})
        
        else:
            return jsonify({"error": "Employee not found"})
                    

    def get_employee_id(self, business_id):
        business = db.businesses.find_one({"_id": business_id})
        if business:
            EMP_NO = business["emp_no"] + 1
            db.businesses.update_one({"_id": business_id}, {"$set": {"emp_no": EMP_NO}})
            return ("EMP0" + str(EMP_NO))
        
        else:
            return None
        

async def main(receiver_email, password ,business_id):
    sender_email = "dilraj2115038@gndec.ac.in"  
    subject = "Business Id"
    message = f"Your Business ID is {business_id}\nYour password is: {password}"
    await sendEmail(sender_email, receiver_email, subject, message)