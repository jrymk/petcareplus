window.addEventListener("DOMContentLoaded", generatePetOptions);

const visitServiceSelect = document.getElementById('visit-service');
visitServiceSelect?.addEventListener("change", getVisitRecords);
const visitPetSelect = document.getElementById('visit-pet');
visitPetSelect?.addEventListener("change", getVisitRecords);


function generatePetOptions(){
    fetch('/get_user_pets', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        var pets = data.pets;
        var selectPets = document.getElementById('visit-pet');
        for(var i = 0; i < pets.length; i++) {  // iterates over branches and add options
            var option = document.createElement("option");
            option.value = parseInt(pets[i][0]);
            option.text = pets[i][1];
            selectPets.appendChild(option);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function getVisitRecords(){
    var visitRecordTable = document.getElementById("visit-record-table");
    if((!visitServiceSelect.value) || (!visitPetSelect.value)) return;

    fetch('/user_get_visit_records_table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            serviceType: visitServiceSelect.value,
            petId: visitPetSelect.value
        })
    })
    .then(response => response.json())
    .then(data => {
        visitRecordTable.innerHTML = data.tableHTML;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}