const currencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

$(document).ready(function () {
    $('.alert.alert-block.alert-danger').hide();
    // $('.feeSplitFields').hide();
    greyOutFields(true);
    // Prevent pressing enter from submitting the form
    $(document).keypress(
        function (event) {
            if (event.which == '13') {
                event.preventDefault();
            }
        });

    $('#id_paymentType').change(function () {
        if ($('#id_paymentType').find(":selected").text() === 'Fee Split') {
            $('.feeSplitFields').show();
            $("label[for='id_reservePrice']").text('Reserve Split');
        }
        else {
            $('.feeSplitFields').hide();
            $("label[for='id_reservePrice']").text('Reserve Price');
        }
    });

    $('#id_treatmentCost, #id_treatmentMin, #id_assessmentCost, #id_assessmentMin').change(function () {
        // If a negative number is entered blank out that input
        if ($(this).val() < 0) {
            $(this).val('');
        }

        let treatmentCost = $('#id_treatmentCost').val();
        let treatmentMin = $('#id_treatmentMin').val();
        let assessmentCost = $('#id_assessmentCost').val();
        let assessmentMin = $('#id_assessmentMin').val();
        let dailyMin = 0;
        let userType = '';

        if (treatmentCost !== '' && treatmentMin !== '' && assessmentCost !== '' && assessmentMin !== '') {
            if ($('#id_type').find(":selected").text() === '---------') {
                userType = 'position: ';
            }
            else {
                userType = $('#id_type').find(":selected").text();
            }
            dailyMin = (parseFloat(treatmentCost) * parseFloat(treatmentMin)) + (parseFloat(assessmentCost) * parseFloat(assessmentMin));
            if (dailyMin < 0) {
                $('#dailyMinimum').text('Daily Minimum for your temporary position: $-');
            }
            else {
                $('#dailyMinimum').text('Daily Minimum for your temporary ' + userType + '  : ' + currencyFormatter.format(dailyMin));
            }
        }
        else {
            $('#dailyMinimum').text('Daily Minimum for your temporary position: $-');
        }
    });

    // Prevent decimal numbers from being added to the number of treatments/assessments
    $('#id_treatmentMin, #id_assessmentMin, #id_reservePrice').on('keyup', function (e) {
        if (e.which === 46) return false;
    }).on('input', function () {
        var self = this;
        setTimeout(function () {
            if (self.value.indexOf('.') != -1) self.value = parseInt(self.value, 10);
        }, 0);
    });

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

    $("#practiceAreaCheckBox").change(function () {
        if (this.checked) {
            $('#practiceAreaDiv').show();
        }
        else {
            $('#practiceAreaDiv').remove();
            // $('.aop').remove();
            // $('#id_practice_area_auction-TOTAL_FORMS').val(0);
            // $('#id_practice_area_auction-MAX_NUM_FORMS').val(0);
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

$('#id_paymentType').change(function () {
    if ($('#id_paymenttype').find(":selected").text() != '---------' && $('#id_type').find(":selected").text() != '---------') {
        greyOutFields(false);
    }
});

$('#id_type').change(function () {
    if ($('#id_type').find(":selected").text() != '---------') {
        $("#optionsMessage").hide();
        $('.feeSplitFields').hide();
        $('#practiceAreaCheckBoxDiv').removeClass('d-none');

        if ($("#practiceAreaCheckBox").is(':checked')) {
            $('#practiceAreaDiv').hide();
            $('#practiceAreaCheckBox').prop('checked', false);
        }

        if ($('#id_paymentType').find(":selected").text() != '---------') {
            greyOutFields(false);
        }

        $.ajax({
            type: "GET",
            url: "/auction/data/check_user_payment_type",
            data: {
                'name': $('#id_type').find(":selected").text()
            },
            success: function (response) {
                console.log(response);
                if (!response.feeSplit) {
                    $("#id_paymentType").val("2");
                    $('#id_paymentType').attr('disabled', 'disabled');
                }
                else {
                    $('#id_paymentType').val('');
                    $('#id_paymentType').removeAttr('disabled');
                    let feeSplitPresent = false;
                    $("#id_paymentType > option").each(function () {
                        if (this.text == "Fee Split") {
                            feeSplitPresent = true;
                        }
                    });
                }

            },
            error: function (error) {
                console.log('error: ', error);
            }
        });
    }
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

$('#priceInfoIcon').click(function () {
    let page = $("#pageTitle").text();
    $.ajax({
        type: "GET",
        url: "/auction/data/get_popups",
        data: {
            'page': page,
            'clickID': 'priceInfoIcon'
        },
        success: function (response) {
            console.log(response);
            if (response.message != "") {
                $("#modalTitle").text(response.title);
                $("#modalParagraph").html(response.message);
                $("#popupModal").modal('show');
            }
        },
        error: function (error) {
            console.log('error: ', error);
        }
    });
})

$("#submitButton").click(function () {
    let errorList = '';

    if ($("#id_type").val() === "0") {
        errorList += "<li>Please select an auction type.</li>";
    }

    if ($("#id_paymentType").val() === "") {
        errorList += "<li>Please select a payment type.</li>";
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

    if ($("#id_thursdayStart").val() !== '') {
        thursdayStart = new Date('1970-01-01T' + $("#id_thursdayStart").val() + 'Z');
    }
    if ($("#id_thursdayEnd").val() !== '') {
        thursdayEnd = new Date('1970-01-01T' + $("#id_thursdayEnd").val() + 'Z');
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

    let treatmentCost = $('#id_treatmentCost').val();
    let treatmentMin = $('#id_treatmentMin').val();
    let assessmentCost = $('#id_assessmentCost').val();
    let assessmentMin = $('#id_assessmentMin').val();

    let costMax = 500;
    let sessionMax = 10;

    //Validate Start/End date
    var now = new Date();
    let oneYear = new Date(now);
    oneYear.setDate(now.getDate() + 365)

    if (days_between(placementStart, placementEnd, false) === 0) {
        errorList += '<li>The placement must be at least one day long.</li>';
    }
    else {
        if (days_between(placementStart, now, false) < 0) {
            errorList += '<li>Therapist Start Date cannot be in the past.</li>';
        }

        if (days_between(placementEnd, now, false) < 0) {
            errorList += '<li>Therapist End Date cannot be in the past.</li>';
        }
    }

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
    if (days_between(placementStart, placementEnd, true) > 548) {
        errorList += '<li>Looks like you are trying to create an ad for an opening longer than 18 months! Please contact us to help you set this up.</li>';
    }

    //Validate Reserve price
    let reserve = '';
    let reserveCapital = '';
    if ($('#id_paymentType').find(":selected").text() === 'Fee Split') {
        reserve = 'reserve split';
        reserveCapital = 'Reserve split';
    }
    else {
        reserve = 'reserve price';
        reserveCapital = 'Reserve price';
    }
    if (reservePrice !== "") {
        if (reservePrice <= 0) {
            errorList += "<li>" + reserveCapital + " cannot be 0 or less. If no " + reserve + " is desired leave the field blank.</li>";
        }
    }
    if (reservePrice !== "" && $('#id_paymentType').find(":selected").text() === 'Flat Fee') {
        if (reservePrice > 25000) {
            errorList += "<li>" + reserveCapital + " must be less than $25,000.</li>";
        }
    }
    if (reservePrice !== "" && $('#id_paymentType').find(":selected").text() === 'Fee Split') {
        if (reservePrice > 100) {
            errorList += "<li>" + reserveCapital + " cannot be greater than 100%.</li>";
        }
    }

    //Validate treatment and assessment costs if the payment type is fee split
    if ($('#id_paymentType').find(":selected").text() === 'Fee Split') {
        //Treatment Cost
        if (treatmentCost === "") {
            errorList += "<li>Please enter a Treatment Cost.</li>";
        }
        if (treatmentCost > costMax && treatmentCost !== "") {
            errorList += "<li>Treatment costs cannot exceed " + currencyFormatter.format(costMax) + "</li>";
        }
        if (treatmentCost < 1 && treatmentCost !== "") {
            errorList += "<li>Treatment costs must be at least $1.</li>";
        }

        //Minimum # of Treatments
        if (treatmentMin === "") {
            errorList += "<li>Please enter a Minimum Number of Treatments.</li>";
        }
        if (treatmentMin > sessionMax && treatmentMin !== "") {
            errorList += "<li>Minimum number of Treatment sessions cannot exceed " + sessionMax + "</li>";
        }
        if (treatmentMin < 0 && treatmentMin !== "") {
            errorList += "<li>Minimum number of Treatment sessions cannot be negative.</li>";
        }

        //Assessment Cost
        if (assessmentCost === "") {
            errorList += "<li>Please enter a Assessment Cost.</li>";
        }
        if (assessmentCost > costMax && assessmentCost !== "") {
            errorList += "<li>Assessment costs cannot exceed " + currencyFormatter.format(costMax) + "</li>";
        }
        if (assessmentCost < 0 && assessmentCost !== "") {
            errorList += "<li>Assessment costs must be at least $1.</li>";
        }

        //Minimum # of Assessments
        if (assessmentMin === "") {
            errorList += "<li>Please enter a Minimum Number of Assessments.</li>";
        }
        if (assessmentMin > sessionMax && assessmentMin !== "") {
            errorList += "<li>Minimum Number of Assessments cannot exceed " + sessionMax + "</li>";
        }
        if (assessmentMin < 1 && assessmentMin !== "") {
            errorList += "<li>Minimum number of Assessments sessions cannot be negative.</li>";
        }
    }


    //Validate Therapist Schedule
    let mondayVal = check_times(mondayStart, mondayEnd, 'Monday');
    let tuesdayVal = check_times(tuesdayStart, tuesdayEnd, 'Tuesday');
    let wednesdayVal = check_times(wednesdayStart, wednesdayEnd, 'Wednesday');
    let thursdayVal = check_times(thursdayStart, thursdayEnd, 'Thursday');
    let fridayVal = check_times(fridayStart, fridayEnd, 'Friday');
    let saturdayVal = check_times(saturdayStart, saturdayEnd, 'Saturday');
    let sundayVal = check_times(sundayStart, sundayEnd, 'Sunday');

    if (mondayVal === 'None') {
        noneCount++;
    }
    else if (mondayVal != '' && mondayVal != 'None') {
        errorList += mondayVal;
    }

    if (tuesdayVal === 'None') {
        noneCount++;
    }
    else if (tuesdayVal != '' && tuesdayVal != 'None') {
        errorList += tuesdayVal;
    }

    if (wednesdayVal === 'None') {
        noneCount++;
    }
    else if (wednesdayVal != '' && wednesdayVal != 'None') {
        errorList += wednesdayVal;
    }

    if (thursdayVal === 'None') {
        noneCount++;
    }
    else if (thursdayVal != '' && thursdayVal != 'None') {
        errorList += thursdayVal;
    }

    if (fridayVal === 'None') {
        noneCount++;
    }
    else if (fridayVal != '' && fridayVal != 'None') {
        errorList += fridayVal;
    }

    if (saturdayVal === 'None') {
        noneCount++;
    }
    else if (saturdayVal != '' && saturdayVal != 'None') {
        errorList += saturdayVal;
    }

    if (sundayVal === 'None') {
        noneCount++;
    }
    else if (sundayVal != '' && sundayVal != 'None') {
        errorList += sundayVal;
    }

    //All day's have been left blank
    if (noneCount === 7) {
        errorList += "<li>You're trying to create a posting, but you've left the therapist schedule blank.  This would indicate to bidding therapists that they have a start and end date, but no days to actual be at your clinic. Please complete at least 1 day showing the start and end time for the therapist before you can submit your auction.</li>";
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
            else if (parseInt($(this).val()) < 0) {
                errorList += '<li>' + demographicCategory + ' cannot be negative.</li>';
            }
            demographicTotal += parseInt($(this).val());
        }
    });
    if (demographicTotal !== 100) {
        errorList += '<li>Demographic percentages must add up to 100%.</li>';
    }

    //Validate Areas of Practice
    if ($("#practiceAreaCheckBox").is(':checked')) {
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
                else if (parseInt($(this).val()) < 0) {
                    errorList += '<li>' + practiceCategory + ' cannot be negative.</li>';
                }
                practiceTotal += parseInt($(this).val());
            }
        });
        if (practiceTotal !== 100) {
            errorList += '<li>Practice area percentages must add up to 100%.</li>';
        }
        console.log(practiceTotal);
        console.log(errorList);
    }

    if (errorList !== '') {
        $('.alert.alert-block.alert-danger').show();
        $('#errorList').html(errorList);
        window.scrollTo(0, 0);
        return false;
    }
    //Django cannot get the values from disabled fields so re-enabled them on submit
    $("form :disabled").removeAttr('disabled');
});

function greyOutFields(val) {
    $("#id_placementStart, #id_placementEnd, #id_reservePrice, #id_demogrpahic_auction-0-percentage, #id_demogrpahic_auction-1-percentage, #id_demogrpahic_auction-2-percentage").attr("disabled", val);
}

function getDateDiff() {
    let start = "";
    let end = "";
    let startDate = "";
    let endDate = "";
    let contractCost = 0

    if ($('#id_placementStart')[0].value != "") {
        start = $('#id_placementStart')[0].value.split("-");
        startDate = new Date(start[0], start[1] - 1, start[2]);
    }

    if ($('#id_placementEnd')[0].value != "") {
        end = $('#id_placementEnd')[0].value.split("-");
        endDate = new Date(end[0], end[1] - 1, end[2]);
    }

    let dateDiff = days_between(startDate, endDate, true);
    // if (dateDiff < 30) {
    //     $("#id_payFrequency option[value='3']").remove();
    // }
    // else {
    //     let monthlyPresent = false;
    //     $("#id_payFrequency > option").each(function () {
    //         if (this.text == "Monthly") {
    //             monthlyPresent = true;
    //         }
    //     });
    //     if (!monthlyPresent) {
    //         $('#id_payFrequency').append($('<option>', {
    //             value: 3,
    //             text: "Monthly"
    //         }));
    //     }
    // }
    if ($('#id_paymentType').find(":selected").text() === 'Fee Split' && endDate > startDate) {
        if (dateDiff * 25 < 300) {
            contractCost = 300;
        }
        else if (dateDiff * 25 > 5000) {
            contractCost = 5000;
        }
        else {
            contractCost = dateDiff * 25;
        }
        $('#contractCost').text('Contract price if matched: ' + currencyFormatter.format(contractCost) + ' + HST');
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

function days_between(date1, date2, abs) {
    // The number of milliseconds in one day
    const ONE_DAY = 1000 * 60 * 60 * 24;
    let differenceMs = '';
    if (abs) {
        // Calculate the difference in milliseconds
        differenceMs = Math.abs(date1 - date2);
    }
    else {
        differenceMs = date1 - date2;
    }

    // Convert back to days and return
    return Math.round(differenceMs / ONE_DAY);

}