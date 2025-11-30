import datetime
from pathlib import Path

from database import Event, EventCategory, Item, ItemStock, User, db
from database_access import database_init
from face_encoding import (
    average_encodings,
    encode_face_from_image,
    encode_face_to_bytes,
)

# Open database and create tables (if they don't exist)
database_init()

def load_face_encs(dir_path):
    dir_path = Path(dir_path)
    paths = [subp for subp in dir_path.iterdir()]
    encs = [encode_face_from_image(p) for p in paths]
    encs = average_encodings(encs)
    encs_bytes = encode_face_to_bytes(encs)
    return encs_bytes


# Add example users (if they don't exist)


# # Four examples:
# # 1. insert a "took the trash out" event
# event = Event.create(
#     user=user_aldo,
#     category=category_trash,
#     photo_path="",
#     notes="Took out the trash"
# )

# # 2. insert a "recharged electricity" event and cost 100$
# event = Event.create(
#     user=user_aldo,
#     category=category_power,
#     photo_path="", # <- empty for now
#     cost=100,
#     notes="Recharged electricity"
# )

# # The cost will be divided evenly for all the users.
# # All of them will pay for the electricity.
# users = list(User.select())
# for u in users:
#     EventCostShare.create(event=event, user=u)

# # 3. insert a "bought toilet paper"⁠event. this should set the "toilet paper" item stock to 1.
# stock_entry = ItemStock.create(
#     item=item_toilet_paper,
#     stock=5
# )
# event = Event.create(
#     user=user_aldo,
#     category=category_purchases,
#     photo_path="",
#     # cost=500,
#     notes="Bought toilet paper",
#     stock=stock_entry
# )
# # The cost will be divided evenly for all the users.
# # All of them will pay for the electricity.
# users = list(User.select())
# for u in users:
#     EventCostShare.create(event=event, user=u)

# # 4. insert a 'toilet paper is over" event. this should set the “toilet paper” item stock to 0.
# stock_entry = ItemStock.create(
#     item=item_toilet_paper,
#     stock=0
# )

# event = Event.create(
#     user=user_aldo,
#     category=category_purchases,
#     photo_path="",
#     notes="Toilet paper is over",
#     stock=stock_entry
# )

# # Close database before finishing use
# db.close()
