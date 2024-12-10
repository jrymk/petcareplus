let readOnly = false;
let readOnlyDesc = "";
let appointmentId = 0;
let petIndex = 0;
let pets = [];
let vaccines = [];

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
                if (data.success) {
                    const appointment = data.appointment;

                    readOnly = appointment.status != 'P!'; // pending and is chosen doctor
                    
                    if (readOnly) {
                        // disable form buttons
                        document.getElementById('save-health-check').disabled = true;
                        document.getElementById('save-diagnosis').disabled = true;
                        document.getElementById('add-vaccine').disabled = true;
                        document.getElementById('add-prescription').disabled = true;
                    }
                    
                    if (appointment.status == 'P!') {
                        readOnlyDesc = "This appointment is editable. You should not be seeing this message.";
                    }
                    else if (appointment.status[0] == 'C') {
                        readOnlyDesc = "This appointment is cancelled and not editable.";
                    }
                    else if (appointment.status[0] == 'O') {
                        readOnlyDesc = "This appointment is archived and not editable.";
                    }
                    else if (appointment.status[0] == 'P') {
                        readOnlyDesc = "This appointment is only editable by the chosen doctor.";
                    } else {
                        readOnlyDesc = "This appointment is not editable.";
                    }

                    const appointmentStatusDiv = document.getElementById('appointment-status');
                    const appointmentStatusText = document.getElementById('appointment-status-text');
                    if (readOnly) {
                        appointmentStatusText.innerHTML = readOnlyDesc;
                        appointmentStatusDiv.style.backgroundColor = '#FF0000';
                        appointmentStatusDiv.style.color = '#FFFFFF';
                    } else {
                        appointmentStatusText.innerHTML = "Appointment is active";
                        document.getElementById('complete-and-archive-button').style.display = 'inline-block';
                        document.getElementById('cancel-button').style.display = 'inline-block';
                    }

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
    
    // load vaccines
    fetch('/get_vaccine_names')
        .then(response => {
            if (!response.ok) {
                throw new Error('Response not OK');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                vaccines = data.vaccines;
            } else {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching vaccines: ', error);
        });
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
    fetch(`/get_pet_record?pet_id=${pets[petIndex].pet_id}&appointment_id=${appointmentId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Response not OK');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.success) {
                if (data.health_check != null) {
                    document.getElementById('general-observation').value = data.health_check.general_observation || '';
                    document.getElementById('body-temp').value = data.health_check.body_temp || '';
                    document.getElementById('pulse-rate').value = data.health_check.pulse_rate || '';
                    document.getElementById('notes').value = data.health_check.notes || '';
                }
                if (data.diagnosis != null) {
                    document.getElementById('symptoms').value = data.diagnosis.symptoms || '';
                    document.getElementById('diagnosis').value = data.diagnosis.diagnosis || '';
                    document.getElementById('treatment-plan').value = data.diagnosis.treatment_plan || '';
                    document.getElementById('follow-up').value = data.diagnosis.follow_up || '';
                }

                const vaccineListDiv = document.getElementById('vaccine-list');
                let vaccineListHtml = `
                    <table>
                        <tr>
                            <th>Vaccine</th>
                            <th>Span</th>
                            <th>Due Date</th>
                            <th>Manage</th>
                        </tr>`;
                if (data.vaccination == null || Object.keys(data.vaccination).length == 0) {
                    vaccineListHtml += `
                        <tr>
                            <td colspan="4" style="text-align: center; font-style: italic;">No vaccines</td>
                        </tr>`;
                }
                else {
                    for (let vid in data.vaccination) {
                        let vaccine = data.vaccination[vid];
                        let spanText =
                            (vaccine.due_span >= 12 ? Math.floor(vaccine.due_span / 12) + '年' : '') +
                            (vaccine.due_span % 12 == 0 ? '' : vaccine.due_span % 12 + '個月');
                        vaccineListHtml += `
                            <tr>
                                <td>${vaccine.vaccine_name}</td>
                                <td>${spanText}</td>
                                <td>${new Date(vaccine.due_date).toISOString().split('T')[0]}</td>
                                <td><button onclick="removeVaccine('${vaccine.vaccine_name}');">Delete</button></td>
                            </tr>
                        `;
                    }
                }
                vaccineListHtml += `</table>`;
                vaccineListDiv.innerHTML = vaccineListHtml;

                const prescriptionListDiv = document.getElementById('prescription-list');
                let prescriptionListHtml = `
                    <table>
                        <tr>
                            <th>Medication</th>
                            <th>Dosage</th>
                            <th>Frequency</th>
                            <th>Duration</th>
                            <th>Notes</th>
                            <th>Manage</th>
                        </tr>`;
                if (data.prescriptions == null || Object.keys(data.prescriptions).length == 0) {
                    prescriptionListHtml += `
                        <tr>
                            <td colspan="6" style="text-align: center; font-style: italic;">No prescriptions</td>
                        </tr>`;
                }
                else {
                    for (let pid in data.prescriptions) {
                        let prescription = data.prescriptions[pid];
                        prescriptionListHtml += `
                            <tr>
                                <td>${prescription.medicine_name}</td>
                                <td>${prescription.dosage}</td>
                                <td>${prescription.frequency}</td>
                                <td>${prescription.duration}</td>
                                <td>${prescription.notes}</td>
                                <td>
                                    <button onclick="removePrescription('${prescription.medicine_name}');">Delete</button>
                                </td>
                            </tr>
                        `;
                    }
                }
                prescriptionListHtml += `</table>`;
                prescriptionListDiv.innerHTML = prescriptionListHtml;

            } else {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching pet record: ', error);
        });
    
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

function saveHealthCheck() {
    if (readOnly) {
        alert(readOnlyDesc);
        return;
    }

    let generalObservation = document.getElementById('general-observation').value;
    let bodyTemp = document.getElementById('body-temp').value;
    let pulseRate = document.getElementById('pulse-rate').value;
    let notes = document.getElementById('notes').value;

    fetch('/update-health-check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appointment_id: appointmentId,
            pet_id: pets[petIndex].pet_id,
            general_observation: generalObservation,
            body_temp: bodyTemp,
            pulse_rate: pulseRate,
            notes: notes
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response not OK');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Health check saved successfully');
            loadPetPastRecords();
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Error saving health check: ', error);
        alert('Failed to save health check.\nError: ' + error);
    });

    reloadPetInfo();
}

function saveDiagnosis() {
    if (readOnly) {
        alert(readOnlyDesc);
        return;
    }

    let symptoms = document.getElementById('symptoms').value;
    let diagnosis = document.getElementById('diagnosis').value;
    let treatmentPlan = document.getElementById('treatment-plan').value;
    let followUp = document.getElementById('follow-up').value;

    fetch('/update-diagnosis', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appointment_id: appointmentId,
            pet_id: pets[petIndex].pet_id,
            symptoms: symptoms,
            diagnosis: diagnosis,
            treatment_plan: treatmentPlan,
            follow_up: followUp
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response not OK');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Diagnosis saved successfully');
            loadPetPastRecords();
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Error saving diagnosis: ', error);
        alert('Failed to save diagnosis.\nError: ' + error);
    });

    reloadPetInfo();
}

function addVaccine() {
    if (readOnly) {
        alert(readOnlyDesc);
        return;
    }

    let vaccineName = document.getElementById('vaccine-name').value;

    fetch('/insert-vaccination', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appointment_id: appointmentId,
            pet_id: pets[petIndex].pet_id,
            vaccine_name: vaccineName,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response not OK');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Vaccine added successfully');
            loadPetPastRecords();
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Error adding vaccine: ', error);
        alert('Failed to add vaccine.\nError: ' + error);
    });
    
    reloadPetInfo();
}


function removeVaccine(vaccineName) {
    if (readOnly) {
        alert(readOnlyDesc);
        return;
    }

    if (!confirm('Are you sure you want to remove this vaccine?')) {
        return;
    }
    fetch('/delete-vaccination', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appointment_id: appointmentId,
            pet_id: pets[petIndex].pet_id,
            vaccine_name: vaccineName,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response not OK');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Vaccine removed successfully');
            loadPetPastRecords();
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Error removing vaccine: ', error);
        alert('Failed to remove vaccine.\nError: ' + error);
    });

    reloadPetInfo();
}

function addPrescription() {
    if (readOnly) {
        alert(readOnlyDesc);
        return;
    }

    let medicineName = document.getElementById('prescription-name').value;
    let dosage = document.getElementById('prescription-dosage').value;
    let frequency = document.getElementById('prescription-frequency').value;
    let duration = document.getElementById('prescription-duration').value;
    let notes = document.getElementById('prescription-notes').value;

    fetch('/insert-prescription', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appointment_id: appointmentId,
            pet_id: pets[petIndex].pet_id,
            medicine_name: medicineName,
            dosage: dosage,
            frequency: frequency,
            duration: duration,
            notes: notes
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Response not OK');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log('Prescription added successfully');
                loadPetPastRecords();
            } else {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('Error adding prescription: ', error);
            alert('Failed to add prescription.\nError: ' + error);
        });

    reloadPetInfo();
}


function removePrescription(medicineName) {
    if (readOnly) {
        alert(readOnlyDesc);
        return;
    }

    if (!confirm(`Are you sure you want to remove the prescription for ${medicineName}?`)) {
        return;
    }
    fetch('/delete-prescription', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appointment_id: appointmentId,
            pet_id: pets[petIndex].pet_id,
            medicine_name: medicineName,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response not OK');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Prescription removed successfully');
            loadPetPastRecords();
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Error removing prescription: ', error);
        alert('Failed to remove prescription.\nError: ' + error);
    });

    reloadPetInfo();
}

function completeAndArchive() {
    if (readOnly) {
        alert(readOnlyDesc);
        return;
    }

    if (!confirm('Are you sure you want to complete and archive this appointment?\nThe appointment will no longer be editable.\nThis cannot be undone!')) {
        return;
    }

    fetch('/archive', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appointment_id: appointmentId,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response not OK');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Appointment completed and archived successfully');
            alert('Appointment completed and archived successfully');
            window.location.reload();
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Error completing and archiving appointment: ', error);
        alert('Failed to complete and archive appointment.\nError: ' + error);
    });
}

function cancelAppointment() {
    if (readOnly) {
        alert(readOnlyDesc);
        return;
    }

    if (!confirm('Are you sure you want to cancel this appointment?\nThe appointment will no longer be editable.\nThis cannot be undone!')) {
        return;
    }

    fetch('/cancel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appointment_id: appointmentId,
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response not OK');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Appointment cancelled successfully');
            alert('Appointment cancelled successfully');
            window.location.reload();
        } else {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Error cancelling appointment: ', error);
        alert('Failed to cancel appointment.\nError: ' + error);
    });
}

function showVaccineCandidates() {
    let filter = document.getElementById('vaccine-name').value;
    let vaccineCandidatesDiv = document.getElementById('vaccine-candidates');
    let vaccineCandidatesHtml = '';

    vaccineCandidatesDiv.style.display = 'block';

    document.getElementById('add-vaccine').disabled = !vaccines.includes(document.getElementById('vaccine-name').value);

    // let filteredVaccines = vaccines.filter(vaccine => vaccine.includes(filter));
    let regex = new RegExp(filter.split('').join('.*'), 'i');
    let filteredVaccines = vaccines.filter(vaccine => regex.test(vaccine));
    if (filteredVaccines.length > 0) {
        vaccineCandidatesHtml = '<ul>';
        filteredVaccines.forEach(vaccine => {
            vaccineCandidatesHtml += `<span onclick="document.getElementById('vaccine-name').value='${vaccine}'; hideVaccineCandidates();">${vaccine}</span><br>`;
        });
    } else {
        vaccineCandidatesHtml = '<p>No matching vaccines found.</p>';
    }
    vaccineCandidatesDiv.innerHTML = vaccineCandidatesHtml;
}

function hideVaccineCandidates() {
    if (vaccines.includes(document.getElementById('vaccine-name').value)) {
        document.getElementById('vaccine-candidates').style.display = 'none';
        document.getElementById('add-vaccine').disabled = false;
    }
}