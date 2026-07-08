const currencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

let feeSplitCalcShown = false;
let assessmentChecked = false;
let treatmentChecked = false;

function getSelectedPaymentTypes() {
    return $('input[name="paymentTypesSelection"]:checked').map(function () {
        return $(this).val();
    }).get();
}

function getSelectedFlatFeeType() {
    return $('input[name="flatFeeType"]:checked').val() || '';
}

function syncOfferGuidanceUI(selectedPaymentTypes) {
    const flatFeeType = getSelectedFlatFeeType();
    const showFeeSplitGuidance = selectedPaymentTypes.includes('Fee Split');
    const showHourlyGuidance = selectedPaymentTypes.includes('Flat Fee') && flatFeeType === 'hourly';
    const showTotalGuidance = selectedPaymentTypes.includes('Flat Fee') && flatFeeType === 'total_contract';

    $('#desiredFeeSplitContainer').toggleClass('d-none', !showFeeSplitGuidance);
    $('#flatFeeGuidanceContainer').toggleClass('d-none', !(showHourlyGuidance || showTotalGuidance));
    $('#desiredFlatFeeHourlyContainer').toggleClass('d-none', !showHourlyGuidance);
    $('#desiredFlatFeeTotalContainer').toggleClass('d-none', !showTotalGuidance);

    if (!showFeeSplitGuidance) {
        $('#id_desiredFeeSplitPercentage').val('');
    }
    if (!showHourlyGuidance) {
        $('#id_desiredFlatFeeHourly').val('');
    }
    if (!showTotalGuidance) {
        $('#id_desiredFlatFeeTotalContract').val('');
    }
}

function syncPaymentTypeUI() {
    const selectedPaymentTypes = getSelectedPaymentTypes();
    const feeSplitEnabled = selectedPaymentTypes.includes('Fee Split');
    const flatFeeEnabled = selectedPaymentTypes.includes('Flat Fee');
    const paymentTypeSelected = selectedPaymentTypes.length > 0;

    greyOutFields(!paymentTypeSelected);

    if (flatFeeEnabled) {
        $('#flatFeeTypeContainer').removeClass('d-none');
    }
    else {
        $('#flatFeeTypeContainer').addClass('d-none');
        $('input[name="flatFeeType"]').prop('checked', false);
    }

    syncOfferGuidanceUI(selectedPaymentTypes);

    if (feeSplitEnabled) {
        $('#assessmentCheckBoxDiv').removeClass('d-none');
        $('#treatmentCheckBoxDiv').removeClass('d-none');
        $('#assessmentTreatmentInfoDiv').removeClass('d-none');
        greyOutFields(false);
    }
    else {
        $('#assessmentCheckBoxDiv').addClass('d-none');
        $('#treatmentCheckBoxDiv').addClass('d-none');
        $('#assessmentTreatmentInfoDiv').addClass('d-none');
        $('.assessmentField').addClass('d-none');
        $('.treatmentField').addClass('d-none');
        $('.feeSplitCalcFields').addClass('d-none');
        $('#assessmentCheckBox').prop('checked', false);
        $('#treatmentCheckBox').prop('checked', false);
        assessmentChecked = false;
        treatmentChecked = false;
        $('#id_assessmentCost').val('');
        $('#id_assessmentMin').val('');
        $('#id_treatmentMin').val('');
        $('#id_treatmentCost').val('');
        calculateDailyMin();
    }
}

