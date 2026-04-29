$(document).ready(function () {
    if ($('.alert-block').css("display") === "block") {
        $('#profile-tab').tab('show');
    }

    if ($('#error_1_id_imageOne').css("display") === "block") {
        $('#profile-tab').tab('show');
    }
    if ($('#error_1_id_imageTwo').css("display") === "block") {
        $('#profile-tab').tab('show');
    }
    if ($('#error_1_id_imageThree').css("display") === "block") {
        $('#profile-tab').tab('show');
    }
    if ($('#error_1_id_imageFour').css("display") === "block") {
        $('#profile-tab').tab('show');
    }

    // Handle hash in URL to show specific tab
    var hash = window.location.hash;
    if (hash) {
        $('.nav-tabs button[data-bs-target="' + hash + '"]').tab('show');
    }
});
const getActiveAuctionsClinic = () => {
    $.ajax({
        type: "GET",
        url: "/auction/data/active_auctions_clinic",
        success: function (response) {
            console.log(response);
            if (response.data.length > 0) {
                auctionStartDateTime = response.data[0].auctionStart;
                auctionEndDateTime = response.data.auctionEnd;
                currentLowBid = response.data.currentLowBid;

                response.data.forEach(element => {
                    countDown(element.auctionEnd, element.auctionID);
                })
            }

        },
        error: function (error) {
            console.log('error: ', error);
        }
    })
}

getActiveAuctionsClinic();