from flask import Response, render_template, request

from database_access import (
    user_get_all,
    user_get_by_id,
    ledger_create,
)


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
            return render_template('dialogs/error.html', error="Both users are required"), 400

        if not amount_str:
            return render_template('dialogs/error.html', error="Amount is required"), 400

        try:
            from_user_id = int(from_user_id)
            to_user_id = int(to_user_id)
            amount = int(amount_str)
            
            if amount <= 0:
                return render_template('dialogs/error.html', error="Amount must be positive"), 400

            # Validate users exist
            user_get_by_id(from_user_id)
            user_get_by_id(to_user_id)

            # Create ledger entry (settlement - no event associated)
            ledger_create(
                event_id=None,
                payer_id=from_user_id,
                beneficiary_id=to_user_id,
                amount=amount,
            )

            resp = render_template('dialogs/success.html', message='Payment recorded successfully!')
            resp = Response(resp)
            resp.headers['HX-Trigger'] = 'userUpdated'
            return resp

        except ValueError as e:
            return render_template('dialogs/error.html', error=f"Invalid input: {str(e)}"), 400
        except Exception as e:
            return render_template('dialogs/error.html', error=f"Error: {str(e)}"), 400

