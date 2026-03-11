from flask_pymongo import PyMongo
from flask_mail import Mail
from flask import current_app as app

# Initialize the PyMongo object to interact with MongoDB
mongo = PyMongo()
mail = Mail() # Move mail here to stop the circular import error

# Function to initialize PyMongo with Flask app
def init_app(app):
    mongo.init_app(app)
    print("MongoDB connected successfully!")