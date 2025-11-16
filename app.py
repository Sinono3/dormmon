from flask import Flask
from database import db, User, Item, ItemStock, EventCategory, Event, EventTemplate, EventTemplateItemStock

db.connect()
db.create_tables([User, Item, ItemStock, EventCategory, Event, EventTemplate, EventTemplateItemStock])
db.close()

app = Flask(__name__)

@app.route("/")
def index():
    return "<p>test</p>"
