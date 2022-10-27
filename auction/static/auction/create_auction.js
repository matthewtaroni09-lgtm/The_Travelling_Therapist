$(document).ready(function () {
    $('.alert.alert-block.alert-danger').hide();
    $('[id^=id_demogrpahic_auction-]').each(function (i, el) {
        if ($(this).is('select')) {
            $(this).attr("disabled", true);
            $(this).val(parseInt($(this).attr('id').match(/\d/)[0]) + 1);
        }
        else if ($(this).is('input') && $(this).attr('type') === "hidden" && $(this).val().indexOf('-') >= 0) {
            $(this).val('');
        }
    });

    $('[id^=id_practice_area_auction-]').each(function (i, el) {
        if ($(this).is('select')) {
            $(this).attr("disabled", true);
        }
        else if ($(this).is('input') && $(this).attr('type') === "hidden" && $(this).val().indexOf('-') >= 0) {
            $(this).val('');
        }
    });

    //Clinic is not a selectable option. If the user selects clinic it will be picked automatically
    let clinicVal = '';
    $('#id_type option').each(function () {
        if ($(this).text() == 'Clinic') {
            clinicVal = $(this).val();
        }
    });
    $("#id_type option[value='" + clinicVal + "']").remove();
});

$('#id_type').change(function () {
    $("#optionsMessage").hide();
});
$('#id_placementStart').change(function () {
    getDateDiff();
});
$('#id_placementEnd').change(function () {
    getDateDiff();
});
$('.clearButton').click(function () {
    $(this).parent().find('input[type=time]')[0].value = '';
    $(this).parent().find('input[type=time]')[1].value = '';
});
$("#submitButton").click(function () {
    let errorList = '';

    if ($("#id_type").val() === "0") {
        errorList += "<li>Please select an auction type.</li>";
    }

    let placementStart = new Date($("#id_placementStart").val());
    let placementEnd = new Date($("#id_placementEnd").val());

    let reservePrice = '';
    if ($("#id_reservePrice").val() !== '') {
        reservePrice = parseFloat($("#id_reservePrice").val());
    }

    let mondayStart = '';
    let mondayEnd = '';
    let tuesdayStart = '';
    let tuesdayEnd = '';
    let wednesdayStart = '';
    let wednesdayEnd = '';
    let thursdayStart = '';
    let thursdayEnd = '';
    let fridayStart = '';
    let fridayEnd = '';
    let saturdayStart = '';
    let saturdayEnd = '';
    let sundayStart = '';
    let sundayEnd = '';

    //JS has not Time object so use the Date object with a dummy date
    if ($("#id_mondayStart").val() !== '') {
        mondayStart = new Date('1970-01-01T' + $("#id_mondayStart").val() + 'Z');
    }
    if ($("#id_mondayEnd").val() !== '') {
        mondayEnd = new Date('1970-01-01T' + $("#id_mondayEnd").val() + 'Z');
    }

    if ($("#id_tuesdayStart").val() !== '') {
        tuesdayStart = new Date('1970-01-01T' + $("#id_tuesdayStart").val() + 'Z');
    }
    if ($("#id_tuesdayEnd").val() !== '') {
        tuesdayEnd = new Date('1970-01-01T' + $("#id_tuesdayEnd").val() + 'Z');
    }

    if ($("#id_wednesdayStart").val() !== '') {
        wednesdayStart = new Date('1970-01-01T' + $("#id_wednesdayStart").val() + 'Z');
    }
    if ($("#id_wednesdayEnd").val() !== '') {
        wednesdayEnd = new Date('1970-01-01T' + $("#id_wednesdayEnd").val() + 'Z');
    }

    if ($("#id_thrusdayStart").val() !== '') {
        thursdayStart = new Date('1970-01-01T' + $("#id_thrusdayStart").val() + 'Z');
    }
    if ($("#id_thrusdayEnd").val() !== '') {
        thursdayEnd = new Date('1970-01-01T' + $("#id_thrusdayEnd").val() + 'Z');
    }

    if ($("#id_fridayStart").val() !== '') {
        fridayStart = new Date('1970-01-01T' + $("#id_fridayStart").val() + 'Z');
    }
    if ($("#id_fridayEnd").val() !== '') {
        fridayEnd = new Date('1970-01-01T' + $("#id_fridayEnd").val() + 'Z');
    }

    if ($("#id_saturdayStart").val() !== '') {
        saturdayStart = new Date('1970-01-01T' + $("#id_saturdayStart").val() + 'Z');
    }
    if ($("#id_saturdayEnd").val() !== '') {
        saturdayEnd = new Date('1970-01-01T' + $("#id_saturdayEnd").val() + 'Z');
    }

    if ($("#id_sundayStart").val() !== '') {
        sundayStart = new Date('1970-01-01T' + $("#id_sundayStart").val() + 'Z');
    }
    if ($("#id_sundayEnd").val() !== '') {
        sundayEnd = new Date('1970-01-01T' + $("#id_sundayEnd").val() + 'Z');
    }

    let noneCount = 0

    let demographicTotal = 0;
    let practiceTotal = 0;
    let demographicCategory = '';
    let practiceCategory = '';

    //Validate Start/End date
    var now = new Date();
    let oneYear = new Date(now);
    oneYear.setDate(now.getDate() + 365)
    if (placementStart === NaN) {
        errorList += '<li>Please enter a valid Therapist Start Date.</li>';
    }
    if (placementEnd === NaN) {
        errorList += '<li>Please enter a valid Therapist End Date.</li>';
    }
    if (placementEnd < placementStart) {
        errorList += '<li>The Therapist End Date must be after the Therapist Start Date.</li>';
    }
    if (placementStart > oneYear) {
        errorList += '<li>Placements must start within the next 12 months.</li>';
    }
    if (days_between(placementStart, placementEnd) > 730) {
        errorList += '<li>Placements must be less than two years.</li>';
    }

    //Validate Reserve price
    if (reservePrice !== "") {
        if (reservePrice <= 0) {
            errorList += "<li>Reserve price cannot be 0 or less. If no reserve price is desired leave the field blank.</li>";
        }
    }
    if (reservePrice !== "") {
        if (reservePrice > 25000) {
            errorList += "<li>Reserve price must be less than $25,000.</li>";
        }
    }

    //Validate Therapist Scheudle
    let mondayVal = check_times(mondayStart, mondayEnd, 'Monday');
    let tuesdayVal = check_times(tuesdayStart, tuesdayEnd, 'Tuesday');
    let wednesdayVal = check_times(wednesdayStart, wednesdayEnd, 'Wednesday');
    let thursdayVal = check_times(thursdayStart, thursdayEnd, 'Thursday');
    let fridayVal = check_times(fridayStart, fridayEnd, 'Friday');
    let saturdayVal = check_times(saturdayStart, saturdayEnd, 'Saturday');
    let sundayVal = check_times(sundayStart, sundayEnd, 'Sunday');

    if (mondayVal === 'None') {
        noneCount = noneCount + 1
    }
    else if (mondayVal != '' && mondayVal != 'None') {
        errorList += mondayVal;
    }

    if (tuesdayVal === 'None') {
        noneCount = noneCount + 1
    }
    else if (tuesdayVal != '' && tuesdayVal != 'None') {
        errorList += tuesdayVal;
    }

    if (wednesdayVal === 'None') {
        noneCount = noneCount + 1
    }
    else if (wednesdayVal != '' && wednesdayVal != 'None') {
        errorList += wednesdayVal;
    }

    if (thursdayVal === 'None') {
        noneCount = noneCount + 1
    }
    else if (thursdayVal != '' && thursdayVal != 'None') {
        errorList += thursdayVal;
    }

    if (fridayVal === 'None') {
        noneCount = noneCount + 1
    }
    else if (fridayVal != '' && fridayVal != 'None') {
        errorList += fridayVal;
    }

    if (saturdayVal === 'None') {
        noneCount = noneCount + 1
    }
    else if (saturdayVal != '' && saturdayVal != 'None') {
        errorList += saturdayVal;
    }

    if (sundayVal === 'None') {
        noneCount = noneCount + 1
    }
    else if (sundayVal != '' && sundayVal != 'None') {
        errorList += sundayVal;
    }

    //Validate Demographics
    $('[id^=id_demogrpahic_auction-]').each(function (i, el) {
        if ($(this).is('select')) {
            demographicCategory = $(this).find(":selected").text();
        }
        if ($(this).attr('type') === 'number') {
            if ($(this).val() === '') {
                errorList += '<li>Please enter a value for ' + demographicCategory + '.</li>';
            }
            else if (parseInt($(this).val()) > 100) {
                errorList += '<li>' + demographicCategory + ' must be less than 100%.</li>';
            }
            demographicTotal += parseInt($(this).val());
        }
    });
    if (demographicTotal !== 100) {
        errorList += '<li>Demographic percentages must add up to 100%.</li>';
    }

    //Validate Areas of Practice
    $('[id^=id_practice_area_auction-]').each(function (i, el) {
        if ($(this).is('select')) {
            practiceCategory = $(this).find(":selected").text();
        }
        if ($(this).attr('type') === 'number') {
            if ($(this).val() === '') {
                errorList += '<li>Please enter a value for ' + practiceCategory + '.</li>';
            }
            else if (parseInt($(this).val()) > 100) {
                errorList += '<li>' + practiceCategory + ' must be less than 100%.</li>';
            }
            practiceTotal += parseInt($(this).val());
        }
    });
    if (practiceTotal !== 100) {
        errorList += '<li>Practice area percentages must add up to 100%.</li>';
    }
    console.log(practiceTotal);
    console.log(errorList);

    if (errorList !== '') {
        $('.alert.alert-block.alert-danger').show();
        $('#errorList').html(errorList);
        window.scrollTo(0, 0);
        return false;
    }
    //Django cannot get the values from disabled fields so re-enabled them on submit
    $("form :disabled").removeAttr('disabled');
});

