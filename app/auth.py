from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

import app
import cloudinary
import cloudinary.uploader
from .mongo import mongo
import re

cloudinary.config( 
    cloud_name = 'du6rqyxva',
    api_key = '311459928837726',
    api_secret = 'IA4OdORNarUF7XN_8sixM-sCinI',
    secure = True
)

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = mongo.db.users.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['user_id'] = str(user['_id'])
            session['email'] = user.get('email', '')
            session['home_city'] = user.get('home_city') 
            session['home_country'] = user.get('home_country')
            session['profile_pic_url'] = user.get('profile_pic_url', '')
            return redirect(url_for('main.userdashboard'))
        else:
            flash('Login failed. Check username/password.', 'danger')
    return render_template('login.html')

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        security_question = request.form.get('security_question')
        security_answer = request.form.get('security_answer')

        if mongo.db.users.find_one({'username': username}):
            flash('Username already exists.', 'warning')
        else:
            hashed_pw = generate_password_hash(password)
            
            user_data = {
                'username': username, 
                'email': email, 
                'password': hashed_pw,
                'security_question': security_question,
                'security_answer': (security_answer.strip().lower() if security_answer else "")
            }

            mongo.db.users.insert_one(user_data)
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
            
    return render_template('signup.html')

@auth_blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    user_found = False
    user_data = None

    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')

        if action == 'find_user':
            user = mongo.db.users.find_one({'username': username})
            if user:
                user_found = True
                user_data = {
                    'username': user['username'],
                    'security_question': user.get('security_question', "No security question set.")
                }
            else:
                flash('Username not found.', 'danger')

        elif action == 'reset_password':
            answer = request.form.get('answer').strip().lower()
            new_password = request.form.get('new_password')
            
            user = mongo.db.users.find_one({'username': username})
            
            if user and user.get('security_answer') == answer:
                hashed_pw = generate_password_hash(new_password)
                mongo.db.users.update_one(
                    {'username': username},
                    {'$set': {'password': hashed_pw}}
                )
                flash('Password updated successfully! Please login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Incorrect answer to security question.', 'danger')
                user_found = True
                user_data = {'username': username, 'security_question': user['security_question']}

    return render_template('forgot_password.html', user_found=user_found, user_data=user_data)



@auth_blueprint.after_app_request  
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@auth_blueprint.route('/update-profile-pic', methods=['POST'])
def update_profile_pic():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # 1. HANDLE EMAIL UPDATE
    new_email = request.form.get('email')
    if new_email:
        # Update the database
        mongo.db.users.update_one(
            {'username': session['username']},
            {'$set': {'email': new_email}}
        )
        # Update the session so the UI shows the new email
        session['email'] = new_email 

    # 2. HANDLE PROFILE PICTURE
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        
        # Only try to upload if a file was actually selected
        if file and file.filename != '':
            upload_result = cloudinary.uploader.upload(file, folder="earthscape_profiles")
            image_url = upload_result.get('secure_url')
            
            mongo.db.users.update_one(
                {'username': session['username']},
                {'$set': {'profile_pic_url': image_url}}
            )
            session['profile_pic_url'] = image_url
            flash('Profile updated successfully!', 'success')
        else:
            # If only email was changed and no file was selected
            flash('Email updated!', 'success')

    return redirect(url_for('main.userdashboard'))

@auth_blueprint.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main.index'))