
from flask import Response, render_template, request

from database_access import (
    category_add,
    category_exists,
    category_get_all,
)


def routes(app):
    @app.route("/categories")
    def category_list():
        """List all categories."""
        categories = category_get_all()
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
            return render_template('dialogs/error.html', error="Name is required"), 400
    
        if category_exists(name):
            return render_template('dialogs/error.html', error="Category already exists"), 400
    
        try:
            category_add(name, icon)
        
            resp = render_template('dialogs/success.html', message=f'Category "{name}" added successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'categoryUpdated'
            return resp
        except Exception as e:
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400

