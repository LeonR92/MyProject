document.getElementById("registration-form").addEventListener("submit",(function(e){document.getElementById("password").value!==document.getElementById("confirm-password").value&&(alert("The passwords do not match!"),e.preventDefault())}));
