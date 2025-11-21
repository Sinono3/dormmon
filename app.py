"""Main Flask application."""
import os

from flask import Flask, render_template

import category
import event
import user
from database_access import (
    database_init,
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config["TEMPLATES_AUTO_RELOAD"] = True
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup
database_init()

@app.route("/")
def index():
    """Main page."""
    return render_template('base.html')

user.routes(app)
category.routes(app)
event.routes(app)

if __name__ == "__main__":
    app.run(debug=True)
