$(document).ready(function () {
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