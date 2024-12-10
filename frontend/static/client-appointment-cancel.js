window.addEventListener("DOMContentLoaded", generateAppIdOptions);

function generateAppIdOptions(){
    // empty selectApp
    var selectApp = document.getElementById('app-id');
    selectApp.innerHTML = `<option disabled selected value> -- select appointment ID -- </option>`

    fetch('/get_user_pending_appointments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        var apps = data.apps;  // returns [[appointment_id, created_at, ...]]
        for(var i = 0; i < apps.length; i++) {  // iterates over appointment ids and add options
            var option = document.createElement("option");
            option.value = parseInt(apps[i][0]);
            option.text = `${apps[i][0]} (${apps[i][1]}, ${apps[i][4]})`
            selectApp.appendChild(option);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function cancelAppointment() {
    document.getElementById('app-cancel-result').innerText = `Processing...`;

    const appId = document.getElementById('app-id').value;
    fetch('/cancel_appointment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            appId: appId
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === 1) {
            document.getElementById('app-cancel-result').innerText = `Cancellation Successful!`;
            generateAppIdOptions();  // remove the cancelled appointment from options
        }
        else
            document.getElementById('app-cancel-result').innerText = data.error
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}