$(document).ready(function () {
    $('.alert.alert-block.alert-danger').hide();
    $('.feeSplitFields').hide();
    greyOutFields(true);
    // Prevent pressing enter from submitting the form
    $(document).keypress(
        function (event) {
            if (event.which == '13') {
                event.preventDefault();
            }
        });

    $('#id_type').change(function () {
        if ($('#id_type').find(":selected").text() != '---------') {
            $('#practiceAreaCheckBoxDiv').removeClass('d-none');
            $("#optionsMessage").hide();

            if ($("#practiceAreaCheckBox").is(':checked')) {
                $('#practiceAreaDiv').hide();
                $('#practiceAreaCheckBox').prop('checked', false);
            }

            syncPaymentTypeUI();

            $.ajax({
                type: "GET",
                url: "/auction/data/check_user_payment_type",
                data: {
                    'name': $('#id_type').find(":selected").text()
                },
                success: function (response) {
                    console.log(response);
                    $('#id_paymentTypesSelection_0').prop('disabled', false);
                    syncPaymentTypeUI();

                },
                error: function (error) {
                    console.log('error: ', error);
                }
            });
        }
        else {
            $("#optionsMessage").hide();
            $('input[name="paymentTypesSelection"]').prop('checked', false).prop('disabled', false);
            syncPaymentTypeUI();
        }
    });

    $('input[name="paymentTypesSelection"]').change(function () {
        syncPaymentTypeUI();
    });

    $('input[name="flatFeeType"]').change(function () {
        syncOfferGuidanceUI(getSelectedPaymentTypes());
    });

    //Show assessment fields checkbox
    $('#assessmentCheckBox').change(function () {
        if (this.checked) {
            $('.assessmentField').removeClass('d-none');
            $('.feeSplitCalcFields').removeClass('d-none');
            assessmentChecked = true;
        }
        else {
            $('.assessmentField').addClass('d-none');
            $('#id_assessmentCost').val('');
            $('#id_assessmentMin').val('');
            calculateDailyMin();
            assessmentChecked = false;
            // If treatment check and assessment check are both unchecked then hide the calculated fields
            if (!treatmentChecked) {
                $('.feeSplitCalcFields').addClass('d-none');
            }
        }
    });

    //Show treatment fields checkbox
    $('#treatmentCheckBox').change(function () {
        if (this.checked) {
            $('.treatmentField').removeClass('d-none');
            $('.feeSplitCalcFields').removeClass('d-none');
            treatmentChecked = true;
        }
        else {
            $('.treatmentField').addClass('d-none');
            $('#id_treatmentCost').val('');
            $('#id_treatmentMin').val('');
            calculateDailyMin();
            treatmentChecked = false;
            // If treatment check and assessment check are both unchecked then hide the calculated fields
            if (!assessmentChecked) {
                $('.feeSplitCalcFields').addClass('d-none');
            }
        }
    });

    $('#id_treatmentCost, #id_treatmentMin, #id_assessmentCost, #id_assessmentMin').change(function () {
        // If a negative number is entered blank out that input
        if ($(this).val() < 0) {
            $(this).val('');
        }

        calculateDailyMin();
    });

    // Prevent decimal numbers from being added to the number of treatments/assessments
    $('#id_treatmentMin, #id_assessmentMin').on('keyup', function (e) {
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
            $('#practiceAreaDiv').hide();
            $('#AOPOpen').text("Yes");
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

    syncPaymentTypeUI();
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
    popUps('priceInfoIcon');
});

$('#reservePriceInfoIcon').click(function () {
    popUps('reservePriceInfoIcon');
});

$('#assessmentTreatmentInfoIcon').click(function () {
    popUps('assessmentTreatmentInfoIcon');
});

$("#submitButton").click(function () {
    let errorList = '';

    if ($("#id_type").val() === "0") {
        errorList += "<li>Please select an clinician type.</li>";
    }

    if (getSelectedPaymentTypes().length === 0) {
        errorList += "<li>Please select a payment type.</li>";
    }

    if (getSelectedPaymentTypes().includes('Flat Fee') && getSelectedFlatFeeType() === "") {
        errorList += "<li>Please select how flat fee offers should be priced.</li>";
    }

    let placementStart = new Date($("#id_placementStart").val());
    let placementEnd = new Date($("#id_placementEnd").val());

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
            errorList += '<li>Clinician Start Date cannot be in the past.</li>';
        }

        if (days_between(placementEnd, now, false) < 0) {
            errorList += '<li>Clinician End Date cannot be in the past.</li>';
        }
    }

    if (placementStart === NaN) {
        errorList += '<li>Please enter a valid Clinician Start Date.</li>';
    }
    if (placementEnd === NaN) {
        errorList += '<li>Please enter a valid Clinician End Date.</li>';
    }
    if (placementEnd < placementStart) {
        errorList += '<li>The Clinician End Date must be after the Clinician Start Date.</li>';
    }
    if (placementStart > oneYear) {
        errorList += '<li>Placements must start within the next 12 months.</li>';
    }
    if (days_between(placementStart, placementEnd, true) > 548) {
        errorList += '<li>Looks like you are trying to create an ad for an opening longer than 18 months! Please contact us to help you set this up.</li>';
    }

    //Validate treatment and assessment costs if the payment type is fee split
    if (getSelectedPaymentTypes().includes('Fee Split')) {
        //Minimum # of Assessments
        if (assessmentMin === "" && assessmentCost !== "") {
            errorList += "<li>Please enter a Minimum Number of Assessments.</li>";
        }
        if (assessmentMin > sessionMax && assessmentMin !== "") {
            errorList += "<li>Minimum Number of Assessments cannot exceed " + sessionMax + "</li>";
        }
        if (assessmentMin < 0 && assessmentMin !== "") {
            errorList += "<li>Minimum Number of Assessments sessions cannot be negative.</li>";
        }

        //Assessment Cost
        if (assessmentCost === "" && assessmentMin !== "") {
            errorList += "<li>Please enter a Assessment Cost.</li>";
        }
        if (assessmentCost > costMax && assessmentCost !== "") {
            errorList += "<li>Assessment Costs cannot exceed " + currencyFormatter.format(costMax) + "</li>";
        }
        if (assessmentCost < 1 && assessmentCost !== "" && assessmentMin > 0 && assessmentMin !== "") {
            errorList += "<li>Assessment Costs must be at least $1.</li>";
        }
        if (assessmentCost > 0 && assessmentCost !== "" && assessmentMin == 0 && assessmentMin !== "") {
            errorList += "<li>There cannot be an assessment cost if there isn't at least 1 Daily Minimum Assessment.</li>";
        }

        //Minimum # of Treatments
        if (treatmentMin === "" && treatmentCost !== "") {
            errorList += "<li>Please enter a Minimum Number of Treatments.</li>";
        }
        if (treatmentMin > sessionMax && treatmentMin !== "") {
            errorList += "<li>Minimum Number of Treatment sessions cannot exceed " + sessionMax + "</li>";
        }
        if (treatmentMin < 0 && treatmentMin !== "") {
            errorList += "<li>Minimum Number of Treatment sessions cannot be negative.</li>";
        }
        //Treatment Cost
        if (treatmentCost === "" && treatmentMin !== "") {
            errorList += "<li>Please enter a Treatment Cost.</li>";
        }
        if (treatmentCost > costMax && treatmentCost !== "") {
            errorList += "<li>Treatment Costs cannot exceed " + currencyFormatter.format(costMax) + "</li>";
        }
        if (treatmentCost < 1 && treatmentCost !== "" && treatmentMin > 0 && treatmentMin !== "") {
            errorList += "<li>Treatment Costs must be at least $1.</li>";
        }
        if (treatmentCost > 0 && treatmentCost !== "" && treatmentMin == 0 && treatmentMin !== "") {
            errorList += "<li>There cannot be an Treatment Cost if there isn't at least 1 Daily Minimum Treatments.</li>";
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
        errorList += "<li>You're trying to create a posting, but you've left the Clinician schedule blank.  This would indicate to bidding Clinicians that they have a start and end date, but no days to actual be at your healthcare facility. Please complete at least 1 day showing the start and end time for the Clinician before you can submit your listing.</li>";
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
        $('#AOPPopulated').val("Yes");
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
    $("#id_placementStart, #id_placementEnd, #id_demogrpahic_auction-0-percentage, #id_demogrpahic_auction-1-percentage, #id_demogrpahic_auction-2-percentage").attr("disabled", val);
}

function calculateDailyMin() {
    let treatmentCost = $('#id_treatmentCost').val();
    let treatmentMin = $('#id_treatmentMin').val();
    let assessmentCost = $('#id_assessmentCost').val();
    let assessmentMin = $('#id_assessmentMin').val();
    let dailyMin = 0;
    let userType = '';

    if ((treatmentCost !== '' && treatmentMin !== '') || (assessmentCost !== '' && assessmentMin !== '')) {
        if ($('#id_type').find(":selected").text() === '---------') {
            userType = 'position: ';
        }
        else {
            userType = $('#id_type').find(":selected").text();
        }
        if ($('#assessmentCheckBox').prop('checked') == true && $('#treatmentCheckBox').prop('checked') == true && (treatmentCost !== '' && treatmentMin !== '' && assessmentCost !== '' && assessmentMin !== '')) {
            dailyMin = (parseFloat(treatmentCost) * parseFloat(treatmentMin)) + (parseFloat(assessmentCost) * parseFloat(assessmentMin));
        }
        else if ($('#assessmentCheckBox').prop('checked') == true && $('#treatmentCheckBox').prop('checked') == false) {
            dailyMin = parseFloat(assessmentCost) * parseFloat(assessmentMin);
        }
        else if ($('#assessmentCheckBox').prop('checked') == false && $('#treatmentCheckBox').prop('checked') == true) {
            dailyMin = parseFloat(treatmentCost) * parseFloat(treatmentMin);
        }
        if (dailyMin <= 0) {
            $('#dailyMinimum').text('Daily Minimum paid to your temporary position: $-');
        }
        else {
            $('#dailyMinimum').text('Daily Minimum paid to your temporary ' + userType + '  : ' + currencyFormatter.format(dailyMin));
        }
    }
    else {
        $('#dailyMinimum').text('Daily Minimum paid to your temporary position: $-');
    }
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
    if (endDate > startDate) {
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

function popUps(id) {
    let page = $("#pageTitle").text();
    $.ajax({
        type: "GET",
        url: "/auction/data/get_popups",
        data: {
            'page': page,
            'clickID': id
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