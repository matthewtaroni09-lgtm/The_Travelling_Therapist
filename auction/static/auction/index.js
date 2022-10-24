// $(document).ready(function () {
//     $("#allAuctionsLink").click(function () {
//         $('#allAuctionsModal').modal('toggle');
//     });
const modal = new bootstrap.Modal(document.getElementById("modal"))
htmx.on("htmx:afterSwap", (e) => {
    // Response targeting #dialog => show the modal
    // if (e.detail.target.id == "dialog") {
    modal.show()
    // }
})

htmx.on("htmx:beforeSwap", (e) => {
    // Empty response targeting #dialog => hide the modal
    // if (e.detail.target.id == "dialog" && !e.detail.xhr.response) {
    modal.hide()
    // e.detail.shouldSwap = false
    // }
})
//});
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