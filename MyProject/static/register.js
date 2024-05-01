document.getElementById('registration-form').addEventListener('submit', function(event) {
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirm-password').value;
    if (password !== confirmPassword) {
        alert("The passwords do not match!");
        event.preventDefault(); // Prevent form submission
    }
});