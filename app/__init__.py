from flask import Flask
from .mongo import mongo, mail # Import both from .mongo
from .auth import auth_blueprint
from .feedback import feedback_bp as feedback_blueprint
from .main import main as main_blueprint
from .notifications import notifications_bp as notifications_blueprint

def create_app():
    app = Flask(__name__ , static_folder='../static' , template_folder='../templates')
    
    app.secret_key = "earthscape_secret_key"
    app.config["MONGO_URI"] = "mongodb://localhost:27017/earthscape_climate_agency"
    
    # Mail Config
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
    app.config['MAIL_PASSWORD'] = 'your-password'

    # Initialize
    mongo.init_app(app)
    mail.init_app(app)

    # Register
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(feedback_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(notifications_blueprint)

    return app