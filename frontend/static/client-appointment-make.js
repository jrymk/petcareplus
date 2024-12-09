window.addEventListener("DOMContentLoaded", setMinDate);
window.addEventListener("DOMContentLoaded", generatePetOptions);
window.addEventListener("DOMContentLoaded", generateBranchOptions);

const appBranchSelect = document.getElementById('app-branch')
appBranchSelect?.addEventListener("change", generateDoctorOptions);
appBranchSelect?.addEventListener("change", generateServiceOptions);


function setMinDate(){
    var tomorrowDate = new Date();
    const offset = tomorrowDate.getTimezoneOffset();
    tomorrowDate = new Date(tomorrowDate.getTime() - (offset*60*1000) + (24*3600*1000));

    const appDateSelect = document.getElementById('app-datetime');
    appDateSelect.min = tomorrowDate.toISOString().split('T')[0] + "T00:00";
}

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
        var selectPets = document.getElementById('app-pet-multipleselect');
        for(var i = 0; i < pets.length; i++) {  // iterates over branches and add options
            var checkboxLabel = document.createElement("label");
            var checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.value = parseInt(pets[i][0]);  // pet_id
            
            checkboxLabel.appendChild(checkbox);
            checkboxLabel.innerHTML += pets[i][1] + "  "  // pet name
            selectPets.appendChild(checkboxLabel);
        }

        // add event listeners to dynamically created inputs
        var selectPetsItems = selectPets.getElementsByTagName("input");
        for(var i = 0; i < selectPetsItems.length; i++)
            selectPetsItems[i].addEventListener("change", checkEnableDisablePetCheckbox);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function checkEnableDisablePetCheckbox(){
    var selectPets = document.getElementById('app-pet-multipleselect');
    var selectPetsItems = selectPets.getElementsByTagName("input");

    var cnt = 0;  // count of checked checkboxes
    for(var i = 0; i < selectPetsItems.length; i++)
        if(selectPetsItems[i].checked) cnt++;

    if(cnt < 3){
        for(var i = 0; i < selectPetsItems.length; i++)
            selectPetsItems[i].disabled = false;  // all checkboxes are activated
    }
    else{  // reached maximum limit of checkboxes (3)
        for(var i = 0; i < selectPetsItems.length; i++)
            if(!selectPetsItems[i].checked)  // all unchecked checkboxes are disabled
                selectPetsItems[i].disabled = true;
    }
}

function generateBranchOptions(){
    fetch('/get_branches', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        var branches = data.branches;  // returns [[branch_id, branch_name, ...]]
        var selectBranches = document.getElementById('app-branch');
        for(var i = 0; i < branches.length; i++) {  // iterates over branches and add options
            var option = document.createElement("option");
            option.value = parseInt(branches[i][0]);
            option.text = branches[i][1];
            selectBranches.appendChild(option);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function generateDoctorOptions(){
    document.getElementById("app-submit").disabled = true;  // temporarily disabling submit button

    const branch_id = document.getElementById('app-branch').value;
    fetch('/get_branch_doctors', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            branch_id: branch_id
        })
    })
    .then(response => response.json())
    .then(data => {
        var doctors = data.doctors;  // returns [[doctor_id, name, ...]]
        var selectDoctors = document.getElementById('app-doctor');

        selectDoctors.innerHTML = `
            <option disabled selected value> -- select doctor -- </option>
        `  // empty options
        for(var i = 0; i < doctors.length; i++) {
            var option = document.createElement("option");
            option.value = parseInt(doctors[i][0]);
            option.text = doctors[i][1];
            selectDoctors.appendChild(option);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function generateServiceOptions(){
    const branch_id = document.getElementById('app-branch').value;
    fetch('/get_branch_services', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            branch_id: branch_id
        })
    })
    .then(response => response.json())
    .then(data => {
        var services = data.services;  // returns [[service_id, name, ...]]
        var selectServices = document.getElementById('app-service');

        selectServices.innerHTML = `
            <option disabled selected value> -- select service -- </option>
        `  // empty options
        for(var i = 0; i < services.length; i++) {
            var option = document.createElement("option");
            option.value = parseInt(services[i][0]);
            option.text = services[i][1];
            selectServices.appendChild(option);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });

    document.getElementById("app-submit").disabled = false;  // re-activate submit button
}

function appendAppointment() {
    var appPets = [];
    var selectPets = document.getElementById('app-pet-multipleselect');
    var selectPetsItems = selectPets.getElementsByTagName("input");
    for(var i = 0; i < selectPetsItems.length; i++)
        if(selectPetsItems[i].checked)
            appPets.push(selectPetsItems[i].value)  // make a list of pets

    const appDatetime = document.getElementById('app-datetime').value;
    const appService = document.getElementById('app-service').value;
    const appBranch = document.getElementById('app-branch').value;
    const appDoctor = document.getElementById('app-doctor').value;

    fetch('/append_appointment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appDatetime: appDatetime,
            appService: appService,
            appBranch: appBranch,
            appDoctor: appDoctor,
            appPets: appPets
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === 1) 
            document.getElementById('app-append-result').innerText = `Appointment Successful!`;
        else
            document.getElementById('app-append-result').innerText = data.error
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}