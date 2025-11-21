"""Database access layer - all database queries and operations."""

from datetime import datetime
from typing import List, Optional

from peewee import fn

from database import Event, EventCategory, Item, ItemStock, Ledger, User, db


def database_init():
    """Initialize database and create default category."""
    db.connect()
    db.create_tables([User, Item, ItemStock, EventCategory, Event, Ledger])

    # Create default category if not exists
    EventCategory.get_or_create(
        name="Default", defaults={"icon": "📋", "created_at": datetime.utcnow()}
    )

    db.close()


def user_get_all():
    """Get all users."""
    return User.select().order_by(User.name)


def user_get_by_id(user_id: int) -> User:
    """Get user by ID."""
    return User.get_by_id(user_id)


def user_create(name: str, face_encoding: bytes) -> User:
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


def category_create(name: str, icon: str) -> EventCategory:
    """Create a new event category."""
    return EventCategory.create(name=name, icon=icon, created_at=datetime.utcnow())


def category_exists(name: str) -> bool:
    """Check if category with given name exists."""
    return EventCategory.select().where(EventCategory.name == name).exists()


# Event operations
def event_get_recent(limit: int = 50):
    """Get recent events."""
    return Event.select().order_by(Event.logged_at.desc()).limit(limit)


def event_create(
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
def ledger_create(
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
        Ledger.select(fn.Sum(Ledger.amount))
        .where(Ledger.payer == user_id)
        .scalar() or 0
    )
    money_received = (
        Ledger.select(fn.Sum(Ledger.amount))
        .where(Ledger.beneficiary == user_id)
        .scalar() or 0
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
    """Get all items."""
    return Item.select().order_by(Item.name)


def item_get_by_id(item_id: int) -> Item:
    """Get item by ID."""
    return Item.get_by_id(item_id)
