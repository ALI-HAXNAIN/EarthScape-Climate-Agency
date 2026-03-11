from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_mail import Message
from .mongo import mongo , mail
from . import mail # Import mail from the current package
import re

feedback_bp = Blueprint('feedback', __name__)

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

@feedback_bp.route('/Feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        email = request.form.get('email')
        user_feedback = request.form.get('feedback')

        if not email or not user_feedback:
            flash('All fields are required!', 'danger')
        elif not is_valid_email(email):
            flash('Invalid email!', 'danger')
        else:
            mongo.db.feedback.insert_one({'email': email, 'feedback': user_feedback})
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('feedback.thank_you'))

    return render_template('feedback.html')

@feedback_bp.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')