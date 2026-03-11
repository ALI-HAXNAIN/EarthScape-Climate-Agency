import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import pickle  # REQUIRED TO SAVE THE MODEL
import os

# Load the climate data
def load_data(file_path):
    # Ensure the path matches your project structure
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Check your 'static/data' folder.")
        return None
    data = pd.read_csv(file_path)
    return data

# Function to train and SAVE the model
def train_trend_prediction_model(data):
    # Features must match the 5 inputs on your predict.html page
    features = data[['humidity', 'co2_levels', 'wind_speed', 'rainfall', 'pressure']]
    target = data['temperature']
    
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    
    # Train Random Forest (Requirement for predictive analysis)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # --- FIX: SAVE THE MODEL FILE ---
    model_dir = 'static/model'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    model_path = os.path.join(model_dir, 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model saved successfully at {model_path}")
    return model

# Detect anomalies (Requirement for EarthScape Climate Agency)
def detect_anomalies(data):
    features = data[['temperature', 'humidity', 'co2_levels', 'wind_speed', 'rainfall', 'pressure']]
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    data['anomaly'] = iso_forest.fit_predict(features)
    anomalies = data[data['anomaly'] == -1]
    print(f"Anomalies detected in historical data: {len(anomalies)}")
    return anomalies

# Visualize correlations (Requirement for visual representation)
def visualize_correlations(data):
    plt.figure(figsize=(10, 8))
    correlation_matrix = data[['temperature', 'humidity', 'co2_levels', 'wind_speed', 'rainfall', 'pressure']].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
    plt.title('Correlation Matrix - Climate Variables')
    plt.tight_layout()
    plt.savefig('static/images/correlation_heatmap.png') # Save for the dashboard
    plt.show()

if __name__ == "__main__":
    # Updated path to match Flask project standards
    file_path = "static/data/climate_data.csv" 
    climate_data = load_data(file_path)

    if climate_data is not None:
        # 1. Train and SAVE model
        trend_model = train_trend_prediction_model(climate_data)
        # 2. Detect anomalies
        anomalies = detect_anomalies(climate_data)
        # 3. Visualize correlations
        visualize_correlations(climate_data)