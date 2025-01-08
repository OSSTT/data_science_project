from functions import *
from predictor import process_weather_and_predict
from flask import Flask, render_template, jsonify
import threading
import time
import os

app = Flask(__name__)

# Konfiguration
API_KEY = 'HERE YOUR KEY'
MODEL_PATH = 'critical_growth_model.pkl'
OUTPUT_FOLDER = 'output_csv'

@app.route('/')
def index():
    screenshots = []
    folder_path = os.path.join(app.root_path, 'static/images/screenshots')

    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".png"):
                try:
                    # Extraktion Daten aus dem Dateinamen
                    parts = file_name.split('_')
                    date_time = parts[2] + " " + parts[3].replace("-", ":")
                    lat = parts[4][3:]  
                    lon = parts[5][3:-4] 

                    screenshots.append({
                        "date_time": date_time,
                        "latitude": lat,
                        "longitude": lon,
                        "file_name": file_name
                    })
                except IndexError:
                    continue

    return render_template('index.html', screenshots=screenshots)

import pandas as pd

@app.route('/data')
def get_data():
    screenshots = []
    folder_path = os.path.join(app.root_path, 'static/images/screenshots')

    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".png"):
                try:
                    # Extraktion Daten aus dem Dateinamen
                    parts = file_name.split('_')
                    date_time = parts[2] + " " + parts[3].replace("-", ":")
                    lat = parts[4][3:]  
                    lon = parts[5][3:-4] 

                    # CSV-Datei basierend auf dem PNG-Dateinamen lesen
                    csv_file = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(file_name)[0]}.csv")
                    action_needed_in = "N/A" 
                    if os.path.exists(csv_file):
                        try:
                            df = pd.read_csv(csv_file)
                            if 'Predicted_days_to_next_critical' in df.columns:
                                action_needed_in = int(df['Predicted_days_to_next_critical'].iloc[0])
                        except Exception as e:
                            print(f"Fehler beim Lesen der CSV-Datei {csv_file}: {e}")

                    screenshots.append({
                        "date_time": date_time,
                        "latitude": lat,
                        "longitude": lon,
                        "file_name": file_name,
                        "action_needed_in": action_needed_in
                    })
                except IndexError:
                    continue

    return jsonify(screenshots)



@app.route('/detail/<filename>')
def detail(filename):
    # Pfad zur CSV-Datei basierend auf dem Dateinamen des Bildes
    csv_file = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(filename)[0]}.csv")
    data = {}

    # CSV-Datei lesen
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            # Extraktion der benötigten Spalten
            data = {
                "rainfall_cumulative": df.get("30-day rainfall cumulative", ["N/A"])[0],
                "temperature_average": round(df.get("30-day temperature average", [0.0])[0], 2),  
                "humidity_average": df.get("30-day humidity average", ["N/A"])[0],
                "predicted_days_to_critical": df.get("Predicted_days_to_next_critical", ["N/A"])[0],
                "test_track_conditions": df.get("Teststrecke", ["N/A"])[0]  
            }
        except Exception as e:
            print(f"Fehler beim Lesen der CSV-Datei {csv_file}: {e}")

    return render_template('detail.html', filename=filename, data=data)


@app.route('/maps')
def maps():
    return render_template('maps.html')

# Funktion, die die Downloads periodisch ausführt
def periodic_downloads():
    config = get_config()
    while True:
        time.sleep(5)  # Wartezeit zwischen den Downloads
        print("Starte den Download der Screenshots...")
        download_screenshots(
            connection_string=config["connection_string"],
            container_name=config["container_name"],
            download_folder=config["download_folder"]
        )

        # Verarbeiung heruntergeladene Bilder
        folder_path = config["download_folder"]
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".png"):
                    file_path = os.path.join(folder_path, file_name)
                    output_file = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(file_name)[0]}.csv")

                    if os.path.exists(output_file):
                        print(f"Prediction für {file_name} bereits vorhanden, überspringe...")
                        continue

                    try:
                        # Verarbeitung Bild & Erstellung CSV
                        process_weather_and_predict(
                            file_path=file_path,
                            api_key=API_KEY,
                            model_path=MODEL_PATH,
                            output_path=output_file
                        )
                    except Exception as e:
                        print(f"Fehler bei der Verarbeitung von {file_name}: {e}")

if __name__ == '__main__':
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    download_thread = threading.Thread(target=periodic_downloads, daemon=True)
    download_thread.start()
    
    app.run(debug=True)
