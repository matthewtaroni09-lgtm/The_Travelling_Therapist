document.getElementById("id_user_type").addEventListener("change", userTypeChange);
// document.getElementById("tandcmodal").addEventListener("change", agreementChecked);
const combinedFields = document.getElementsByClassName('combinedFields');
const clinicFields = document.getElementsByClassName('clinicField');
const therapistFields = document.getElementsByClassName('therapistField');
const termsButton = document.getElementById('termsButton');
const submitButton = document.getElementById('submitButton');

for (const fields of combinedFields) {
    fields.style.display = 'none';
}
for (const fields of clinicFields) {
    fields.style.display = 'none';
}
for (const fields of therapistFields) {
    fields.style.display = 'none';
}
termsButton.style.display = 'none';

function userTypeChange() {
    let userType = document.getElementById("id_user_type");
    let userTypeValue = userType.options[userType.selectedIndex].text

    if (userTypeValue.split(" ")[1] === "Clinic") {
        for (const fields of combinedFields) {
            fields.style.display = 'block';
        }
        for (const fields of clinicFields) {
            fields.style.display = 'block';
        }
        for (const fields of therapistFields) {
            fields.style.display = 'none';
        }
    }
    else {
        for (const fields of combinedFields) {
            fields.style.display = 'block';
        }
        for (const fields of clinicFields) {
            fields.style.display = 'none';
        }
        for (const fields of therapistFields) {
            fields.style.display = 'block';
        }
    }
    termsButton.style.display = 'block';
}

$(document).ready(function () {
    //$('#submitButton').prop('disabled', false);
    $('#tandcModal').on('hidden.bs.modal', function () {
        $('#agreementCheckBox').css("display", "none");
        $('#agreementCheckBoxLabel').css("display", "none");
    })

    $('#termsButton').click(function () {
        $('#agreementCheckBox').css("display", "block");
        $('#agreementCheckBoxLabel').css("display", "block");
    });

    $('#agreementCheckBox').click(function () {
        if ($('#agreementCheckBox').prop("checked") === true) {
            $('#submitButton').prop('disabled', false);
        }
        else {
            $('#submitButton').prop('disabled', true);
        }
    });
});