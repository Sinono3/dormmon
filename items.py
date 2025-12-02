from flask import Response, render_template, request

from database import Item
from database_access import (
    item_add,
    item_get_all,
    item_get_all_with_stock,
    item_get_by_id,
    item_stock_set_by_id,
)
from response_helpers import json_error, json_response, wants_json_response


def routes(app):
    @app.route("/items")
    def items_list():
        item_stock = list(item_get_all_with_stock())

        if wants_json_response():
            return json_response(
                {
                    "items": [
                        {
                            "id": item.id,
                            "name": item.name,
                            "icon": item.icon,
                            "created_at": item.created_at.isoformat(),
                            "stock": stock.stock if stock else None,
                            "stock_logged_at": stock.logged_at.isoformat()
                            if stock
                            else None,
                        }
                        for item, stock in item_stock
                    ]
                }
            )

        return render_template("items.html", item_stock=item_stock)

    @app.route("/dialog/add_item")
    def item_add_dialog():
        return render_template("dialogs/add_item.html")

    @app.route("/items", methods=["POST"])
    def item_add_handle():
        name = request.form.get("name")
        icon = request.form.get("icon", "📦")

        if not name:
            if wants_json_response():
                return json_error("Name required", 400)
            return "Error: Name required", 400

        item = item_add(name, icon)

        if wants_json_response():
            return json_response(
                {
                    "message": f'Item "{name}" added successfully!',
                    "item": {
                        "id": item.id,
                        "name": item.name,
                        "icon": item.icon,
                        "created_at": item.created_at.isoformat(),
                    },
                }
            )

        resp = render_template(
            "dialogs/success.html", message=f'Item "{name}" added successfully!'
        )
        resp = Response(resp)
        resp.headers["HX-Trigger"] = "itemUpdated"
        return resp

    # Stock management
    @app.route("/dialog/set_stock")
    def item_stock_set_dialog():
        return render_template("dialogs/set_stock.html", items=item_get_all())

    @app.route("/stock", methods=["POST"])
    def item_stock_set_handle():
        item_id = request.form.get("item_id")
        stock = int(request.form.get("stock", 0))

        try:
            item = item_get_by_id(item_id)
            entry = item_stock_set_by_id(item, stock)

            if wants_json_response():
                return json_response(
                    {
                        "message": f'Stock for "{item.name}" set to {stock}!',
                        "stock": {
                            "item_id": item.id,
                            "stock": entry.stock,
                            "logged_at": entry.logged_at.isoformat(),
                        },
                    }
                )

            resp = render_template(
                "dialogs/success.html", message=f'Stock for "{item.name}" set to {stock}!'
            )
            resp = Response(resp)
            resp.headers["HX-Trigger"] = "itemUpdated"
            return resp
        except Item.DoesNotExist:
            if wants_json_response():
                return json_error("Item not found", 400)
            return "Error: Item not found", 400
