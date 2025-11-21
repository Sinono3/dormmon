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
    stock = ForeignKeyField(ItemStock, backref='event', null=True, unique=True, on_delete='CASCADE')
    notes = TextField(default="") 

class Ledger(Model):
    event = ForeignKeyField(Event, backref='ledger_items', null=True, on_delete='CASCADE')
    payer = ForeignKeyField(User, backref='money_sent', on_delete='CASCADE')
    beneficiary = ForeignKeyField(User, backref='money_recv', on_delete='CASCADE')
    amount = DecimalField(15, 2, null=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    
    class Meta:
        database = db
        indexes = (
            (('event', 'payer', 'beneficiary'), False), # False = not unique
        )
