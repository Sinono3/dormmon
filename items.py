from flask import Response, render_template, request

from database import Item
from database_access import (
    item_add,
    item_get_all,
    item_get_all_with_stock,
    item_get_by_id,
    item_stock_set_by_id,
)


def routes(app):
    @app.route("/items")
    def items_list():
        return render_template("items.html", item_stock=item_get_all_with_stock())

    @app.route("/dialog/add_item")
    def item_add_dialog():
        return render_template("dialogs/add_item.html")

    @app.route("/items", methods=["POST"])
    def item_add_handle():
        name = request.form.get("name")
        icon = request.form.get("icon", "📦")

        if not name:
            return "Error: Name required", 400

        item_add(name, icon)
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
            item_stock_set_by_id(item, stock)

            resp = render_template(
                "dialogs/success.html", message=f'Stock for "{item.name}" set to {stock}!'
            )
            resp = Response(resp)
            resp.headers["HX-Trigger"] = "itemUpdated"
            return resp
        except Item.DoesNotExist:
            return "Error: Item not found", 400
