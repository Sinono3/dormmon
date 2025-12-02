import os
import uuid

from flask import Response, render_template, request, url_for
from PIL import Image

from database import ItemStock
from database_access import (
    category_get_all,
    category_get_by_id,
    event_add,
    event_get_by_id,
    event_get_cost,
    event_get_recent,
    item_get_all,
    item_get_by_id,
    ledger_add,
    user_get_all,
    user_get_by_id,
)
from response_helpers import json_error, json_response, wants_json_response


def routes(app):
    @app.route("/events")
    def event_list():
        """List recent events."""
        limit = request.args.get("limit", type=int) or 50
        category_id = request.args.get("category_id", type=int)
        category_name = request.args.get("category_name")

        events = list(
            event_get_recent(
                limit=limit, category_id=category_id, category_name=category_name
            )
        )
        # Calculate cost for each event from ledger entries
        events_with_cost = []
        for event in events:
            cost = event_get_cost(event.id)
            events_with_cost.append((event, cost))

        if wants_json_response():
            return json_response(
                {
                    "events": [
                        {
                            "id": event.id,
                            "user": {
                                "id": event.user.id,
                                "name": event.user.name,
                            },
                            "category": {
                                "id": event.category.id,
                                "name": event.category.name,
                                "icon": event.category.icon,
                            },
                            "cost": cost,
                            "notes": event.notes,
                            "logged_at": event.logged_at.isoformat(),
                            "photo": {
                                "filename": event.photo_path,
                                "url": url_for(
                                    'download_file',
                                    name=event.photo_path,
                                    _external=True,
                                ),
                            },
                            "ledger_items": [
                                {
                                    "id": item.id,
                                    "payer_id": item.payer.id,
                                    "beneficiary_id": item.beneficiary.id,
                                    "amount": item.amount,
                                }
                                for item in event.ledger_items
                            ],
                            "stock": (
                                {
                                    "item_id": event.stock.item.id,
                                    "item_name": event.stock.item.name,
                                    "stock": event.stock.stock,
                                    "logged_at": event.stock.logged_at.isoformat(),
                                }
                                if event.stock
                                else None
                            ),
                        }
                        for event, cost in events_with_cost
                    ]
                }
            )

        return render_template('events.html', events_with_cost=events_with_cost)


    @app.route("/dialog/add_event")
    def event_add_dialog():
        """Show add event dialog."""
        users = user_get_all()
        categories = category_get_all()
        items = item_get_all()
        return render_template('dialogs/add_event.html', users=users, categories=categories, items=items)


    @app.route("/events", methods=["POST"])
    def event_add_handle():
        """Handle event creation."""
        user_id = request.form.get('user_id')
        category_id = request.form.get('category_id')
        cost = request.form.get('cost')
        notes = request.form.get('notes', '')
        costsharers = request.form.getlist('costsharers')
        item_id = request.form.get('item_id')
        stock = request.form.get('stock')
    
        # Handle photo upload
        photo_file = request.files.get('photo')
        if not photo_file or not photo_file.filename:
            if wants_json_response():
                return json_error("Photo is required", 400)
            return render_template('dialogs/error.html', error="Photo is required"), 400
    
        try:
            # Validate user and category exist
            payer = user_get_by_id(int(user_id))
            category_get_by_id(int(category_id))
        
            # Save photo
            filename = f"{uuid.uuid4()}.jpg"
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img = Image.open(photo_file)
            img = img.convert('RGB')
            img.save(photo_path, 'JPEG', optimize=True, quality=70)        

            # Handle stock
            item_stock_id = None
            if item_id and stock and stock.strip():
                # Validate item exists
                item = item_get_by_id(int(item_id))
                stock_value = int(stock)
                
                # Create ItemStock record
                item_stock = ItemStock.create(item=item, stock=stock_value)
                item_stock_id = item_stock.id
        
            # Handle cost
            sharer_ids = []
            if cost is not None:
                cost = int(cost)

                # Determine who shares the cost
                if costsharers:
                    # Only selected users share the cost
                    sharer_ids = [int(cs) for cs in costsharers]
                    if payer.id not in sharer_ids:
                        sharer_ids.append(payer.id)  # Include payer
                else:
                    # All users share the cost
                    all_users = user_get_all()
                    sharer_ids = [u.id for u in all_users]
                
                # Calculate amount per person
                num_sharers = len(sharer_ids)
                amount_per_person = round(cost / num_sharers)
                
        
            # Create event
            event = event_add(
                user_id=int(user_id),
                category_id=int(category_id),
                photo_path=filename,
                notes=notes,
                item_stock_id=item_stock_id
            )
        
            # Create ledger entries after event is inserted: payer pays for each sharer
            for sharer_id in sharer_ids:
                ledger_add(
                    event_id=event.id,
                    payer_id=payer.id,
                    beneficiary_id=sharer_id,
                    amount=amount_per_person,
                )
        
            if wants_json_response():
                return json_response(
                    {
                        "message": "Event added successfully!",
                        "event": {
                            "id": event.id,
                            "user_id": event.user.id,
                            "category_id": event.category.id,
                            "notes": event.notes,
                            "photo": {
                                "filename": event.photo_path,
                                "url": url_for(
                                    'download_file', name=event.photo_path, _external=True
                                ),
                            },
                        },
                    }
                )

            resp = render_template('dialogs/success.html', message='Event added successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'eventUpdated, userUpdated'
            return resp
    
        except ValueError as e:
            if wants_json_response():
                return json_error(f"Invalid input: {str(e)}", 400)
            return render_template('dialogs/error.html', error=f"Invalid input: {str(e)}"), 400
        except Exception as e:
            if wants_json_response():
                return json_error(str(e), 400)
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400

    @app.route("/dialog/eventpic/<int:event_id>")
    def event_picture_view(event_id):
        event = event_get_by_id(event_id)
        return render_template('dialogs/picture.html', picture_filename=event.photo_path)

