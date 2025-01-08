import cv2
from ultralytics import YOLO
from datetime import datetime
import os
import time
import serial
import pynmea2
from azure.storage.blob import BlobServiceClient
import threading
import numpy as np

class GPSReader:
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.latitude = None
        self.longitude = None
        self.running = True

    def start(self):
        self.thread = threading.Thread(target=self._read_gps_data, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def _read_gps_data(self):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as gps_serial:
                while self.running:
                    line = gps_serial.readline().decode('ascii', errors='replace').strip()
                    if line.startswith('$GPGGA'):
                        try:
                            msg = pynmea2.parse(line)
                            self.latitude = msg.latitude
                            self.longitude = msg.longitude
                        except pynmea2.ParseError:
                            pass
        except serial.SerialException as e:
            print(f"Fehler beim Zugriff auf den Port {self.port}: {e}")

def upload_to_blob_storage_async(connection_string, container_name, file_path, filename):
    def upload():
        try:
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"Datei '{filename}' erfolgreich in Azure Blob Storage hochgeladen.")
        except Exception as e:
            print(f"Fehler beim Hochladen von '{filename}' in Azure Blob Storage: {e}")

    threading.Thread(target=upload, daemon=True).start()

def apply_segmentation_mask(frame, mask, color=(0, 255, 0)):
    alpha = 0.5 
    colored_mask = np.zeros_like(frame, dtype=np.uint8)
    for c in range(3): 
        colored_mask[:, :, c] = mask * color[c]
    return cv2.addWeighted(frame, 1, colored_mask, alpha, 0)

if __name__ == "__main__":
    connection_string = "HERE YOUR KEY" # Connection-String einfügen
    container_name = " HERE CONTAINER NAME" # Containername wird benötigt
    gps_port = "COM3" # COM Port zuerst nachschauen
    gps_reader = GPSReader(gps_port)
    gps_reader.start()

    model = YOLO('hub.pt') 
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    cap = cv2.VideoCapture(1)
    next_screenshot_time = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Durchführung der Objekterkennung mit Segmentierung
            results = model.predict(frame, conf=0.5)
            annotated_frame = frame.copy()

            # Über Segmentierungsergebnisse iterieren
            if results[0].masks:
                for mask in results[0].masks.data:  
                    mask = mask.cpu().numpy().astype(np.uint8)
                    annotated_frame = apply_segmentation_mask(annotated_frame, mask)

            # OpenCV-Anzeige
            cv2.imshow("YOLOv8-Segmentierung", annotated_frame)

            current_time = time.time()
            if results[0].masks and current_time >= next_screenshot_time:
                latitude = gps_reader.latitude if gps_reader.latitude else "Unbekannt"
                longitude = gps_reader.longitude if gps_reader.longitude else "Unbekannt"

                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"erkanntes_objekt_{timestamp}_lat{latitude}_lon{longitude}.png"
                file_path = os.path.join(screenshot_dir, filename)
                cv2.imwrite(file_path, annotated_frame)
                print(f"Screenshot gespeichert: {file_path} mit GPS-Koordinaten: {latitude}, {longitude}")

                upload_to_blob_storage_async(connection_string, container_name, file_path, filename)
                next_screenshot_time = current_time + 10

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        gps_reader.stop()
