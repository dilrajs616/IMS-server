from flask import request, session, jsonify
from app import db
from datetime import datetime
import asyncio
import smtplib
from sendmail import sendEmail

class Job:

    def fetch_jobs(self):
        business_id = session.get("business_id")
        business = db.businesses.find_one({"_id": business_id})
        jobs = business.get("jobs")
        pending_jobs = []
        active_jobs = []
        for job in jobs:
            if job["status"] == "pending":
                pending_jobs.append(job)
            if job['status'] == 'in progress':
                active_jobs.append(job)

        return jsonify({"active_jobs": active_jobs, "pending_jobs": pending_jobs})

    def create_job(self):
        business_id = session.get("business_id")
        product_id = request.json.get("product_id")
        business = db.businesses.find_one({"_id": business_id})
        product = None
        for prod in business["products"]:
            if prod["product_id"] == product_id:
                product = prod
                break

        product_name = product["name"]
        
        quantity = int(request.json.get("quantity"))
        job_id = self.get_job_id(business_id)
        job = {
            "job_id": job_id,
            "product_id": product_id,
            "product": product_name,
            "quantity": quantity,
            "status": "pending", 
            "completion_time": ''
        }
        
        if db.businesses.update_one({"_id": business_id}, {"$push" :{"jobs": job}}):
            return jsonify({"success": True, "Message": "job added successfully."})
        
        return jsonify({"success": False, "Message": "job could not be added"})
    
    def cancel_job(self):
        business_id = session.get("business_id")
        job_id = request.json.get("job_id")

        result = db.businesses.update_one({"_id": business_id}, {"$pull": {"jobs": {"job_id": job_id}}})

        if result.modified_count == 1:
            return jsonify({"success": True, "message": "Job deleted successfully."})
        
        else:
            return jsonify({"success": False, "message": "Failed to delete job"})
        
    def start_job(self):
        business_id = session.get("business_id")
        job_id = request.json.get("job_id")

        result = db.businesses.update_one({"_id": business_id, "jobs.job_id": job_id}, {"$set": {"jobs.$.status": "in progress"}})

        if result.modified_count == 1:
            return jsonify({"success": True, "message": "Job deleted successfully."})
        
        else:
            return jsonify({"success": False, "message": "Failed to delete job"})
        
    def finish_job(self):
        business_id = session.get("business_id")
        job_id = request.json.get("job_id")

        admin_mail = ""
        business = db.businesses.find_one({"_id": business_id})
        for user in business["employees"]:
            if user["role"] == "admin":
                admin_mail = user["email"]
        job = None
        job_list = business["jobs"]
        for j in job_list:
            if j["job_id"] == job_id:
                job = j
                break

        if not job:
            return jsonify({"success": False, "message": "Bad JobID"})

        product_id = job["product_id"]
        product = None
        for prod in business["products"]:
            if prod["product_id"] == product_id:
                product = prod
                break

        if not product:
            return jsonify({"success": False, "message": "couldn't find product"})
        
        quantity = int(job["quantity"])
        quantity_in_kg = quantity * 50
        batch_size = int(product["batch_size"])

        for prod_item in product["items"]:
            item_id = prod_item["item_id"]
            required_stock = float(prod_item["quantity"])
            item = None
            for db_item in business["items"]:
                if db_item["item_id"] == item_id:
                    item = db_item
                    break
            if item:
                available_stock = item["current_stock"]
                new_stock = available_stock - ((required_stock/batch_size) * quantity_in_kg)
                db.businesses.update_one({"_id": business_id, "items.item_id": item_id}, {"$set": {"items.$.current_stock": new_stock}})
                if new_stock <= item["threshold_stock"]:
                    asyncio.run(main(admin_mail, item["name"], new_stock))


        result = db.businesses.update_one({"_id": business_id, "jobs.job_id": job_id}, {"$set": {"jobs.$.status": "finish", "jobs.$.completion_time": str(datetime.now())}})

        if result.modified_count == 1:
            return jsonify({"success": True, "message": "Job finished successfully."})
        
        else:
            return jsonify({"success": False, "message": "Failed to complete job"})

    def fetch_complete_jobs(self):
        business_id = session.get("business_id")
        business = db.businesses.find_one({"_id": business_id})
        jobs = business.get("jobs")
        finished_jobs = []
        for job in jobs:
            if job["status"] == "finish":
                finished_jobs.append(job)

        return jsonify({"finished_jobs": finished_jobs})

    def get_job_id(self, business_id):
        business = db.businesses.find_one({"_id": business_id})
        JOB_NO = business["job_no"] + 1
        db.businesses.update_one({"_id": business_id}, {"$set": {"job_no": JOB_NO}})
        return ("JOB0" + str(JOB_NO))
    


async def main(receiver_email, item, stock):
    sender_email = "dilraj2115038@gndec.ac.in"  
    subject = "Business Id"
    message = f"{item} is low in stock, only {stock} kg left"
    await sendEmail(sender_email, receiver_email, subject, message)
