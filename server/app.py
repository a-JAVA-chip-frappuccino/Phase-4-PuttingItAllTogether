from config import app
from flask import make_response, request
from flask_restful import Api, Resource

from models import db, MakeupItem, Store, StoreHasItem

api = Api(app)

@app.route('/makeup_items', methods = ['GET'])
def makeup_items():
    makeup_items = MakeupItem.query.all()

    makeup_items_dict = [item.to_dict() for item in makeup_items]

    response = make_response(
        makeup_items_dict,
        200
    )

    return response

@app.route('/stores', methods = ['GET', 'POST'])
def stores():
    if request.method == 'GET':
        stores = Store.query.all()

        stores_dict = [store.to_dict(rules = ('-item_stores', )) for store in stores]

        response = make_response(
            stores_dict,
            200
        )
    elif request.method == 'POST':
        try:
            form_data = request.get_json()

            new_store_obj = Store (
                name = form_data['name']
            )

            db.session.add(new_store_obj)
            db.session.commit()

            response = make_response(
                new_store_obj.to_dict(),
                201
            )
        except ValueError:
            response = make_response(
                {"ERROR" : "VALIDATION ERROR RAISED!"},
                400
            )

    return response

@app.route('/stores/<int:id>', methods = ['GET', 'DELETE'])
def store_by_id(id):
    store = Store.query.filter(Store.id == id).first()

    if store:
        if request.method == 'GET':
            store_dict = store.to_dict()

            response = make_response(
                store_dict,
                200
            )
        elif request.method == 'DELETE':
            assoc_store_item = StoreHasItem.query.filter(StoreHasItem.store_id == id).all()

            for row in assoc_store_item:
                db.session.delete(row)

            db.session.delete(store)
            db.session.commit()

            response = make_response(
                {},
                204
            )
    else:
        response = make_response(
            {"ERROR" : "STORE NOT FOUND!"},
            404
        )

    return response

class SHI(Resource):
    def patch(self, id):
        store_has_item = StoreHasItem.query.filter(StoreHasItem.id == id).first()

        if store_has_item:
            try:
                form_data = request.get_json()

                for attr in form_data:
                    setattr(store_has_item, attr, form_data[attr])

                db.session.commit()

                response = make_response(
                    store_has_item.to_dict(),
                    200
                )

            except ValueError:
                response = make_response(
                    {"ERROR" : "VALIDATION ERROR RAISED!"},
                    400
                )
        else:
            response = make_response(
                {"ERROR" : "COULD NOT FIND ITEM!"},
                404
            )

        return response
    
api.add_resource(SHI, '/store_has_item/<int:id>')

if __name__ == "__main__":
    app.run(port = 5555, debug = True)