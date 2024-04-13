from app import app
from product.models import Product

@app.route("/product/fetch")
def fetch_products():
    return Product().fetch_products()

@app.route("/product/fetch-items", methods=["POST"])
def fetch_products_items():
    return Product().fetch_products_items()

@app.route("/product/fetch-remaining-items", methods={"POST"})
def remaining_items():
    return Product().remaining_items()

@app.route("/product/add", methods = ["POST"])
def add_product():
    return Product().add_product()

@app.route("/product/add_item", methods=["POST"])
def product_item():
    return Product().add_product_item()

@app.route("/product/remove", methods = ["POST"])
def remove_product():
    return Product().remove_product()

@app.route("/product/remove_item", methods=["POST"])
def remove_item():
    return Product().remove_item()