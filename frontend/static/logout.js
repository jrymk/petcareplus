function logout() {
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if(data.success === 1) {
            window.location.href = "/login"
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}