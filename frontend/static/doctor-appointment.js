let appointmentId = 0;
let petIndex = 0;
let pets = [];

window.addEventListener("DOMContentLoaded", () => {

    const appointmentDetailsDiv = document.getElementById('appointment-details');
    appointmentId = appointmentDetailsDiv.getAttribute('data-appointment-id');
    const thisAppointment = document.getElementById('this-appointment');

    if (appointmentId) {
        fetch(`/get_appointment_details?appointment_id=${appointmentId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Response not OK');
                }
                return response.json();
            })
            .then(data => {
                console.log(data);                
                if (data.success) {
                    const appointment = data.appointment;
                    let service_time = String(appointment.service_duration % 60) + "分鐘";
                    if (appointment.service_duration >= 60) {
                        service_time = String(Math.floor(appointment.service_duration / 60)) + "小時" + service_time;
                    }
                    
                    appointmentDetailsDiv.innerHTML = `
                        <h3>Appointment Details</h3>
                        <table style="border-collapse: collapse; background-color: #FFFFDD">
                            <tr>
                                <th>Owner name</th>
                                <td>${appointment.username ? appointment.username : 'N/A'}</td>
                            </tr>
                            <tr>
                                <th rowspan="2">Service</th>
                                <td>${appointment.service_name ? appointment.service_name : 'N/A'} / ${service_time}</td>
                            </tr>
                            <tr>
                                <td>${appointment.service_description ? appointment.service_description : 'N/A'}</td>
                            </tr>
                            <tr>
                                <th>Contact</th>
                                <td>${appointment.contact ? appointment.contact : 'N/A'}</td>
                            </tr>
                        </table>
                        <br>
                    `;
                    pets = appointment.pets;

                    for (let i = 0; i < pets.length; i++) {
                        if (appointmentDetailsDiv.getAttribute('data-pet-id') == pets[i].pet_id) {
                            petIndex = i;
                            break;
                        }
                    }

                    reloadPetInfo();
                } else {
                    throw new Error(data.error);
                }
            })
            .then(() => {
                
            })
            .catch(error => {
                console.error('Error fetching appointment details: ', error);
                thisAppointment.innerHTML = `<p style="color: red">Failed to load appointment details.<br>Error: ${error}</p>`;
            });
        
        }
});


function reloadPetInfo() {
    let petSelectorDiv = document.getElementById('pet-selector');

    let petSelectorHtml = `
    <table>
        <tr>
            <th>Pet name</th>
            <th>Species</th>
            <th>Breed</th>
            <th>Age</th>
            <th>Gender</th>
            <th></th>
        </tr>`;
    
    for (let i = 0; i < pets.length; i++) {
        petSelectorHtml += `
            <tr style='background-color: ${petIndex == i ? "#DDFFFF" : "#FFFFFF"}'>
                <td>${petIndex == i ? '<strong>' : ''}${pets[i].name}${petIndex == i ? '</strong>' : ''}</td>
                <td>${pets[i].species}</td>
                <td>${pets[i].breed}</td>
                <td>${pets[i].age}</td>
                <td>${pets[i].gender}</td>
                <td><button onclick="petIndex = ${i}; reloadPetInfo();">Select</button></td>
            </tr>
        `;
    }
    petSelectorHtml += `</table>`;
    petSelectorDiv.innerHTML = petSelectorHtml;

    // load current appointment health check and stuff

    loadPetPastRecords();
}

function loadPetPastRecords() {
    console.log('Loading past records for pet: ', pets[petIndex].name);
    let petPastRecordsDiv = document.getElementById('pet-past-records');
    petPastRecordsDiv.innerHTML = `<p>Loading...</p>`;

    fetch(`/get_pet_appointments?pet_id=${pets[petIndex].pet_id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Response not OK');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.success) {
            // | View | Appointment             | Health Check                                 | Diagnosis            | Vaccine |
            // |      | Date | Service | Doctor | General Observation | Body Temp | Pulse Rate | Symptoms | Diagnosis |         |
                let pastRecordsHtml = `
                    <table style="border-collapse: collapse; background-color: #FFFFDD">
                        <tr>
                            <th rowspan="2"></th>
                            <th colspan="3">Appointment</th>
                            <th colspan="3">Health Check</th>
                            <th colspan="2">Diagnosis</th>
                            <th rowspan="2">Vaccine</th>
                        </tr>
                        <tr>
                            <th>Date</th>
                            <th>Service</th>
                            <th>Doctor</th>
                            <th>General Observation</th>
                            <th>Body Temp</th>
                            <th>Pulse Rate</th>
                            <th>Symptoms</th>
                            <th>Diagnosis</th>
                        </tr>
                `;

                for (let aid in data.appointments) {
                    let appointment = data.appointments[aid];
                    const appointmentDate = new Date(appointment['datetime']).toISOString().split('T')[0];

                    const fields = ['service', 'doctor', 'general_observation', 'body_temp', 'pulse_rate', 'symptoms', 'diagnosis', 'vaccine_name'];
                    fields.forEach(field => {
                        appointment[field] = appointment[field] || '<span style="color: #999999">N/A</span>';
                    });
                    
                    if (appointment['appointment_id'] == appointmentId) {
                        pastRecordsHtml += `<tr style="background-color: #DDFFFF">`;
                        pastRecordsHtml += `<td><strong>Current</strong></td>`;
                    } else {
                        pastRecordsHtml += `<tr">`;
                        pastRecordsHtml += `
                            <td><button onclick="window.location.href='/doctor-appointment?appointment_id=${appointment.appointment_id}&pet_id=${pets[petIndex].pet_id}'">
                                View</button></td>`;
                    }

                    pastRecordsHtml += `<td>${appointmentDate}</td>
                            <td>${appointment['service']}</td>
                            <td>${appointment['doctor']}</td>
                            <td>${appointment['general_observation']}</td>
                            <td>${appointment['body_temp']}</td>
                            <td>${appointment['pulse_rate']}</td>
                            <td>${appointment['symptoms']}</td>
                            <td>${appointment['diagnosis']}</td>
                            <td>${appointment['vaccine_name']}</td>
                        </tr>
                    `;
                }
                pastRecordsHtml += `</table>`;

                petPastRecordsDiv.innerHTML = pastRecordsHtml;
            
            } else {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching pet past records: ', error);
            petPastRecordsDiv.innerHTML = `<p style="color: red">Failed to load past records.<br>Error: ${error}</p>`;
        });
}