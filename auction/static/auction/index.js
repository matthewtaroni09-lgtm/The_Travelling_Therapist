const modal = new bootstrap.Modal(document.getElementById("modal"))
htmx.on("htmx:afterSwap", (e) => {
    modal.show();
})

htmx.on("htmx:beforeSwap", (e) => {
    modal.hide();
})

$("#modalXButton").click(function () {
    modal.hide();
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