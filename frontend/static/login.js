function submitLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    fetch('/submit_login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        }),
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === 1) {
            document.getElementById('login-result').innerText = `Login Successful!`;
            window.location.href = "/"
        }
        else {
            document.getElementById('login-result').innerText = data.error
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function submitRegister() {
    const username = document.getElementById('r-username').value;
    const password = document.getElementById('r-password').value;
    const contact = document.getElementById('r-contact').value;
    const email = document.getElementById('r-email').value;
    
    fetch('/submit_register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password,
            contact: contact,
            email: email
        }),
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === 1) {
            document.getElementById('register-result').innerText = `Register Successful!`;
        }
        else {
            document.getElementById('register-result').innerText = data.error
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function randomUserLogin() {
    fetch('/random_user_login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === 1) {
            document.getElementById('login-result').innerText = `Login Successful!`;
            window.location.href = "/";
        }
        else {
            document.getElementById('login-result').innerText = data.error
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function randomDoctorLogin() {
    fetch('/random_doctor_login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === 1) {
            document.getElementById('login-result').innerText = `Login Successful!`;
            window.location.href = "/doctor-home";
        }
        else {
            document.getElementById('login-result').innerText = data.error
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Ensure functions are available globally
    window.submitLogin = submitLogin;
    window.submitRegister = submitRegister;
    window.randomUserLogin = randomUserLogin;
    window.randomDoctorLogin = randomDoctorLogin;
});