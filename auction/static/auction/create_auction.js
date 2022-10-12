$(document).ready(function () {
    let practiceTypes = [];
    let usedTypes = [];
    // $('.alert.alert-block.alert-danger').hide();
    $.ajax({
        type: "GET",
        url: "/auction/data/get_practice_types",
        success: function (response) {
            for (let i = 0; i < response.data.length; i++) {
                practiceTypes.push(response.data[i].name);
            }
            $('[id^=id_demogrpahic_auction-]').each(function (i, el) {
                if ($(this).is('select')) {
                    $(this).attr("disabled", true);
                    $(this).val(parseInt($(this).attr('id').match(/\d/)[0]) + 1);
                }
            });
            $('[id^=id_practice_area_auction-]').each(function (i, el) {
                if ($(this).is('select')) {
                    let index = 0;
                    $(this).attr("disabled", true);
                    $(this).find('option').each(function (i, el) {
                        if (practiceTypes.includes($(this).text()) && !usedTypes.includes(i)) {
                            index = i;
                            usedTypes.push(index)
                            return false;
                        }
                    });
                    $(this).val(index);
                }
            });
        },
        error: function (error) {
            console.log('error: ', error);
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
    //Django cannot get the values from disabled fields so re-enabled them on submit
    $("#submitButton").click(function () {
        let errorList = '';
        let demographicTotal = 0;
        let practiceTotal = 0;
        let demographicCategory = '';
        let practiceCategory = '';
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
            errorList += '<li>Demographic percentages must add up to 100%</li>';
        }

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
            errorList += '<li>Practice area percentages must add up to 100%</li>';
        }
        console.log(practiceTotal);
        console.log(errorList);

        if (errorList !== '') {
            $('.alert.alert-block.alert-danger').show();
            $('#errorList').html(errorList);
            window.scrollTo(0, 0);
            return false;
        }

        $("form :disabled").removeAttr('disabled');
    });
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

function days_between(date1, date2) {
    // The number of milliseconds in one day
    const ONE_DAY = 1000 * 60 * 60 * 24;

    // Calculate the difference in milliseconds
    const differenceMs = Math.abs(date1 - date2);

    // Convert back to days and return
    return Math.round(differenceMs / ONE_DAY);

}