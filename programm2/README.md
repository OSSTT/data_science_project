# Wichtige Informationen

## Einrichtung für Windows Users

1. Klonen Sie dieses Projekt von GitHub.
2. Stellen Sie sicher, dass Sie sich im Projektordner befinden und nicht in einem übergeordneten Verzeichnis.
3. Erstellen Sie eine neue Python-virtuelle Umgebung. Hier sind die Befehle für Visual Studio unter Windows:
    - `python -m venv .venv`
    - `.venv\Scripts\activate`
4. Sobald Sie die virtuelle Umgebung aktiviert haben, installieren Sie die Pakete, die in der Datei requirements.txt aufgeführt sind. Verwenden Sie dazu den folgenden Befehl:
    - `pip install -r requirements.txt`

5. Um das Programm 2 auszuführen, werden folgende Daten benötigt:
    - **Connection String** für Microsoft Azure Blob Storage (`functions.py`)
    - **Containername** von Microsoft Azure Blob Storage (`functions.py`)
    - **API-Key** für OpenWeatherMap (`predictor.py`)
    
    Falls Sie diese Daten nicht selbst bereitstellen können, kontaktieren Sie bitte einen der Entwickler, thayath1@students.zhaw.ch oder ferrefab@students.zhaw.ch.
6. Um das Programm zu starten, führen Sie `app.py` aus.