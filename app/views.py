from flask import Blueprint, render_template, current_app

main = Blueprint('main', __name__)

# Route for rendering the index page
@main.route('/')
def index():
    try:
        # Rendering the index page (ensure index.html is present in the templates folder)
        return render_template('index.html')
    except Exception as e:
        # Log error (if any) and provide a user-friendly message
        current_app.logger.error(f"Error rendering index page: {e}")
        return "An error occurred while rendering the page. Please try again later.", 500
