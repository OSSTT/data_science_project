import os
import re
import requests
import pandas as pd
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor
import joblib

def process_weather_and_predict(file_path, api_key, model_path, output_path):
    # Dateinamen aus dem Pfad extrahieren
    file_name = os.path.basename(file_path)

    # Datum und Koordinaten aus dem Dateinamen extrahieren
    pattern = r'erkanntes_objekt_(\d{4}-\d{2}-\d{2})_\d{2}-\d{2}-\d{2}_lat([-\d.]+)_lon([-\d.]+?)\.png'
    match = re.match(pattern, file_name)

    if match:
        extracted_date = match.group(1)
        latitude = float(match.group(2))
        longitude = float(match.group(3))
    else:
        raise ValueError("Fehler: Dateiname hat kein gültiges Format.")

    try:
        start_date = datetime.strptime(extracted_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Ungültiges Datum im Dateinamen.")

    # API-Endpoint
    endpoint = 'https://api.openweathermap.org/data/3.0/onecall/day_summary'

    # Standortdefinition aus dem Dateinamen
    locations = [{"lat": latitude, "lon": longitude}]

    # Erstellung Liste, um die Ergebnisse zu speichern
    data = []

    # API-Daten abrufen
    for location in locations:
        formatted_date = start_date.strftime("%Y-%m-%d")
        params = {
            'lat': location["lat"],
            'lon': location["lon"],
            'date': formatted_date,
            'appid': api_key,
            'units': "metric"
        }

        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            weather_data = response.json()

            # Extraktion relevanten Werte
            temperature = weather_data.get("temperature", {})
            rainfall = weather_data.get("precipitation", {"total": 0})
            humidity = weather_data.get("humidity", {})

            # Speicherung Daten
            data.append({
                "temp min": temperature.get("min"),
                "temp max": temperature.get("max"),
                "temp afternoon": temperature.get("afternoon"),
                "temp night": temperature.get("night"),
                "temp evening": temperature.get("evening"),
                "temp morning": temperature.get("morning"),
                "humidity": humidity.get("afternoon"),
                "rainfall": rainfall.get("total", 0)
            })
        else:
            print(f"Fehler beim Abrufen der Daten für {location} am {formatted_date}")

    # Konvertierung DataFrame
    df = pd.DataFrame(data)

    # Berechnungen Spalten
    df['temp average'] = df[['temp min', 'temp max', 'temp afternoon', 'temp night', 'temp evening']].mean(axis=1)
    df['30-day rainfall cumulative'] = df['rainfall'].rolling(window=30, min_periods=1).sum()
    df['30-day temperature average'] = df['temp average'].rolling(window=30, min_periods=1).mean()
    df['30-day humidity average'] = df['humidity'].rolling(window=30, min_periods=1).mean()

    df['day_of_year'] = start_date.timetuple().tm_yday
    df['month'] = start_date.month
    df['season'] = df['month'].apply(
        lambda x: 1 if x in [12, 1, 2] else 2 if x in [3, 4, 5] else 3 if x in [6, 7, 8] else 4
    )

    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    df = df[[
        "temp min", "temp max", "temp afternoon", "temp night", "temp evening", "temp morning",
        "humidity", "rainfall", "temp average", "30-day rainfall cumulative",
        "30-day temperature average", "30-day humidity average", "day_of_year", "month", "season"
    ]]

    # ---- Vorhersageprozess ----

    # Model laden
    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Das Modell wurde unter {model_path} nicht gefunden.")

    # Spalten entfernen
    excluded_columns = ['Critical Growth Stage', 'Date', 'Latitude', 'Longitude', 'days_to_next_critical']
    prediction_features = df.drop(columns=excluded_columns, errors='ignore')

    # Vorhersage
    predictions = model.predict(prediction_features)
    df['Predicted_days_to_next_critical'] = predictions.astype(int)

    # Teststrecke-Logik
    df['Teststrecke'] = df.apply(
        lambda row: 'geeignet' if (
            15 <= row['30-day temperature average'] <= 20 and
            60 <= row['30-day humidity average'] <= 80 and
            6 <= row['30-day rainfall cumulative'] <= 10
        ) else 'nicht geeignet',
        axis=1
    )

    df['png_file_name'] = file_name

    df.to_csv(output_path, index=False)
    print(f"Vorhersagen gespeichert in: {output_path}")
    return df