function getDateDiff() {
    let start = "";
    let end = "";
    let startDate = "";
    let endDate = "";
    if ($('#id_placementStart')[0].value != "") {
        start = $('#id_placementStart')[0].value.split("-");
        startDate = new Date(start[0], start[1] - 1, start[2]);
    }

    if ($('#id_placementEnd')[0].value != "") {
        end = $('#id_placementEnd')[0].value.split("-");
        endDate = new Date(end[0], end[1] - 1, end[2]);
    }

    let dateDiff = days_between(startDate, endDate);
    if (dateDiff < 30) {
        $("#id_payFrequency option[value='3']").remove();
    }
    else {
        let monthlyPresent = false;
        $("#id_payFrequency > option").each(function () {
            if (this.text == "Monthly") {
                monthlyPresent = true;
            }
        });
        if (!monthlyPresent) {
            $('#id_payFrequency').append($('<option>', {
                value: 3,
                text: "Monthly"
            }));
        }
    }
}

function check_times(start_time, end_time, day) {
    if ((start_time === '' && end_time !== '') || (start_time !== '' && end_time === '')) {
        return "<li>Please ensure that the start and end times are completed for " + day + ". If this is not a working day please remove both start and end times.</li>";
    }
    else if (start_time !== '' && end_time !== '') {
        if (start_time >= end_time) {
            return "<li>" + day + "'s start time is after the end time.</li>";
        }
        else {
            return '';
        }
    }
    else if (start_time === '' && end_time === '') {
        return 'None';
    }
    else {
        return ''
    }
}

function days_between(date1, date2) {
    // The number of milliseconds in one day
    const ONE_DAY = 1000 * 60 * 60 * 24;

    // Calculate the difference in milliseconds
    const differenceMs = Math.abs(date1 - date2);

    // Convert back to days and return
    return Math.round(differenceMs / ONE_DAY);

}