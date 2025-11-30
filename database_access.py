"""Database access layer - all database queries and operations."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from peewee import fn

from database import Event, EventCategory, Item, ItemStock, Ledger, User, db


def database_init():
    """Initialize database and create default category."""
    db.connect()
    db.create_tables([User, Item, ItemStock, EventCategory, Event, Ledger])

    def load_face_encs(dir_path):
        from face_encoding import (
            average_encodings,
            encode_face_from_image,
            encode_face_to_bytes,
        )
        dir_path = Path(dir_path)
        paths = [subp for subp in dir_path.iterdir()]
        encs = [encode_face_from_image(p) for p in paths]
        encs = average_encodings(encs)
        encs_bytes = encode_face_to_bytes(encs)
        return encs_bytes

    user_maia, _ = User.get_or_create(
        name="Maia",
        defaults={
            "face_encoding": load_face_encs("database/maia"),
            "created_at": datetime.utcnow(),
        },
    )
    user_jaz, _ = User.get_or_create(
        name='Jaz',
        defaults={
            "face_encoding": load_face_encs("database/jaz"),
            "created_at": datetime.utcnow(),
        },
    )
    user_simon, _ = User.get_or_create(
        name='Simon',
        defaults={
            "face_encoding": load_face_encs("database/simon"),
            "created_at": datetime.utcnow(),
        },
    )
    user_aldo, _ = User.get_or_create(
        name='Aldo',
        defaults={
            "face_encoding": load_face_encs("database/aldo"),
            "created_at": datetime.utcnow(),
        },
    )

    # Add example categories (if they don't exist)
    category_default, _ = EventCategory.get_or_create(
        name='Default',
        defaults={'icon': '📋', 'created_at': datetime.utcnow()}
    )
    category_trash, _ = EventCategory.get_or_create(
        name='Trash',
        defaults={'icon': '🗑️', 'created_at': datetime.utcnow()}
    )
    category_power, _ = EventCategory.get_or_create(
        name='Power',
        defaults={'icon': '⚡️', 'created_at': datetime.utcnow()}
    )
    category_purchases, _ = EventCategory.get_or_create(
        name='Purchases',
        defaults={'icon': '🛍️', 'created_at': datetime.utcnow()}
    )
    category_default, _ = EventCategory.get_or_create(
        name='Room Cleaning',
        defaults={'icon': '🧹', 'created_at': datetime.utcnow()}
    )

    # Add example items (if they don't exist)
    item_toilet_paper, _ = Item.get_or_create(
        name='Toilet paper',
        defaults={'icon': '🧻', 'created_at': datetime.utcnow()}
    )
    # ItemStock.create(item=item_toilet_paper, stock=0, logged_at=datetime.utcnow())
    db.close()


def user_get_all():
    """Get all users."""
    return User.select().order_by(User.name)


def user_get_by_id(user_id: int) -> User:
    """Get user by ID."""
    return User.get_by_id(user_id)


def user_add(name: str, face_encoding: bytes) -> User:
    """Create a new user."""
    return User.create(
        name=name, face_encoding=face_encoding, created_at=datetime.utcnow()
    )


def user_exists(name: str) -> bool:
    """Check if user with given name exists."""
    return User.select().where(User.name == name).exists()


# Event Category operations
def category_get_all():
    """Get all event categories."""
    return EventCategory.select().order_by(EventCategory.name)


def category_get_by_id(category_id: int) -> EventCategory:
    """Get category by ID."""
    return EventCategory.get_by_id(category_id)


def category_add(name: str, icon: str) -> EventCategory:
    """Create a new event category."""
    return EventCategory.create(name=name, icon=icon, created_at=datetime.utcnow())


def category_exists(name: str) -> bool:
    """Check if category with given name exists."""
    return EventCategory.select().where(EventCategory.name == name).exists()


def category_get_by_name(name: str) -> Optional[EventCategory]:
    """Get a category by name if it exists."""
    return EventCategory.get_or_none(EventCategory.name == name)


# Event operations
def event_get_recent(
    limit: int = 50,
    category_id: Optional[int] = None,
    category_name: Optional[str] = None,
):
    """Get recent events, optionally filtered by category."""
    query = Event.select().order_by(Event.logged_at.desc())

    if category_id is not None:
        query = query.where(Event.category == category_id)
    elif category_name:
        query = (
            query.join(EventCategory)
            .where(EventCategory.name == category_name)
            .switch(Event)
        )

    return query.limit(limit)

def event_get_by_id(id: int) -> Event:
    return Event.get_by_id(id)


def event_add(
    user_id: int,
    category_id: int,
    photo_path: str,
    notes: str = "",
    item_stock_id: Optional[int] = None,
) -> Event:
    """Create a new event."""
    return Event.create(
        user=user_id,
        category=category_id,
        photo_path=photo_path,
        notes=notes,
        stock=item_stock_id,
        logged_at=datetime.utcnow(),
        modified_at=datetime.utcnow(),
    )


def event_get_latest_by_category(category: EventCategory) -> Optional[Event]:
    """Return the latest event for a category."""
    return (
        Event.select()
        .where(Event.category == category)
        .order_by(Event.logged_at.desc())
        .first()
    )


def event_user_has_category_entry_since(
    user_id: int, category: EventCategory, since: datetime
) -> bool:
    """Check whether a user has logged an event in a category since a given datetime."""
    return (
        Event.select()
        .where(
            (Event.category == category)
            & (Event.user == user_id)
            & (Event.logged_at >= since)
        )
        .exists()
    )


def event_get_cost(event_id: int) -> Optional[int]:
    """Get the total cost of an event from ledger entries."""
    # Sum all ledger entries for this event (each entry is a portion of the total)
    # We can sum all entries or just the self-reference ones - both should give the same total
    total = (
        Ledger.select(fn.Sum(Ledger.amount))
        .where(Ledger.event == event_id)
        # .where(Ledger.payer == Ledger.beneficiary)  # Self-reference entries represent the total
        .scalar()
    )
    return total if total else None


# Ledger operations
def ledger_add(
    event_id: Optional[int],
    payer_id: int,
    beneficiary_id: int,
    amount: int,
) -> Ledger:
    """Create a ledger entry."""
    return Ledger.create(
        event=event_id,
        payer=payer_id,
        beneficiary=beneficiary_id,
        amount=amount,
        created_at=datetime.utcnow(),
    )


def ledger_get_balance(user_id: int) -> int:
    """
    Get the net balance for a user.
    Positive = user is owed money (others owe them)
    Negative = user owes money (they owe others)
    """
    money_sent = (
        Ledger.select(fn.Sum(Ledger.amount)).where(Ledger.payer == user_id).scalar()
        or 0
    )
    money_received = (
        Ledger.select(fn.Sum(Ledger.amount))
        .where(Ledger.beneficiary == user_id)
        .scalar()
        or 0
    )
    return money_sent - money_received


def ledger_get_all_balances() -> dict:
    """Get balances for all users. Returns dict mapping user_id to balance."""
    users = User.select()
    balances = {}
    for user in users:
        balances[user.id] = ledger_get_balance(user.id)
    return balances


def ledger_get_owed_to_user(user_id: int) -> List[Ledger]:
    """Get all ledger entries where user is owed money."""
    return (
        Ledger.select()
        .where(Ledger.payer == user_id)
        .where(Ledger.beneficiary != user_id)
        .order_by(Ledger.created_at.desc())
    )


def ledger_get_owed_by_user(user_id: int) -> List[Ledger]:
    """Get all ledger entries where user owes money."""
    return (
        Ledger.select()
        .where(Ledger.payer != user_id)
        .where(Ledger.beneficiary == user_id)
        .order_by(Ledger.created_at.desc())
    )


def item_get_all():
    return Item.select().order_by(Item.name)


def item_get_all_with_stock():
    items = Item.select().order_by(Item.name)
    stocks = [
        ItemStock.select()
        .where(ItemStock.item == item)
        .order_by(ItemStock.logged_at.desc())
        .first()
        for item in items
    ]
    return zip(items, stocks)


def item_get_by_id(item_id: int) -> Item:
    return Item.get_by_id(item_id)


def item_add(
    name: str,
    icon: str,
) -> Item:
    item = Item.create(name=name, icon=icon, created_at=datetime.utcnow())
    ItemStock.create(item=item, stock=0)
    return item


def item_stock_set_by_id(item_id: int, stock: int) -> Item:
    return ItemStock.create(item=item_id, stock=stock)
