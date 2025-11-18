"""Database access layer - all database queries and operations."""
from database import (
    db, User, Item, ItemStock, EventCategory, Event, EventCostShare
)
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


def init_database():
    """Initialize database and create default category."""
    db.connect()
    db.create_tables([
        User, Item, ItemStock, EventCategory, Event, EventCostShare
    ])
    
    # Create default category if not exists
    EventCategory.get_or_create(
        name='Default',
        defaults={'icon': '📋', 'created_at': datetime.utcnow()}
    )
    
    db.close()


# User operations
def get_all_users():
    """Get all users."""
    return User.select().order_by(User.name)


def get_user_by_id(user_id: int) -> User:
    """Get user by ID."""
    return User.get_by_id(user_id)


def create_user(name: str, face_encoding: bytes) -> User:
    """Create a new user."""
    return User.create(
        name=name,
        face_encoding=face_encoding,
        created_at=datetime.utcnow()
    )


def user_exists(name: str) -> bool:
    """Check if user with given name exists."""
    return User.select().where(User.name == name).exists()


# Event Category operations
def get_all_categories():
    """Get all event categories."""
    return EventCategory.select().order_by(EventCategory.name)


def get_category_by_id(category_id: int) -> EventCategory:
    """Get category by ID."""
    return EventCategory.get_by_id(category_id)


def create_category(name: str, icon: str) -> EventCategory:
    """Create a new event category."""
    return EventCategory.create(
        name=name,
        icon=icon,
        created_at=datetime.utcnow()
    )


def category_exists(name: str) -> bool:
    """Check if category with given name exists."""
    return EventCategory.select().where(EventCategory.name == name).exists()


# Event operations
def get_recent_events(limit: int = 50):
    """Get recent events."""
    return Event.select().order_by(Event.logged_at.desc()).limit(limit)


def create_event(
    user_id: int,
    category_id: int,
    photo_path: str,
    cost: Optional[Decimal] = None,
    notes: str = "",
    item_stock_id: Optional[int] = None
) -> Event:
    """Create a new event."""
    return Event.create(
        user=user_id,
        category=category_id,
        photo_path=photo_path,
        cost=cost,
        notes=notes,
        stock=item_stock_id,
        logged_at=datetime.utcnow(),
        modified_at=datetime.utcnow()
    )


def add_event_cost_shares(event_id: int, user_ids: List[int]):
    """Add cost shares for an event."""
    for user_id in user_ids:
        EventCostShare.create(event=event_id, user=user_id)


def get_event_cost_shares(event_id: int):
    """Get all users who share the cost of an event."""
    return User.select().join(EventCostShare).where(
        EventCostShare.event == event_id
    )


# Item operations (kept for potential future use)
def get_all_items():
    """Get all items."""
    return Item.select().order_by(Item.name)


def get_item_by_id(item_id: int) -> Item:
    """Get item by ID."""
    return Item.get_by_id(item_id)

