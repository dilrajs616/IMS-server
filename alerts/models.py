from flask import session, jsonify, request
from app import db

class Alert():

    def fetch_alert(self):
        business_id = session.get("business_id")
        business = db.businesses.find_one({"_id": business_id})
        shit_list = []
        for item in business["items"]:
            if item["current_stock"] < item["threshold_stock"]:
                alert = f"{item["name"]} is low in stock"
                shit_list.append(alert)

        return jsonify({"alert_list": shit_list})
        