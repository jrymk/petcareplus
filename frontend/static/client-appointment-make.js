window.addEventListener("DOMContentLoaded", generateBranchOptions);

const appBranchSelect = document.getElementById('app-branch')
appBranchSelect?.addEventListener("change", generateDoctorOptions);
appBranchSelect?.addEventListener("change", generateServiceOptions);

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
