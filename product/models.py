from flask import request, jsonify, session
from app import db

class Product():
    
    def fetch_products(self):
        business_id = session.get("business_id")
        business = db.businesses.find_one({"_id": business_id})
        if business:
            product_list = business["products"]
            for product in product_list:
                del product["items"]
            
            return jsonify({"success": True,"product_list": product_list})
        else:
            return jsonify({"success": False, "error": "Could not fetch products"})
        
    def fetch_products_items(self):
        business_id = session.get("business_id")
        product_id = request.json.get("product_id")

        if not business_id:
            return jsonify({"success": False, "error": "No business ID provided"})
        if not product_id:
            return jsonify({"success": False, "item_list": []})

        business = db.businesses.find_one({"_id": business_id})

        if not business:
            return jsonify({"success": False, "error": "Business not found"})
        
        product = None
        for prod in business.get("products", []):
            if prod.get("product_id") == product_id:
                product = prod
                break

        if not product:
            return jsonify({"success": False, "error": "Product not found"})

        item_list = product.get("items", [])

        return jsonify({"success": True, "item_list": item_list})

    def add_product(self):
        
        business_id = session.get("business_id")
        name = request.json.get("name")
        batch_size = request.json.get("batch_size")
        product_id = self.get_product_id(business_id)

        product = {
            "product_id": product_id,
            "name": name,
            "batch_size": batch_size,
            "items": []
        }

        if db.businesses.update_one({"_id": business_id}, {"$push" :{"products": product}}):
            return jsonify({"success": True, "Message": "Product added successfully."})
        
        return jsonify({"success": False, "Message": "Product could not be added"})

    def add_product_item(self):
        business_id = session.get("business_id")
        if not business_id:
            return jsonify({"success": False, "error": "Business ID not found in session."}), 400
        
        product_id = request.json.get("product_id")
        item_id = request.json.get("item_id")
        item_name = ""
        business = db.businesses.find_one({"_id": business_id})
        for dbItem in business["items"]:
            if dbItem["item_id"] == item_id:
                item_name = dbItem["name"]
        quantity = float(request.json.get("quantity", 0))
        
        if not (product_id and item_id):
            return jsonify({"success": False, "error": "Product ID or Product ID missing in request."}), 400
        
        item = {
            "item_id": item_id,
            "item_name": item_name,
            "quantity": quantity
        }
        
        result = db.businesses.update_one(
            {"_id": business_id, "products.product_id": product_id},
            {"$push": {"products.$.items": item}}
        )
        
        if result.modified_count == 1:
            return jsonify({"success": True, "message": "Item added successfully."})
        else:
            return jsonify({"success": False, "error": "Failed to add item to product."}), 500

    def remaining_items(self):
        business_id = session.get("business_id")
        product_items = {}
        product_id = request.json.get("product_id")
        business = db.businesses.find_one({"_id": business_id})
        
        if business:
            item_list = business["items"]
            
            if not product_id:
                return jsonify({"success": False, "remaining_items": []})

            for product in business["products"]:
                if product["product_id"] == product_id:
                    product_items = product["items"]
                    break

            used_itemid = []
            for item in product_items:
                used_itemid.append(item['item_id'])

            remaining_items = [item for item in item_list if item["item_id"] not in used_itemid]

            return jsonify({"success": True, "remaining_items": remaining_items}), 200
        
        else :
            return jsonify({"success": False, "remaining_items": []})

    def remove_product(self):
        product_id = request.json["product_id"]
        business_id = session.get("business_id")

        if db.businesses.count_documents({"_id": business_id, "products.product_id": product_id}):
            result = db.businesses.update_one(
                {"_id": business_id},
                {"$pull": {"products": {"product_id": product_id}}}
            )
            
            if result.modified_count == 1:
                return jsonify({"success": "Product has been removed"})
            
            else:
                return jsonify({"error": "Could not remove Product"})
        
        else:
            return jsonify({"error": "Product not found"})

    def remove_item(self):
        product_id = request.json["product_id"]
        item_id = request.json["item_id"]
        business_id = session.get("business_id")
        business = db.businesses.find_one({"_id": business_id})
        for product in business["products"]:
            for item in product["items"]:
                if item["item_id"] == item_id:
                    result = db.businesses.update_one(
                        {"_id": business_id, "products.product_id": product_id},
                        {"$pull": {"products.$.items": {"item_id": item_id}}}
                    )
                    if result.modified_count == 1:
                        return jsonify({"success": True, "message": "Item deleted."})
                    else:
                        return jsonify({"success": False, "message": "Failed to remove item."}), 500
        return jsonify({"success": False, "message": "Item not found."}), 404

    def get_product_id(self, business_id):
        business = db.businesses.find_one({"_id": business_id})
        if business:
            PROD_NO = business["product_no"] + 1
            db.businesses.update_one({"_id": business_id}, {"$set": {"product_no":PROD_NO}})
            return ("PROD0" + str(PROD_NO))

        else:
            return None
