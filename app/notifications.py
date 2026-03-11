from flask import Blueprint, render_template, session, redirect, url_for, flash
import requests

notifications_bp = Blueprint('notifications', __name__)

# Route for viewing notifications
@notifications_bp.route('/notifications', methods=['GET'])
def view_notifications():
    # Check if the user is logged in
    if not session.get('username'):
        flash('You must be logged in to view notifications.')
        return redirect(url_for('auth.login'))

    # API key for the news API
    api_key = '2bd3405c25204801af9c98c2195f4c9f'  # Replace with your actual API key

    # Fetching climate-related news from the NewsAPI
    url = f"https://newsapi.org/v2/everything?q=weather OR climate&sortBy=publishedAt&apiKey={api_key}&pageSize=12"
    response = requests.get(url)

    if response.status_code == 200:
        news_data = response.json().get('articles', [])  # Extract articles from API response
    else:
        news_data = []  # Handle API failure

    return render_template('notifications.html', news_data=news_data)
