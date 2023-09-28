const URL = window.location.href;
const auctionID = URL.substring(URL.lastIndexOf('/') + 1);
let currentLowBid = 0

$(document).ready(function () {
    $("#warningMessage").hide();
    // $("#submitBidButton").prop("disabled", true);
    let max_bid = 0;
    let currentLowBid = 0;
    let url = $(location).attr('href').split("/");
    let auctionID = url[url.length - 1];
    let auctionEnd = "";
    let reservePrice = 0;

    $(document).keypress(
        function (event) {
            if (event.which == '13') {
                event.preventDefault();
            }
        });

    $('#splitCompSlider').slider({
        formatter: function (value) {
            return 'Current value: ' + value;
        }
    });

    $("#submitBidButton").click(function () {
        if ($("#id_amount").val() !== '') {
            $("#bidModalSubFooter").show();
            $("#closeButton").prop('disabled', true);
            $("#submitBidButton").prop('disabled', true);
        }
    });

    $("#closeButtonSubFooter").click(function () {
        $("#id_amount").val('');
        $("#closeButton").prop('disabled', false);
        $("#submitBidButton").prop('disabled', false);
        $("#bidModalSubFooter").hide();
    });

    if ($('#error_1_id_amount').css("display") === "block") {
        $("#exampleModal").modal("show");
    }

    $.ajax({
        type: "GET",
        url: "/auction/data/view_auction_data",
        data: {
            'auctionID': auctionID
        },
        success: function (response) {
            console.log(response);
            max_bid = response.max_bid;
            currentLowBid = response.currentLowBid;
            auctionEnd = new Date(response.auctionEnd);
            reservePrice = response.reservePrice;

            let currentTime = new Date().getTime()
            let subtractMilliSecondsValue = auctionEnd.getTime() - currentTime;
            console.log(subtractMilliSecondsValue);
            setTimeout(auctionEnded, subtractMilliSecondsValue);

            if (currentLowBid == 1) {
                $("#submitBidButton").prop("disabled", true);
                $("#id_amount").prop("disabled", true);
                $("#id_amount").attr('placeholder', 'Lowest Bid Reached');;
            }
        },
        error: function (error) {
            console.log('error: ', error);
        }
    });

    $("#id_amount").change(function () {
        $("#warningMessage").hide();
        $("#warningMessage").removeClass("alert-warning");
        $("#warningMessage").removeClass("alert-danger");
        if ($("#id_amount").val().includes(".")) {
            bidError("Danger", "Please enter only whole numbers.");
        }
        else if (parseInt($("#id_amount").val()) > currentLowBid && currentLowBid !== 0 && currentLowBid !== null) {
            bidError("Warning", "Your bid is over the current minimum bid and will not be considered for determing the winner of the auction.Click Submit if you would like to proceed anyway.");
        }
        else if (parseInt($("#id_amount").val()) <= 0) {
            bidError("Danger", "Bids must be above $0.");
        }
        else {
            $("#submitBidButton").prop("disabled", false);
        }
    });

    function bidError(alert, message) {
        let alertType = "";
        if (alert == "Danger") {
            alertType = "alert-danger";
            $("#submitBidButton").prop("disabled", true);
        }
        else {
            alertType = "alert-warning";
            $("#submitBidButton").prop("disabled", false);
        }
        $("#warningMessage").addClass(alertType);
        $("#warningMessage").text(message)
        $("#warningMessage").show();
    }

    function auctionEnded() {
        $("#bidButton").hide();
        $("#exampleModal").modal("hide");
        if (currentLowBid > reservePrice && reservePrice !== null) {
            $("#bidText").text("Reserve price not met");
        }
        else {
            $("#bidText").text("Winning Bid: $" + currentLowBid.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        }
    }
});

const getAuction = () => {
    $.ajax({
        type: "GET",
        url: "/auction/data/auction/" + auctionID,
        success: function (response) {
            console.log(response);
            auctionStartDateTime = response.data.auctionStart;
            auctionEndDateTime = response.data.auctionEnd;
            currentLowBid = response.data.currentLowBid;
            countDown(auctionEndDateTime, auctionID);

            //Demographics Chart
            const demographicsLabels = []
            for (let demographic of response.data.demographic_types) {
                demographicsLabels.push(demographic)
            }

            const demographicsValues = []
            for (let value of response.data.demographic_percentages) {
                demographicsValues.push(value)
            }

            const data = {
                labels: demographicsLabels,
                datasets: [{
                    label: 'Client Demographics',
                    backgroundColor: [
                        '#0AEAA9',
                        '#0ABBEA',
                        '#A90AEA',
                        '#61707D',
                        '#7D8491',
                        '#CAE5FF'
                    ],
                    borderColor: [
                        '#0AEAA9',
                        '#0ABBEA',
                        '#A90AEA',
                        '#61707D',
                        '#7D8491',
                        '#CAE5FF'
                    ],
                    data: demographicsValues,
                }]
            };

            const config = {
                type: 'doughnut',
                data: data,
                options: {
                    responsive: true,
                    layout: {
                        padding: 20
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Client Demographics',
                            font: {
                                size: 16
                            },
                            color: '#000',
                            padding: {
                                bottom: 30
                            }
                        },
                        legend: {
                            display: true,
                            position: 'bottom',
                        }
                    }
                }
            };

            const demographics = new Chart(
                document.getElementById('demographics'),
                config
            );

            // Area of Practice Chart
            const areasOfPracticeLabels = []
            for (let practice of response.data.practice_area_types) {
                areasOfPracticeLabels.push(practice)
            }

            const areaOfPracticeValues = []
            for (let value of response.data.practice_area_percentages) {
                areaOfPracticeValues.push(value)
            }

            const areasOfPracticeData = {
                labels: areasOfPracticeLabels,
                datasets: [{
                    label: 'Area of Practice',
                    backgroundColor: [
                        '#0AEAA9',
                        '#0ABBEA',
                        '#A90AEA',
                        '#61707D',
                        '#7D8491',
                        '#CAE5FF'
                    ],
                    borderColor: [
                        '#0AEAA9',
                        '#0ABBEA',
                        '#A90AEA',
                        '#61707D',
                        '#7D8491',
                        '#CAE5FF'
                    ],
                    data: areaOfPracticeValues,
                }]
            };

            const areasOfPracticeConfig = {
                type: 'doughnut',
                data: areasOfPracticeData,
                options: {
                    responsive: true,
                    layout: {
                        padding: 20
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Area of Practice',
                            font: {
                                size: 16
                            },
                            color: '#000',
                            padding: {
                                bottom: 30
                            }
                        },
                        legend: {
                            display: true,
                            position: 'bottom'
                        }
                    }
                }
            };

            const areasOfPracticeChart = new Chart(
                document.getElementById('areaOfPractice'),
                areasOfPracticeConfig
            );
        },
        error: function (error) {
            console.log('error: ', error);
        }
    })
}

getAuction();