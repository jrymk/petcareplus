const appStatusSelect = document.getElementById('app-status')
appStatusSelect.addEventListener("change", getUserAppointments);


function getUserAppointments() {
    const status = document.getElementById('app-status').value;
    fetch('/get_user_appointments', {
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

/*
function appendPet() {
    const petName = document.getElementById('pet-name').value;
    const petSpecies = document.getElementById('pet-species').value;
    const petBreed = document.getElementById('pet-breed').value;
    const petBdate = document.getElementById('pet-bdate').value;
    const petGender = document.getElementById('pet-gender').value;

    fetch('/append_pet', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            petName: petName,
            petSpecies: petSpecies,
            petBreed: petBreed,
            petBdate: petBdate,
            petGender: petGender
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === 1) {
            document.getElementById('pet-append-result').innerText = `Append Successful!`;
            getUserPets();
        }
        else {
            document.getElementById('pet-append-result').innerText = data.error
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}*/