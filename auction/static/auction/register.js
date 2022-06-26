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

    //Show clinic fields
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
        termsButton.style.display = 'block';
    }
    //If nothing is selected hide fields
    else if (userTypeValue === "---------") {
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
        termsButton.style.display = 'block';
    }
}

$(document).ready(function () {
    //$('#submitButton').prop('disabled', false);
    if ($("#id_user_type :selected").text() !== "---------") {
        $('#termsButton').css("display", "block");
    }

    if ($('#agreementCheckBox').prop("checked") === true) {
        $('#submitButton').prop('disabled', false);
    }

    $("#id_user_type").change(function () {
        $('.alert-block').css("display", "none");
    });

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

    if ($('.alert-block').css("display") === "block") {
        userTypeChange();
    }

    // Show and hide image inputs
    clearAndHideImageTwo();
    clearAndHideImageThree();
    clearAndHideImageFour();

    $('#id_imageOne').change(function () {
        if ($(this).val() != '') {
            $('#div_id_imageTwo').show();
        } else {
            clearAndHideImageTwo();
            clearAndHideImageThree();
            clearAndHideImageFour();
        }
    })

    $('#id_imageTwo').change(function () {
        if ($(this).val() != '') {
            $('#div_id_imageThree').show();
        } else {
            clearAndHideImageThree();
            clearAndHideImageFour();
        }
    })

    $('#id_imageThree').change(function () {
        if ($(this).val() != '') {
            $('#div_id_imageFour').show();
        } else {
            clearAndHideImageFour();
        }
    })

    function clearAndHideImageTwo() {
        $('#id_imageTwo').val('');
        $('#div_id_imageTwo').hide();
    }

    function clearAndHideImageThree() {
        $('#id_imageThree').val('');
        $('#div_id_imageThree').hide();
    }
    function clearAndHideImageFour() {
        $('#id_imageFour').val('');
        $('#div_id_imageFour').hide();
    }

});