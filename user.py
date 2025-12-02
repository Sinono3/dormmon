from flask import Response, render_template, request
from werkzeug.utils import secure_filename
import os

from database_access import (
    user_get_all,
    user_add,
    user_exists,
    ledger_get_all_balances,
)
from face_encoding import (
    encode_face_from_image,
    average_encodings,
    encode_face_to_bytes,
)
from response_helpers import json_error, json_response, wants_json_response

def routes(app):
    @app.route("/users")
    def user_list():
        """List all users."""
        users = list(user_get_all())
        balances = ledger_get_all_balances()

        if wants_json_response():
            return json_response(
                {
                    "users": [
                        {
                            "id": user.id,
                            "name": user.name,
                            "created_at": user.created_at.isoformat(),
                            "balance": balances.get(user.id, 0),
                        }
                        for user in users
                    ]
                }
            )

        return render_template('users.html', users=users, balances=balances)


    @app.route("/dialog/add_user")
    def user_add_dialog():
        """Show add user dialog."""
        return render_template('dialogs/add_user.html')


    @app.route("/users", methods=["POST"])
    def user_add_handle():
        """Handle user creation."""
        name = request.form.get('name')
        if not name:
            if wants_json_response():
                return json_error("Name is required", 400)
            return render_template('dialogs/error.html', error="Name is required"), 400
    
        if user_exists(name):
            if wants_json_response():
                return json_error("User already exists", 400)
            return render_template('dialogs/error.html', error="User already exists"), 400
    
        files = request.files.getlist('images')
        if not files or not any(f.filename for f in files):
            if wants_json_response():
                return json_error("At least one image is required", 400)
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
            new_user = user_add(name, face_encoding_bytes)
        
            if wants_json_response():
                return json_response(
                    {
                        "message": f'User "{name}" added successfully!',
                        "user": {
                            "id": new_user.id,
                            "name": new_user.name,
                            "created_at": new_user.created_at.isoformat(),
                        },
                    }
                )

            resp = render_template('dialogs/success.html', message=f'User "{name}" added successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'userUpdated'
            return resp
    
        except Exception as e:
            if wants_json_response():
                return json_error(str(e), 400)
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400
    
        finally:
            # Clean up temporary files
            for filepath in temp_files:
                try:
                    os.remove(filepath)
                except:
                    pass

