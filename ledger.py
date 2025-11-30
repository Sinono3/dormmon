from flask import Response, render_template, request

from database_access import (
    user_get_all,
    user_get_by_id,
    ledger_add,
)
from response_helpers import json_error, json_response, wants_json_response


def routes(app):
    @app.route("/dialog/pay")
    def ledger_pay_dialog():
        """Show pay dialog."""
        users = user_get_all()
        return render_template('dialogs/pay.html', users=users)

    @app.route("/dialog/pay/<int:from_user_id>/<int:to_user_id>")
    def ledger_pay_dialog_prefilled(from_user_id, to_user_id):
        """Show pay dialog with prefilled users."""
        users = user_get_all()
        from_user = user_get_by_id(from_user_id)
        to_user = user_get_by_id(to_user_id)
        return render_template(
            'dialogs/pay.html',
            users=users,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            from_user_name=from_user.name,
            to_user_name=to_user.name,
        )

    @app.route("/ledger/pay", methods=["POST"])
    def ledger_pay_handle():
        """Handle pay creation."""
        from_user_id = request.form.get('from_user_id')
        to_user_id = request.form.get('to_user_id')
        amount_str = request.form.get('amount')

        if not from_user_id or not to_user_id:
            message = "Both users are required"
            if wants_json_response():
                return json_error(message, 400)
            return render_template('dialogs/error.html', error=message), 400

        if not amount_str:
            message = "Amount is required"
            if wants_json_response():
                return json_error(message, 400)
            return render_template('dialogs/error.html', error=message), 400

        try:
            from_user_id = int(from_user_id)
            to_user_id = int(to_user_id)
            amount = int(amount_str)
            
            if amount <= 0:
                message = "Amount must be positive"
                if wants_json_response():
                    return json_error(message, 400)
                return render_template('dialogs/error.html', error=message), 400

            # Validate users exist
            user_get_by_id(from_user_id)
            user_get_by_id(to_user_id)

            # Create ledger entry (settlement - no event associated)
            entry = ledger_add(
                event_id=None,
                payer_id=from_user_id,
                beneficiary_id=to_user_id,
                amount=amount,
            )

            if wants_json_response():
                return json_response(
                    {
                        "message": "Payment recorded successfully!",
                        "ledger_entry": {
                            "id": entry.id,
                            "event_id": entry.event.id if entry.event else None,
                            "payer_id": entry.payer.id,
                            "beneficiary_id": entry.beneficiary.id,
                            "amount": entry.amount,
                            "created_at": entry.created_at.isoformat(),
                        },
                    }
                )

            resp = render_template('dialogs/success.html', message='Payment recorded successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'userUpdated'
            return resp

        except ValueError as e:
            if wants_json_response():
                return json_error(f"Invalid input: {str(e)}", 400)
            return render_template('dialogs/error.html', error=f"Invalid input: {str(e)}"), 400
        except Exception as e:
            if wants_json_response():
                return json_error(str(e), 400)
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400


