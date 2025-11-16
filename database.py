from peewee import IntegerField, Model, SqliteDatabase, CharField, ForeignKeyField, TextField, BlobField, DateTimeField, DecimalField
import datetime

db = SqliteDatabase('my_database.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)
    face_encoding = BlobField()
    created_at = DateTimeField(default=datetime.datetime.now)
   
class Item(BaseModel):
    name = CharField()
    icon = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    # category = CharField()

class ItemStock(BaseModel):
    item = ForeignKeyField(Item, backref='stocks', on_delete='CASCADE')
    stock = IntegerField()

class EventCategory(BaseModel):
    name = CharField()
    icon = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)

class Event(BaseModel):
    user = ForeignKeyField(User, backref='events')
    category = ForeignKeyField(EventCategory, backref='events')
    logged_at = DateTimeField(default=datetime.datetime.now)
    modified_at = DateTimeField(default=datetime.datetime.now)
    photo_path = TextField()
    cost = DecimalField(10, 2, null=True)
    stock = ForeignKeyField(ItemStock, backref='event', null=True, unique=True, on_delete='CASCADE')
    notes = TextField(default="") 

# Template
class EventTemplate(BaseModel):
    category = ForeignKeyField(EventCategory, backref='templates', on_delete='CASCADE')
    cost = DecimalField(10, 2, null=True)
    notes = TextField(default="")

# Separate table to not add 2 nullable fields requiring double manual NOT NULL check
class EventTemplateItemStock(BaseModel):
    template = ForeignKeyField(EventTemplate, backref='stock', on_delete='CASCADE')
    item = ForeignKeyField(Item, backref='event_template_item_stocks', on_delete='CASCADE')
    stock = IntegerField()

