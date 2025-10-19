from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import url_for

def send_reset_email(mail, app, user_email):
    """Send a password reset link to the user's email."""
    s = URLSafeTimedSerializer(app.secret_key)
    token = s.dumps(user_email, salt='password-reset')

    reset_url = url_for('reset_password', token=token, _external=True)

    msg = Message(
        subject="Password Reset Request",
        recipients=[user_email],
        body=f"Click the link to reset your password: {reset_url}"
    )

    mail.send(msg)
