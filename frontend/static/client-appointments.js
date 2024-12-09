const appStatusSelect = document.getElementById('app-status')
appStatusSelect?.addEventListener("change", getUserAppointments);

function getUserAppointments() {
    const status = document.getElementById('app-status').value;
    fetch('/get_user_appointments_table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('appointment-record-table').innerHTML = data.tableHTML;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}