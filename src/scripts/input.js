const parameterInputs = document.getElementById('parameterInputs');
const sendRequestButton = document.getElementById('sendRequestButton');
const responseOutput = document.getElementById("response");
let currentService = '';
let currentServer = '';
let backendUrl = "http://localhost:5000/api/service";
let keyInput, valueInput;

const updateParameters = (service) => {
    currentService = service;
    let html = '';
    switch(service) {
        case 'ping':
        html = '<input type="text" class="form-control" placeholder="No parameters needed" disabled>';
        break;
        case 'get':
        case 'strln':
        case 'del':
        html = '<input type="text" class="form-control" placeholder="Key" id="keyInput">';
        break;
        case 'set':
        case 'append':
        html = `
            <input type="text" class="form-control" placeholder="Key" id="keyInput">
            <input type="text" class="form-control" placeholder="Value" id="valueInput">
        `;
        break;
        default:
        break;
    }
    parameterInputs.innerHTML = html;
    validateForm();
    parameterInputs.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', validateForm);
    });
}

const validateForm = () => {
    const inputs = parameterInputs.querySelectorAll('input');
    const allFilled = Array.from(inputs).every(input => input.value.trim() !== '');
    if (currentServer && (currentService === 'ping' || (currentService && allFilled))) {
        sendRequestButton.disabled = false;
    } else {
        sendRequestButton.disabled = true;
    }
    console.log(currentService, currentServer);
}

sendRequestButton.addEventListener('click', async() => {
    console.log("Sending request", currentService, "to", currentServer);
    switch (currentService){
        case "ping":
            try {
                const response = await fetch(backendUrl, {
                    method: 'POST', 
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({'service': 'ping', 'params': ''})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const data = await response.json();
                console.log("API response:", data);
                responseOutput.innerHTML = "Response: " + JSON.stringify(data);
            } catch (error) {
                console.error("Error sending request:", error);
            }
            break;
        case "get":
            keyInput = document.getElementById("keyInput").value;
            try {
                const response = await fetch(backendUrl, {
                    method: 'POST', 
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({'service': 'get', 'params': keyInput})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const data = await response.json();
                console.log("API response:", data);
                responseOutput.innerHTML = "Response: " + JSON.stringify(data);
            } catch (error) {
                console.error("Error sending request:", error);
            }
            break;
        case "set":
            keyInput = document.getElementById("keyInput").value;
            valueInput = document.getElementById("valueInput").value;
            try {
                const response = await fetch(backendUrl, {
                    method: 'POST', 
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({'service': 'set', 'params': {'key': keyInput, 'value':valueInput}})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const data = await response.json();
                console.log("API response:", data);
                responseOutput.innerHTML = "Response: " + JSON.stringify(data);
            } catch (error) {
                console.error("Error sending request:", error);
            }
            break;
        case "strln":
            keyInput = document.getElementById("keyInput").value;
            try {
                const response = await fetch(backendUrl, {
                    method: 'POST', 
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({'service': 'strln', 'params': {'key': keyInput}})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const data = await response.json();
                console.log("API response:", data);
                responseOutput.innerHTML = "Response: " + JSON.stringify(data);
            } catch (error) {
                console.error("Error sending request:", error);
            }
            break;
        case "del":
            keyInput = document.getElementById("keyInput").value;
            try {
                const response = await fetch(backendUrl, {
                    method: 'POST', 
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({'service': 'delete', 'params': {'key': keyInput}})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const data = await response.json();
                console.log("API response:", data);
                responseOutput.innerHTML = "Response: " + JSON.stringify(data);
            } catch (error) {
                console.error("Error sending request:", error);
            }
            break;
        case "append":
            keyInput = document.getElementById("keyInput").value;
            valueInput = document.getElementById("valueInput").value;
            try {
                const response = await fetch(backendUrl, {
                    method: 'POST', 
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({'service': 'append', 'params': {'key': keyInput, 'value':valueInput}})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const data = await response.json();
                console.log("API response:", data);
                responseOutput.innerHTML = "Response: " + JSON.stringify(data);
            } catch (error) {
                console.error("Error sending request:", error);
            }
            break;
    }
});

document.querySelectorAll('#dropdownServiceButton + .dropdown-menu .dropdown-item').forEach(item => {
    item.addEventListener('click', function() {
        const service = this.getAttribute('data-service');
        document.getElementById('dropdownServiceButton').textContent = this.textContent;
        updateParameters(service);
    });
});

document.querySelectorAll('#dropdownServerButton + .dropdown-menu .dropdown-item').forEach(item => {
    item.addEventListener('click', function() {
        currentServer = this.getAttribute('data-server');
        document.getElementById('dropdownServerButton').textContent = this.textContent;
        validateForm();
    });
});