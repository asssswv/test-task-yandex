from app import db, ma


# Product Class/Model
class Product(db.Model):
    id = db.Column(db.String(1000), primary_key=True)
    type = db.Column(db.String(1000), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    parentId = db.Column(db.Integer, nullable=True)
    children = db.Column(db.String(1000), nullable=True)
    date = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Product %r>' % self


# Product Schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'type', 'name', 'price', 'parentId', 'children', 'date')


# Init Schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
