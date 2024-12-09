window.addEventListener("DOMContentLoaded", () => {
    let currentWeekOffset = 0;

    document.getElementById('prev-week').addEventListener('click', (event) => {
        event.preventDefault();
        currentWeekOffset -= 1;
        getDoctorSchedule(currentWeekOffset);
    });

    document.getElementById('next-week').addEventListener('click', (event) => {
        event.preventDefault();
        currentWeekOffset += 1;
        getDoctorSchedule(currentWeekOffset);
    });

    getDoctorSchedule(currentWeekOffset);
});

function getDoctorSchedule(weekOffset) {
    fetch('/get_doctor_schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ weekOffset: weekOffset })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('doctor-schedule-table').innerHTML = data.tableHTML;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}