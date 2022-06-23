from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from datetime import datetime
import math

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Init client for development testing
client = app.test_client()

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'product.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)


# Product Class/Model
class Product(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    parentId = db.Column(db.Integer, nullable=True)
    children = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Product %r>' % self


# Product Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'type', 'name', 'price', 'parentId', 'children', 'date')


# Init Schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


# Post and Put func
def check(table, idd):
    for item in table:
        if item['id'] == idd:
            return True

    return False


def update(item, updateDate):
    target = Product.query.get(item['id'])
    try:
        new_name = item['name']
        target.name = new_name
    except:
        pass

    try:
        new_price = item['price']
        target.price = new_price
    except:
        pass

    try:
        new_parentId = item['parentId']
        if not (new_parentId == target.parentId):
            if not (target.parentId == "") and not (target.parentId is None):
                parentId = target.parentId
                parent = Product.query.get(parentId)
                str_children = parent.children.split(" ")
                str_children.remove(target.id)
                parent.children = " ".join(str_children)

            new_parent = Product.query.get(new_parentId)
            if new_parent.children == "" or new_parent.children is None:
                new_parent.children = item["id"]
            else:
                children = new_parent.children.split(" ")
                if not (target.id in children):
                    children.append(target.id)
                    new_parent.children = " ".join(children)

        target.parentId = new_parentId

    except:
        pass

    try:
        children = item['children']
        children_id = []
        for item in children:
            children_id.append(item['id'])
        children_id = ' '.join(children_id)
        target.children = children_id
    except:
        pass

    try:
        new_date = item['date']
        target.date = new_date
    except:
        pass
    target.date = updateDate

    try:
        db.session.commit()
        return product_schema.jsonify(target)
    except:
        return "OOOOPS"


def add(item, updateDate):
    id = item['id']
    type = item['type']
    name = item['name']

    try:
        price = item['price']
    except:
        price = None

    try:
        parentId = item['parentId']
        parent = Product.query.get(parentId)

        if parent.children == "" or parent.children == None:
            parent.children = id
        else:
            children = parent.children.split(" ")
            if not (id in children):
                children.append(id)
                parent.children = " ".join(children)

    except:
        parentId = None

    try:
        children = item['children']
        children_id = []
        for item in children:
            children_id.append(item['id'])
        children_id = ' '.join(children_id)
    except:
        children_id = None

    date = updateDate
    new_product = Product(id=id, type=type, name=name, price=price, parentId=parentId, children=children_id, date=date)

    try:
        db.session.add(new_product)
        db.session.commit()
        return product_schema.jsonify(new_product)
    except:
        return "OOOOPS"


# Crate a Product
@app.route('/imports', methods=['POST', 'PUT'])
def add_product():
    data = request.get_json()
    items = data["items"]

    try:
        all_products = Product.query.all()
        list_all_products = products_schema.dump(all_products)

    except:
        list_all_products = []

    try:
        updateDate = datetime.strptime(data['updateDate'], '%Y-%m-%dT%H:%M:%S.%f%z')

    except:
        return "Record not found", 400

    for item in items:
        idd = item['id']

        if check(list_all_products, idd):
            update(item, updateDate)

        else:
            add(item, updateDate)

    return "OK", 200


# Get func
def GetInfoAboutChildren(target):
    res = []
    price = [0, 0]

    children_id = target["children"].split(" ")

    for id in children_id:

        child = Product.query.get(id)
        child_json = product_schema.dump(child)

        if child_json["children"] == "" or child_json["children"] == None:

            if child_json["type"] == "OFFER":
                price[0] += child_json["price"]
                price[1] += 1

            res.append(child_json)

        else:

            child_json["children"], get_price = GetInfoAboutChildren(child_json)

            if get_price[1] > 0:
                child_json["price"] = math.floor(get_price[0] / get_price[1])

            price[0] += get_price[0]
            price[1] += get_price[1]

            res.append(child_json)

    return res, price


# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    try:
        all_products = Product.query.all()
        result = products_schema.dump(all_products)

    except:
        result = []

    my_result = []
    for item in result:

        if item["children"] == "" or item["children"] == None:
            my_result.append(item)

        else:
            item["children"], price = GetInfoAboutChildren(item)

            if price[1] > 0:
                item["price"] = math.floor(price[0] / price[1])

            my_result.append(item)

    return jsonify(my_result)


@app.route('/nodes/<string:id>', methods=['GET'])
def get_product(id):
    try:
        data = Product.query.get(id)
        target = product_schema.dump(data)

        if target["children"] == "" or target["children"] == None:
            return jsonify(target)

        else:
            target["children"], price = GetInfoAboutChildren(target)

            if price[1] > 0:
                target["price"] = math.floor(price[0] / price[1])

            return jsonify(target)

    except:
        return "Product with this id does not exist!"


# Delete func
def delete(target_id):
    target = Product.query.get(target_id)
    target_json = product_schema.dump(target)
    children = target_json["children"]

    if children == "" or children == None:
        if target.parentId is None or target.parentId == "":
            db.session.delete(target)
            return

        parentId = target.parentId
        parent = Product.query.get(parentId)
        str_children = parent.children.split(" ")
        str_children.remove(target.id)
        parent.children = " ".join(str_children)

        db.session.delete(target)
        return

    else:
        for child in children.split(" "):
            delete(child)

        if target.parentId is None or target.parentId == "":
            db.session.delete(target)
            return

        parentId = target.parentId
        parent = Product.query.get(parentId)
        str_children = parent.children.split(" ")
        str_children.remove(target.id)
        parent.children = " ".join(str_children)
        db.session.delete(target)
        return


@app.route('/delete/<string:id>', methods=['DELETE'])
def delete_product(id):
    try:
        delete(id)
        db.session.commit()
        return redirect("/products")

    except:
        return "Product with this id does not exist!"


# Run Server
if __name__ == '__main__':
    # tprint("YANDEX ACADEMY", font="bulbhead")
    app.run(debug=True)
#   app.run(debug=False, host="0.0.0.0", port=80)
