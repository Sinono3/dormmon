import os

from flask import Flask, render_template, send_from_directory

import category
import event
import items
import ledger
import user
import tasks
from database_access import (
    database_init,
)
#hola
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config["TEMPLATES_AUTO_RELOAD"] = True
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup
database_init()

@app.route("/")
def index():
    return render_template('base.html')

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

user.routes(app)
category.routes(app)
event.routes(app)
ledger.routes(app)
items.routes(app)
tasks.routes(app)

if __name__ == "__main__":
    app.run(debug=True)
