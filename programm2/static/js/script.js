// Funktion zum Sortieren der Daten
function sortData(data) {
    return data.sort((a, b) => {
        if (a.action_needed_in <= 50 && b.action_needed_in > 50) return -1;
        if (a.action_needed_in > 50 && b.action_needed_in <= 50) return 1;
        return a.action_needed_in - b.action_needed_in; // Sortieren nach aufsteigendem Wert
    });
}

// Funktion zum Färben der Tabellenzeilen
function colorTableRows() {
    const rows = document.querySelectorAll('tbody tr');

    rows.forEach(row => {
        const actionNeededIn = parseInt(row.dataset.actionNeededIn, 10);

        if (actionNeededIn >= 0 && actionNeededIn <= 50) {
            row.style.backgroundColor = 'red';
            row.style.color = 'white'; 
        } else if (actionNeededIn >= 51 && actionNeededIn <= 100) {
            row.style.backgroundColor = 'yellow';
            row.style.color = 'black';
        } else if (actionNeededIn > 100) {
            row.style.backgroundColor = 'green';
            row.style.color = 'white';
        }
    });
}

// Daten abrufen, sortieren und Tabelle aktualisieren
async function fetchAndUpdateTable() {
    try {
        const response = await fetch('/data'); 
        let data = await response.json();

        data = sortData(data);

        const tableBody = document.querySelector('tbody');
        tableBody.innerHTML = ''; 

        data.forEach((screenshot, index) => {
            const row = `
                <tr data-action-needed-in="${screenshot.action_needed_in}">
                    <td>${index + 1}</td>
                    <td>${screenshot.latitude}, ${screenshot.longitude}</td>
                    <td>${screenshot.date_time}</td>
                    <td>${screenshot.action_needed_in}</td>
                    <td>
                        <a href="/detail/${screenshot.file_name}">
                            Details
                        </a>
                    </td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });

        colorTableRows();
    } catch (error) {
        console.error('Fehler beim Abrufen der Daten:', error);
    }
}

// Tabelle alle 5 Sekunden aktualisieren
setInterval(fetchAndUpdateTable, 5000);

// Tabelle sofort beim Laden der Seite aktualisieren
fetchAndUpdateTable();
