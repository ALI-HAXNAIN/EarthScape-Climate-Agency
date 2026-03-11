import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle


def load_and_train_model(file_path='data/climate_data.csv'):
    # load the dataset
    data = pd.read_csv(file_path)

    # Feature and target (temperature is predicted using other variables)
    features = data[['humidity' , 'co2_levels' , 'wind_speed' , 'rainfall' , 'pressure']]
    target = data['temperature']

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

    print("Model trained and saved as model.pkl")

    return model

if __name__ == "__main__":
    load_and_train_model()         