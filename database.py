from peewee import IntegerField, Model, SqliteDatabase, CharField, ForeignKeyField, TextField, BlobField, DateTimeField, DecimalField
import datetime

db = SqliteDatabase('my_database.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    name = CharField(unique=True)
    face_encoding = BlobField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
   
class Item(BaseModel):
    name = CharField()
    icon = CharField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

class ItemStock(BaseModel):
    item = ForeignKeyField(Item, backref='stocks', on_delete='CASCADE')
    stock = IntegerField()
    logged_at = DateTimeField(default=datetime.datetime.utcnow)

class EventCategory(BaseModel):
    name = CharField(unique=True)
    icon = CharField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

class Event(BaseModel):
    user = ForeignKeyField(User, backref='events', on_delete='CASCADE')
    category = ForeignKeyField(EventCategory, backref='events', on_delete='CASCADE')
    logged_at = DateTimeField(default=datetime.datetime.utcnow)
    modified_at = DateTimeField(default=datetime.datetime.utcnow)
    photo_path = TextField()
    cost = DecimalField(10, 2, null=True)
    stock = ForeignKeyField(ItemStock, backref='event', null=True, unique=True, on_delete='CASCADE')
    notes = TextField(default="") 

# If the event has a cost, who should pay for this event?
# There can be multiple per event, and the cost is divided evenly between the people.
class EventCostShare(BaseModel):
    event = ForeignKeyField(Event, backref='cost_shared_among', on_delete='CASCADE')
    user = ForeignKeyField(User, backref='events_cost_shared', on_delete='CASCADE')

# # Template
# class EventTemplate(BaseModel):
#     category = ForeignKeyField(EventCategory, backref='templates', on_delete='CASCADE')
#     cost = DecimalField(10, 2, null=True)
#     notes = TextField(default="")

# # Separate table to not add 2 nullable fields requiring double manual NOT NULL check
# class EventTemplateItemStock(BaseModel):
#     template = ForeignKeyField(EventTemplate, backref='stock', on_delete='CASCADE')
#     item = ForeignKeyField(Item, backref='event_template_item_stocks', on_delete='CASCADE')
#     stock = IntegerField()

