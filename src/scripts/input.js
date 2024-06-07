
const parameterInputs = document.getElementById('parameterInputs');
const sendRequestButton = document.getElementById('sendRequestButton');
let currentService = '';
let currentServer = '';

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
        html = '<input type="text" class="form-control" placeholder="Key">';
        break;
        case 'set':
        case 'append':
        html = `
            <input type="text" class="form-control" placeholder="Key">
            <input type="text" class="form-control" placeholder="Value">
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

sendRequestButton.addEventListener('click', () => {
    console.log("Sending request", currentService, "to", currentServer);
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