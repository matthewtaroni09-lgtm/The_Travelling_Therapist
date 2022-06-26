$(document).ready(function () {
    if ($('.alert-block').css("display") === "block") {
        $('#profile-tab').tab('show');
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