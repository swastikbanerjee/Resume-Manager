document.getElementById('resumeForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var formData = new FormData(this);
    var jsonData = {};
    formData.forEach(function(value, key) {
        jsonData[key] = value;
    });

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        var responseMessage = document.getElementById('responseMessage');
        responseMessage.style.display = 'block';
        responseMessage.textContent = data.message;
    })
    .catch(error => console.error('Error:', error));
});
