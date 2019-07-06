

window.addEventListener("load", function () {
  function sendData() {
    var XHR = new XMLHttpRequest();

    var forms = document.getElementsByClassName('kitchen-form');

    // Bind the FormData object and the form element
    var formData = new FormData(forms);
    formData.append('name', document.getElementById('name').value)
    formData.append('description', document.getElementById('description').value)
    formData.append('username', document.getElementById('username').value)
    formData.append('password', document.getElementById('password').value)
    formData.append('first_name', document.getElementById('first_name').value)
    formData.append('last_name', document.getElementById('last_name').value)
    formData.append('address', document.getElementById('address').value)
    formData.append('state', document.getElementById('state').value)
    formData.append('city', document.getElementById('state').value)
    formData.append('zipcode', document.getElementById('zipcode').value)
    formData.append('phone_number', document.getElementById('phone_number').value)
    formData.append('close_time', document.getElementById('close_time').value)
    formData.append('open_time', document.getElementById('open_time').value)

    // Define what happens on successful data submission
    XHR.addEventListener("load", function(event) {
      alert(event.target.responseText);
    });

    // Define what happens in case of error
    XHR.addEventListener("error", function(event) {
      alert('Oops! Something went wrong.');
    });

    // Set up our request
    XHR.open("POST", "http://127.0.0.1:5000/api/v1/kitchens/register", true);

    // The data sent is what the user provided in the form
    XHR.send(formData);
  }



// Fetch all the forms we want to apply custom Bootstrap validation styles to
var forms = document.getElementsByClassName('kitchen-form');

// Loop over them and prevent submission
var validation = Array.prototype.filter.call(forms, function(form) {

                form.addEventListener('submit', function(event) {
                    if (form.checkValidity() === false) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                    sendData();
                }, false);
            });

});