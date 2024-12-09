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