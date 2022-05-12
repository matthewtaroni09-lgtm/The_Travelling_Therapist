const getActiveAuctionsClnic = () => {
    $.ajax({
        type: "GET",
        url: "/auction/data/active_auctions_clinic",
        success: function (response) {
            console.log(response);
            auctionStartDateTime = response.data[0].auctionStart;
            auctionEndDateTime = response.data.auctionEnd;
            currentLowBid = response.data.currentLowBid;

            response.data.forEach(element => {
                countDown(element.auctionEnd, element.auctionID);
            })

        },
        error: function (error) {
            console.log('error: ', error);
        }
    })
}

getActiveAuctionsClnic();