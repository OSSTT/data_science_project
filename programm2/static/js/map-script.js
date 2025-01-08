// Start Karte Schweiz
var map = L.map('map').setView([46.8182, 8.2275], 7);


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

// Marker-Gruppe 
var markerGroup = L.layerGroup().addTo(map);

// Funktion farbige Icons 
function getMarkerIcon(actionNeededIn) {
    let color;

    if (actionNeededIn >= 0 && actionNeededIn <= 50) {
        color = 'red';
    } else if (actionNeededIn >= 51 && actionNeededIn <= 100) {
        color = 'yellow';
    } else if (actionNeededIn > 100) {
        color = 'green';
    } else {
        color = 'gray'; 
    }

    return L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid black;"></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
    });
}

// Abrufen von Daten & Aktualisierung Karte
async function fetchAndUpdateMarkers() {
    try {
        const response = await fetch('/data');
        const data = await response.json();

        markerGroup.clearLayers();

        data.forEach(({ latitude, longitude, file_name, action_needed_in }) => {
            const marker = L.marker([latitude, longitude], { icon: getMarkerIcon(action_needed_in) }).addTo(markerGroup);

            marker.on('click', () => {
                window.location.href = `/detail/${file_name}`;
            });
        });
    } catch (error) {
        console.error('Fehler beim Abrufen der Daten:', error);
    }
}


// Marker alle 5 Sekunden aktualisieren
setInterval(fetchAndUpdateMarkers, 5000);

// Marker sofort beim Laden der Seite aktualisieren
fetchAndUpdateMarkers();
