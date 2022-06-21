from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from datetime import datetime

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
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


def check(table, idd):
    for item in table:
        if item['id'] == idd:
            return True

    return False


def update(db, item, updateDate):
    product = Product.query.get(item['id'])
    try:
        new_name = item['name']
        product.name = new_name
    except:
        pass

    try:
        new_price = item['price']
        product.price = new_price
    except:
        pass

    try:
        new_parentId = item['parentId']
        product.parentId = new_parentId
    except:
        pass

    try:
        new_children = item['children']
        product.children = new_children
    except:
        pass

    try:
        new_date = item['date']
        product.date = new_date
    except:
        pass
    product.date = updateDate

    try:
        db.session.commit()
        product_schema.jsonify(product)
        return "OK", 200
    except:
        return "OOOOPS"


def add(db, item, updateDate):
    id = item['id']
    type = item['type']
    name = item['name']

    try:
        price = item['price']
    except:
        price = None

    try:
        parentId = item['parentId']
    except:
        parentId = None

    try:
        children = item['children']
    except:
        children = None

    date = updateDate
    new_product = Product(id=id, type=type, name=name, price=price, parentId=parentId, children=children, date=date)
    try:
        db.session.add(new_product)
        db.session.commit()
        product_schema.jsonify(new_product)
        return "OK", 200
    except:
        return "OOOOPS"


# Crate a Product
@app.route('/import', methods=['POST', 'PUT'])
def add_product():
    data = request.get_json()
    items = data['items']
    try:
        all_products = Product.query.all()
        table = products_schema.dump(all_products)
    except:
        table = []

    try:
        updateDate = datetime.strptime(data['updateDate'], '%Y-%m-%dT%H:%M:%S.%f%z')
    except:
        return "Record not found", 400

    for item in items:
        idd = item['id']

        if check(table, idd):
            update(db, item, updateDate)

        else:
            add(db, item, updateDate)
    return "OK", 200


@app.route('/0.0.0.0:80/products', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)


@app.route('/0.0.0.0:80/<string:id>', methods=['GET'])
def get_product(id):
    try:
        all_products = Product.query.all()
        table = products_schema.dump(all_products)
        res = []

        for item in table:
            if item['id'] == id:
                res.append(item)
                break

        if res[0]['type'] == 'CATEGORY' and not (res[0]['children'] == None):
            for i in res[0]['children'].split(' '):
                for item in table:
                    if item['id'] == i:
                        res.append(item)
                        break
        return jsonify(res)
    except:
        return "OOOOPS"


@app.route('/0.0.0.0:80/<string:id>', methods=['DELETE'])
def delete_product(id):
    try:
        all_products = Product.query.all()
        table = products_schema.dump(all_products)
        target = Product.query.get(id)
        try:
            data = target.children.split(' ')
        except:
            data = []

        db.session.delete(target)

        for item in table:
            if item['id'] in data:
                target = Product.query.get(item['id'])
                db.session.delete(target)

        db.session.commit()
        return "OK"

    except:
        return "OOOOPS"


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
