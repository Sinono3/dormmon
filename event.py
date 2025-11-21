from flask import Response, render_template, request
from werkzeug.utils import secure_filename
import os
from decimal import Decimal

from database_access import (
    user_get_all,
    user_get_by_id,
    category_get_all,
    category_get_by_id,
    event_get_recent,
    event_create,
)

def routes(app):
    @app.route("/events")
    def event_list():
        """List recent events."""
        events = event_get_recent()
        return render_template('events.html', events=events)


    @app.route("/dialog/add_event")
    def event_add_dialog():
        """Show add event dialog."""
        users = user_get_all()
        categories = category_get_all()
        return render_template('dialogs/add_event.html', users=users, categories=categories)


    @app.route("/events", methods=["POST"])
    def event_add_handle():
        """Handle event creation."""
        user_id = request.form.get('user_id')
        category_id = request.form.get('category_id')
        cost_str = request.form.get('cost')
        notes = request.form.get('notes', '')
        # FIX:
        # costsharers = request.form.getlist('costsharers')
    
        # Handle photo upload
        photo_file = request.files.get('photo')
        if not photo_file or not photo_file.filename:
            return render_template('dialogs/error.html', error="Photo is required"), 400
    
        try:
            # Validate user and category exist
            user_get_by_id(int(user_id))
            category_get_by_id(int(category_id))
        
            # Save photo
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(photo_path)
        
            # Handle cost
            cost = None
            if cost_str:
                try:
                    cost = Decimal(cost_str)
                except:
                    return render_template('dialogs/error.html', error="Invalid cost value"), 400
        
            # Create event
            event = event_create(
                user_id=int(user_id),
                category_id=int(category_id),
                photo_path=photo_path,
                cost=cost,
                notes=notes
            )
        
            # FIX:
            # # Add cost shares if cost is set and costsharers are specified
            # if cost is not None and costsharers:
            #     costsharers_ids = [int(cs) for cs in costsharers]
            #     event_cost_share_get(event.id, costsharers_ids)
        
            resp = render_template('dialogs/success.html', message='Event added successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'eventUpdated'
            return resp
    
        except ValueError as e:
            return render_template('dialogs/error.html', error=f"Invalid input: {str(e)}"), 400
        except Exception as e:
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400
