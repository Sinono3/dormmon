from flask import Response, render_template, request
from werkzeug.utils import secure_filename
import os

from database import ItemStock
from database_access import (
    user_get_all,
    user_get_by_id,
    category_get_all,
    category_get_by_id,
    event_get_recent,
    event_add,
    event_get_cost,
    ledger_add,
    item_get_all,
    item_get_by_id,
)

def routes(app):
    @app.route("/events")
    def event_list():
        """List recent events."""
        events = event_get_recent()
        # Calculate cost for each event from ledger entries
        events_with_cost = []
        for event in events:
            cost = event_get_cost(event.id)
            events_with_cost.append((event, cost))
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
            return render_template('dialogs/error.html', error="Photo is required"), 400
    
        try:
            # Validate user and category exist
            payer = user_get_by_id(int(user_id))
            category_get_by_id(int(category_id))
        
            # Save photo
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(photo_path)
        
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
                photo_path=photo_path,
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
        
            resp = render_template('dialogs/success.html', message='Event added successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'eventUpdated, userUpdated'
            return resp
    
        except ValueError as e:
            return render_template('dialogs/error.html', error=f"Invalid input: {str(e)}"), 400
        except Exception as e:
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400
