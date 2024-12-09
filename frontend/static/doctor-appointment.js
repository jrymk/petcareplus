window.addEventListener("DOMContentLoaded", () => {
    const appointmentDetailsDiv = document.getElementById('appointment-details');
    const appointmentId = appointmentDetailsDiv.getAttribute('data-appointment-id');

    if (appointmentId) {
        fetch(`/api/get_appointment_details?appointment_id=${appointmentId}`)
            .then(response => response.json())
            .then(data => {
                // Process and display appointment details
                console.log(data);
            })
            .catch(error => console.error('Error fetching appointment details:', error));
    }
});

