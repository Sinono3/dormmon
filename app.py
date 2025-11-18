"""Main Flask application."""
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from decimal import Decimal

from database_access import (
    init_database,
    get_all_users,
    get_user_by_id,
    create_user,
    user_exists,
    get_all_categories,
    get_category_by_id,
    create_category,
    category_exists,
    get_recent_events,
    create_event,
    add_event_cost_shares,
)
from face_encoding import (
    encode_face_from_image,
    average_encodings,
    encode_face_to_bytes,
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database on startup
init_database()


@app.route("/")
def index():
    """Main page."""
    return render_template('base.html')


# User routes
@app.route("/users")
def list_users():
    """List all users."""
    users = get_all_users()
    return render_template('users.html', users=users)


@app.route("/dialog/add_user")
def dialog_add_user():
    """Show add user dialog."""
    return render_template('dialogs/add_user.html')


@app.route("/users", methods=["POST"])
def handle_create_user():
    """Handle user creation."""
    name = request.form.get('name')
    if not name:
        return render_template('dialogs/error.html', error="Name is required"), 400
    
    if user_exists(name):
        return render_template('dialogs/error.html', error="User already exists"), 400
    
    files = request.files.getlist('images')
    if not files or not any(f.filename for f in files):
        return render_template('dialogs/error.html', error="At least one image is required"), 400
    
    # Process all images and combine encodings
    encodings = []
    temp_files = []
    
    try:
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                temp_files.append(filepath)
                
                encoding = encode_face_from_image(filepath)
                if encoding is not None:
                    encodings.append(encoding)
        
        if not encodings:
            return render_template('dialogs/error.html', error="No faces detected in images"), 400
        
        # Average all encodings
        avg_encoding = average_encodings(encodings)
        face_encoding_bytes = encode_face_to_bytes(avg_encoding)
        
        # Create user
        create_user(name, face_encoding_bytes)
        
        return render_template('dialogs/success.html', message=f'User "{name}" added successfully!')
    
    except Exception as e:
        return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400
    
    finally:
        # Clean up temporary files
        for filepath in temp_files:
            try:
                os.remove(filepath)
            except:
                pass


# Category routes
@app.route("/categories")
def list_categories():
    """List all categories."""
    categories = get_all_categories()
    return render_template('categories.html', categories=categories)


@app.route("/dialog/add_category")
def dialog_add_category():
    """Show add category dialog."""
    return render_template('dialogs/add_category.html')


@app.route("/categories", methods=["POST"])
def handle_create_category():
    """Handle category creation."""
    name = request.form.get('name')
    icon = request.form.get('icon', '📋')
    
    if not name:
        return render_template('dialogs/error.html', error="Name is required"), 400
    
    if category_exists(name):
        return render_template('dialogs/error.html', error="Category already exists"), 400
    
    try:
        create_category(name, icon)
        return render_template('dialogs/success.html', message=f'Category "{name}" added successfully!')
    except Exception as e:
        return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400


# Event routes
@app.route("/events")
def list_events():
    """List recent events."""
    events = get_recent_events()
    return render_template('events.html', events=events)


@app.route("/dialog/add_event")
def dialog_add_event():
    """Show add event dialog."""
    users = get_all_users()
    categories = get_all_categories()
    return render_template('dialogs/add_event.html', users=users, categories=categories)


@app.route("/events", methods=["POST"])
def handle_create_event():
    """Handle event creation."""
    user_id = request.form.get('user_id')
    category_id = request.form.get('category_id')
    cost_str = request.form.get('cost')
    notes = request.form.get('notes', '')
    benefactors = request.form.getlist('benefactors')
    
    # Handle photo upload
    photo_file = request.files.get('photo')
    if not photo_file or not photo_file.filename:
        return render_template('dialogs/error.html', error="Photo is required"), 400
    
    try:
        # Validate user and category exist
        get_user_by_id(int(user_id))
        get_category_by_id(int(category_id))
        
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
        event = create_event(
            user_id=int(user_id),
            category_id=int(category_id),
            photo_path=photo_path,
            cost=cost,
            notes=notes
        )
        
        # Add cost shares if cost is set and benefactors are specified
        if cost is not None and benefactors:
            benefactor_ids = [int(b) for b in benefactors]
            add_event_cost_shares(event.id, benefactor_ids)
        
        return render_template('dialogs/success.html', message='Event added successfully!')
    
    except ValueError as e:
        return render_template('dialogs/error.html', error=f"Invalid input: {str(e)}"), 400
    except Exception as e:
        return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400


if __name__ == "__main__":
    app.run(debug=True)
