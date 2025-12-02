
from flask import Response, render_template, request

from database_access import (
    category_add,
    category_exists,
    category_get_all,
)
from response_helpers import json_error, json_response, wants_json_response


def routes(app):
    @app.route("/categories")
    def category_list():
        """List all categories."""
        categories = list(category_get_all())

        if wants_json_response():
            return json_response(
                {
                    "categories": [
                        {
                            "id": category.id,
                            "name": category.name,
                            "icon": category.icon,
                            "created_at": category.created_at.isoformat(),
                        }
                        for category in categories
                    ]
                }
            )

        return render_template('categories.html', categories=categories)


    @app.route("/dialog/add_category")
    def category_add_dialog():
        """Show add category dialog."""
        return render_template('dialogs/add_category.html')


    @app.route("/categories", methods=["POST"])
    def category_add_handle():
        """Handle category creation."""
        name = request.form.get('name')
        icon = request.form.get('icon', '📋')
    
        if not name:
            if wants_json_response():
                return json_error("Name is required", 400)
            return render_template('dialogs/error.html', error="Name is required"), 400
    
        if category_exists(name):
            if wants_json_response():
                return json_error("Category already exists", 400)
            return render_template('dialogs/error.html', error="Category already exists"), 400
    
        try:
            category = category_add(name, icon)
        
            if wants_json_response():
                return json_response(
                    {
                        "message": f'Category "{name}" added successfully!',
                        "category": {
                            "id": category.id,
                            "name": category.name,
                            "icon": category.icon,
                            "created_at": category.created_at.isoformat(),
                        },
                    }
                )

            resp = render_template('dialogs/success.html', message=f'Category "{name}" added successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'categoryUpdated'
            return resp
        except Exception as e:
            if wants_json_response():
                return json_error(str(e), 400)
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400

