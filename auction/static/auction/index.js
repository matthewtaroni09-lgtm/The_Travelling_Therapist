const modal = new bootstrap.Modal(document.getElementById("modal"))

$(document).ready(function () {
    $("#modalXButton, #cancelButton").click(function () {
        modal.hide();
        $('#searchAllCheckbox').prop('checked', false);
    });

    $("#allAuctionsLink").click(function () {
        modal.show();
        $("#allAuctionsButton").show();
        $("#selectAuctionsButton").hide();
    });
    $("#selectAuctionsLink").click(function () {
        $("#allAuctionsLink").show();
        $("#selectAuctionsLink").hide();
    });

    $("#allAuctionsButton").click(function () {
        $("#allAuctionsLink").hide();
        $("#selectAuctionsLink").show();
    });

    $("#searchAllCheckbox").change(function () {
        modal.show('show');
    });
});
const getAuctionIndex = () => {
    $.ajax({
        type: "GET",
        url: "/auction/data/all_auctions",
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

getAuctionIndex();