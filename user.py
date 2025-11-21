from flask import Response, render_template, request
from werkzeug.utils import secure_filename
import os

from database_access import (
    user_get_all,
    user_create,
    user_exists,
    ledger_get_all_balances,
)
from face_encoding import (
    encode_face_from_image,
    average_encodings,
    encode_face_to_bytes,
)

def routes(app):
    @app.route("/users")
    def user_list():
        """List all users."""
        users = user_get_all()
        balances = ledger_get_all_balances()
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
            user_create(name, face_encoding_bytes)
        
            resp = render_template('dialogs/success.html', message=f'User "{name}" added successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'userUpdated'
            return resp
    
        except Exception as e:
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400
    
        finally:
            # Clean up temporary files
            for filepath in temp_files:
                try:
                    os.remove(filepath)
                except NotImplementedError:
                    pass

