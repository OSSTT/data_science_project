import os
from azure.storage.blob import BlobServiceClient

# Konfigurationsfunktion
def get_config():
    return {
        "connection_string": "HERE YOUR KEY",
        "container_name": "HERE YOUR CONTAINER NAME",
        "download_folder": "static/images/screenshots"
    }

def download_screenshots(connection_string, container_name, download_folder):
    try:
        # Verbindung zum Blob-Service herstellen
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        os.makedirs(download_folder, exist_ok=True)

        print(f"Beginne mit dem Herunterladen der Dateien aus dem Container '{container_name}'...")

        # Durchlauf alle Blobs im Container
        for blob in container_client.list_blobs():
            blob_name = blob.name
            download_path = os.path.join(download_folder, blob_name)

            if not os.path.exists(download_path):
                print(f"Lade '{blob_name}' herunter...")
                with open(download_path, "wb") as file:
                    blob_client = container_client.get_blob_client(blob_name)
                    file.write(blob_client.download_blob().readall())
                print(f"'{blob_name}' wurde erfolgreich heruntergeladen.")
            else:
                print(f"'{blob_name}' existiert bereits. Übersprungen.")
    except Exception as e:
        print(f"Fehler beim Herunterladen der Dateien: {e}")
