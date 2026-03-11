import matplotlib.pyplot as plt
from flask import Blueprint, render_template, request
import pandas as pd
from app.mongo import mongo
import os

visualization_bp = Blueprint('visualization', __name__)

# Route for rendering the visualization
@visualization_bp.route('/visualization', methods=['GET'])
def show_visualization():
    # Fetch climate data from MongoDB
    climate_data = mongo.db.climate_data.find()  # Make sure the 'climate_data' collection exists
    data = pd.DataFrame(climate_data)

    if not data.empty:
        # Check for necessary columns before plotting
        if 'date' in data.columns and 'temperature' in data.columns:
            plot_temperature_trend(data)
        else:
            return "Missing required data columns", 400
    else:
        return "No data available", 400

    # Display the image and data
    return render_template('visualization.html')

# Function to plot the temperature trend
def plot_temperature_trend(data):
    # Ensure the static/images directory exists
    image_dir = 'static/images'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # Plotting temperature trend
    plt.figure(figsize=(10, 5))
    plt.plot(data['date'], data['temperature'], label='Temperature', color='blue')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Trend Over Time')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Save the plot as an image
    plt.savefig(os.path.join(image_dir, 'temperature_trend.png'))
