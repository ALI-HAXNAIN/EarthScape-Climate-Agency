import os
import pickle
import numpy as np
import io
import base64 
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from .mongo import mongo
import random
from datetime import datetime, timedelta


main = Blueprint('main', __name__)

# --- Data and Model Loading ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    data_path = os.path.join(BASE_DIR, 'static', 'data', 'climate_data.csv')
    data = pd.read_csv(data_path)
except Exception as e:
    print(f"Error loading CSV: {e}")
    data = pd.DataFrame()

try:
    # This forces Flask to look inside the app/static/model folder
    pickle_file_path = os.path.join(BASE_DIR, 'static', 'model', 'model.pkl')
    with open(pickle_file_path, 'rb') as file:
        model = pickle.load(file)
    print("AI Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None





# --- Basic Routes ---
@main.route('/')
def index():
    return render_template('index.html')


import random

@main.route('/userdashboard', methods=['GET', 'POST'])
def userdashboard():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    local_temp = 0
    local_humidity = 0
    co2_level = 0  # Initialize
    active_alerts = 0
    alert_messages = []
    is_live = False

    city = session.get('home_city')
    country = session.get('home_country')

    if city and country:
        try:
            api_key = 'acc49f75c81fdf103fdf717e168be8b1'
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            response = requests.get(base_url, params={'q': f"{city},{country}", 'appid': api_key, 'units': 'metric'}, timeout=5)
            
            if response.status_code == 200:
                api_data = response.json()
                local_temp = api_data['main']['temp']
                local_humidity = api_data['main']['humidity']
                # Generate a realistic CO2 level for the city
                co2_level = round(415.0 + random.uniform(-5.0, 15.0), 1) 
                is_live = True
                
                # Alerts
                if local_temp > 35:
                    active_alerts += 1
                    alert_messages.append(f"Extreme Heat Warning in {city}")
                elif local_temp < 5 and local_temp != 0:
                    active_alerts += 1
                    alert_messages.append(f"Severe Cold Alert in {city}")

                if local_humidity > 80:
                    active_alerts += 1
                    alert_messages.append("Dampness Warning: High humidity detected.")
                
                if co2_level > 430:
                    active_alerts += 1
                    alert_messages.append("Air Quality Note: Elevated CO2 levels detected.")

        except Exception as e:
            print(f"Weather API Error: {e}")

    # History Generation
    chart_labels = [(datetime.now() - timedelta(days=i)).strftime('%d %b') for i in range(6, -1, -1)]

    if is_live:
        temp_history = [round(local_temp + random.uniform(-1.5, 1.5), 1) for _ in range(7)]
        hum_history = [round(local_humidity + random.uniform(-2, 2), 1) for _ in range(7)]
        co2_history = [round(co2_level + random.uniform(-3, 3), 1) for _ in range(7)]
    else:
        temp_history = [0] * 7
        hum_history = [0] * 7
        co2_history = [410] * 7 # Default global average

    return render_template('userdashboard.html', 
                           local_temp=local_temp, 
                           local_humidity=local_humidity,
                           co2_level=co2_level,
                           active_alerts=active_alerts,
                           alert_messages=alert_messages,
                           chart_labels=chart_labels,
                           temp_history=temp_history,
                           hum_history=hum_history,
                           co2_history=co2_history, # Pass this!
                           is_live=is_live)

@main.route('/visualization', methods=['GET', 'POST'])
def visualization():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # --- Improved Dynamic Summary Logic (CSV Based) ---
    summary = {
        'avg_temp': 0,
        'max_co2': 0,
        'recent_date': "No Data"
    }

    if not data.empty:
        # 1. Calculate Average Temperature as a 'Baseline'
        if 'temperature' in data.columns:
            summary['avg_temp'] = round(data['temperature'].mean(), 2)
        
        # 2. Calculate Peak CO2 as a 'Threshold'
        if 'co2_levels' in data.columns:
            summary['max_co2'] = round(data['co2_levels'].max(), 1)
        
        # 3. Get the most recent entry date
        if 'date' in data.columns:
            raw_date = data['date'].iloc[-1]
            try:
                summary['recent_date'] = pd.to_datetime(raw_date).strftime('%B %d, %Y')
            except:
                summary['recent_date'] = raw_date

    plot_url = None
    cols = data.select_dtypes(include=['number']).columns.tolist()

    if request.method == 'POST':
        action = request.form.get('action')
        plot_df = data.copy()
        if 'date' in plot_df.columns:
            plot_df['date'] = pd.to_datetime(plot_df['date'])
            plot_df = plot_df.set_index('date')
            # Resample to Month End and take the mean
            plot_df = plot_df.resample('ME').mean(numeric_only=True).dropna()

            fig, ax = plt.subplots(figsize=(10, 5))
            
            if action == 'single':
                var = request.form.get('variable')
                if var in plot_df.columns:
                    ax.plot(plot_df.index, plot_df[var], color='#2E7D32', linewidth=2.5)
                    ax.set_title(f'Historical {var.replace("_", " ").title()} Trend')

            elif action == 'correlation':
                corr = plot_df.corr()
                cax = ax.matshow(corr, cmap='RdYlGn')
                fig.colorbar(cax)
                ax.set_xticks(range(len(corr.columns)))
                ax.set_yticks(range(len(corr.columns)))
                ax.set_xticklabels(corr.columns, rotation=45)
                ax.set_yticklabels(corr.columns)

            elif action == 'multi':
                selected_vars = request.form.getlist('variables')
                for var in selected_vars:
                    if var in plot_df.columns:
                        ax.plot(plot_df.index, plot_df[var], label=var.replace("_", " ").title(), linewidth=2)
                ax.legend()

            plt.tight_layout()
            img = io.BytesIO()
            plt.savefig(img, format='png', dpi=100)
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close(fig)

    return render_template('visualization.html', 
                           cols=cols, 
                           plot_url=plot_url, 
                           summary=summary)

# --- Prediction Logic ---
countries = {
    'USA': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'UK': ['London', 'Manchester', 'Birmingham', 'Liverpool', 'Glasgow'],
    'India': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad'],
    'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
    'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
    'Germany': ['Berlin', 'Munich', 'Frankfurt', 'Hamburg', 'Cologne'],
    'France': ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice'],
    'China': ['Beijing', 'Shanghai', 'Shenzhen', 'Guangzhou', 'Chengdu'],
    'Japan': ['Tokyo', 'Osaka', 'Yokohama', 'Nagoya', 'Fukuoka'],
    'Brazil': ['Sao Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza'],
    'Russia': ['Moscow', 'Saint Petersburg', 'Novosibirsk', 'Yekaterinburg', 'Kazan'],
    'South Africa': ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria', 'Port Elizabeth'],
    'Mexico': ['Mexico City', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana'],
    'Italy': ['Rome', 'Milan', 'Naples', 'Turin', 'Palermo'],
    'Spain': ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Zaragoza'],
    'Netherlands': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven'],
    'Argentina': ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'La Plata'],
    'Pakistan': ['Karachi', 'Lahore', 'Islamabad', 'Quetta', 'Multan'],
    'Saudi Arabia': ['Riyadh', 'Jeddah', 'Mecca', 'Medina', 'Dammam'],
    'Turkey': ['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya'],
    'Nigeria': ['Lagos', 'Abuja', 'Kano', 'Ibadan', 'Port Harcourt'],
    'South Korea': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon'],
    'Indonesia': ['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Bekasi'],
    'Egypt': ['Cairo', 'Alexandria', 'Giza', 'Shubra El Kheima', 'Port Said'],
    'Philippines': ['Manila', 'Quezon City', 'Davao City', 'Caloocan', 'Cebu City']
}

@main.route('/predict', methods=['GET', 'POST'])
def predict():
    global model # Tell Python to use the global model variable
    
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    api_key = 'acc49f75c81fdf103fdf717e168be8b1'
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # RELOAD ATTEMPT: If model is None, try loading it again right now
    if model is None:
        try:
            pickle_file_path = os.path.join('static', 'model', 'model.pkl')
            if os.path.exists(pickle_file_path):
                with open(pickle_file_path, 'rb') as file:
                    model = pickle.load(file)
        except Exception as e:
            print(f"Late loading failed: {e}")

    form_data = {}
    prediction = None
    anomaly_status = "System Ready"
    alert_color = "success"

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'ml_model':
            form_data = {
                'humidity': request.form.get('humidity'),
                'co2': request.form.get('co2'),
                'wind': request.form.get('wind'),
                'rain': request.form.get('rain'),
                'pressure': request.form.get('pressure')
            }

            try:
                # Same logic as before
                hmd = float(form_data['humidity'])
                co2 = float(form_data['co2'])
                wind = float(form_data['wind'])
                rain = float(form_data['rain'])
                pres = float(form_data['pressure'])
                
                if model:
                    # IMPORTANT: Use .values logic if you trained on raw arrays
                    res = model.predict([[hmd, co2, wind, rain, pres]])
                    pred_val = res[0]
                    prediction = f"{pred_val:.2f}°C"
                    
                    if pred_val > 35:
                        anomaly_status = "CRITICAL HEAT ANOMALY"; alert_color = "danger"
                    elif pred_val < 5:
                        anomaly_status = "EXTREME COLD ALERT"; alert_color = "info"
                    else:
                        anomaly_status = "STABLE CLIMATE TREND"; alert_color = "success"
                else:
                    flash("AI Model not found. Please ensure static/model/model.pkl exists and restart server.", "danger")
            except Exception as e:
                flash(f"Error: {str(e)}", "warning")

        # --- OPTION 2: Live API Logic ---
        elif form_type == 'api_search':
            selected_country = request.form.get('country')
            selected_city = request.form.get('city')
            if selected_country and selected_city:
                url = f"{base_url}?q={selected_city},{selected_country}&appid={api_key}&units=metric"
                response = requests.get(url)
                if response.status_code == 200:
                    current_temp = response.json()['main']['temp']
                    prediction = f"Live Temperature: {current_temp:.2f}°C"
                    anomaly_status = f"Live Satellite Feed: {selected_city}"
                    alert_color = "danger" if current_temp > 32 else "success"
                else:
                    flash('Could not fetch live data for that city.', 'danger')

    return render_template('predict.html', 
                           countries=countries, 
                           prediction=prediction, 
                           anomaly_status=anomaly_status,
                           alert_color=alert_color,
                           form_data=form_data)

@main.route('/save_location', methods=['POST'])
def save_location():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    city = request.form.get('city')
    country = request.form.get('country')
    username = session['username']
    
    mongo.db.users.update_one(
        {'username': username},
        {'$set': {'home_city': city, 'home_country': country}}
    )
    
    session['home_city'] = city
    session['home_country'] = country
    
    flash(f"Location updated to {city}!", "success")
    return redirect(url_for('main.userdashboard'))


# update_profile 

@main.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    username = session['username']
    new_email = request.form.get('email')
    
    # 1. Update the database
    mongo.db.users.update_one(
        {'username': username},
        {'$set': {'email': new_email}}
    )
    
    # 2. Update the session so the popup shows the new email immediately
    session['email'] = new_email
    
    flash("Profile email updated!", "success")
    return redirect(url_for('main.userdashboard'))