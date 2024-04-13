from flask import jsonify, request, session
from passlib.hash import pbkdf2_sha256
from app import db
import asyncio
import smtplib
from sendmail import sendEmail

class Business:

    def start_session(self, user, business_id, login):
        
        additional_claims = {
            "user_id": user["employee_id"]
        }

        if login:
            additional_claims["isLoggedIn"] = True
            del user["password"]
            session['logged_in'] = True
            session['user'] = user
            session["business_id"] = business_id
            return jsonify({"Response": "Baba ji ka thullu"}), 200

        return business_id, 200
    
    def signup(self):
        
        BIZ_ID = self.get_business_id()

        # extract data from form request
        business_name = request.json["business"]
        email = request.json["email"]
        name = request.json["name"]
        password = request.json["password"]
        
        # Check for existing email address
        if db.businesses.find_one({ "employees.email": email }):
            return "Email Already exists", 201
        
        else:
            employee_id = 'EMP01'
            
            # create business object
            business = {
                "_id": BIZ_ID,
                "business_name" : business_name,
                "emp_no": 1,
                "item_no": 0,
                "product_no": 0,
                "job_no": 0,
                "employees": [],
                "items": [],
                "products": [],
                "jobs": []
            }
            
            # create employee object
            employee = {
                "employee_id" : employee_id,
                "name" : name,
                "email" : email,
                "role" : "admin",
                "password" : password
            }
            
            employee["password"] = pbkdf2_sha256.encrypt(employee['password'])
        
            db.businesses.insert_one(business)
            
            if db.businesses.update_one({'_id': BIZ_ID}, {'$push': {'employees': employee}}):
                asyncio.run(main(email, password, BIZ_ID))
                return self.start_session(employee, BIZ_ID, False)
            
        return jsonify( { "error": "Signup failed" } ), 400
    
    
    
    def signout(self):
        if session.clear():
            return jsonify({"success": True})
        
        else:
            return jsonify({"Error": "Could not logout"})
    
    
    def login(self):
        
        business_id = request.json["business_id"]
        email = request.json["email"]
        password = request.json["password"]
        
        business = db.businesses.find_one({"_id" : business_id})
        if not business:
            return jsonify({"error": "business id is invalid"})
        
        employee = next((emp for emp in business.get('employees', []) if emp['email'] == email), None)
        
        if employee and pbkdf2_sha256.verify(password, employee['password']):
            return self.start_session(employee, business_id, True)
        
        return jsonify({
            "error": "Credentials not found"
        }), 401
        
                    
    def get_business_id(self):

        try:
            data = db.businesses.find_one({"_id": "INFO01"})
            BIZ_NO = data["BIZ_NO"] + 1
            db.businesses.update_one({"_id": "INFO01"}, {"$set": {"BIZ_NO": BIZ_NO}})

        except:
            biz_info = {
                "_id": "INFO01",
                "BIZ_NO": 1
            }
            db.businesses.insert_one(biz_info)
            BIZ_NO = 1

        return ("BIZ0" + str(BIZ_NO))
    
async def main(receiver_email, password ,business_id):
    sender_email = "dilraj2115038@gndec.ac.in"  
    subject = "Business Id"
    message = f"Your Business ID is {business_id}\nYour password is: {password}"
    await sendEmail(sender_email, receiver_email, subject, message)
