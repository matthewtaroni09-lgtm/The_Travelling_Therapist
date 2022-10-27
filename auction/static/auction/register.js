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

function userTypeChange(userType) {
    // let userType = document.getElementById("id_user_type");
    // let userTypeValue = userType.options[userType.selectedIndex].text

    //Show clinic fields
    if (userType === "Clinic") {
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
    else if (userType === "---------") {
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
    let clinicVal = '';
    $('#id_user_type option').each(function () {
        if ($(this).text() == 'Clinic') {
            clinicVal = $(this).val();
        }
    });

    $("#clinicButton").click(function () {
        userTypeChange("Clinic");
        $("#clinicButton").css("background-color", "#0AEAA9");
        $("#therapistButton").css("background-color", "#FFFFFF");
        $('#id_user_type').append($('<option>', {
            value: clinicVal,
            text: 'Clinic'
        }));
        $('#id_user_type').val(clinicVal);
    });
    $("#therapistButton").click(function () {
        userTypeChange("Therapist");
        $("#clinicButton").css("background-color", "#FFFFFF");
        $("#therapistButton").css("background-color", "#0AEAA9");
        //Clinic is not a selectable option. If the user selects clinic it will be picked automatically
        $("#id_user_type option[value='" + clinicVal + "']").remove();
    });

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

    if ($('#error_1_id_imageOne').css("display") === "block") {
        userTypeChange();
    }
    if ($('#error_1_id_imageTwo').css("display") === "block") {
        userTypeChange();
    }
    if ($('#error_1_id_imageThree').css("display") === "block") {
        userTypeChange();
    }
    if ($('#error_1_id_imageFour').css("display") === "block") {
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