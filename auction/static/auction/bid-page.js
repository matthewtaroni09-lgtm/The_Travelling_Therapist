const URL = window.location.href;
const auctionID = URL.substring(URL.lastIndexOf('/') + 1);
let currentLowBid = 0

$(document).ready(function () {
    $("#warningMessage").hide();
    let max_bid = 0;
    let currentLowBid = 0;
    let url = $(location).attr('href').split("/");
    let auctionID = url[url.length - 1];
    let auctionEnd = "";
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

            let currentTime = new Date().getTime()
            let subtractMilliSecondsValue = auctionEnd.getTime() - currentTime;
            console.log(subtractMilliSecondsValue);
            setTimeout(auctionEnded, subtractMilliSecondsValue);
        },
        error: function (error) {
            console.log('error: ', error);
        }
    });

    $("#id_amount").change(function () {
        $("#warningMessage").hide();
        if (parseInt($("#id_amount").val()) > currentLowBid && currentLowBid !== 0) {
            $("#warningMessage").text("Your bid is over the current minimum bid and will not be considered for determing the winner of the auction. Click Submit if you would like to proceed anyway.")
            $("#warningMessage").show();
        }
    });

    function auctionEnded() {
        $("#bidButton").hide();
        $("#exampleModal").modal("hide");
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
            const demographicsLabels = [
                'Under 18',
                '18 - 65',
                'Over 65',
            ];

            const data = {
                labels: demographicsLabels,
                datasets: [{
                    label: 'Client Demographics',
                    backgroundColor: [
                        '#0AEAA9',
                        '#0ABBEA',
                        '#A90AEA'
                    ],
                    borderColor: [
                        '#0AEAA9',
                        '#0ABBEA',
                        '#A90AEA'
                    ],
                    data: [response.data.demogrpahics.Under18, response.data.demogrpahics.eighteenToSixtyFive, response.data.demogrpahics.Over65],
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
            const areasOfPracticeLabels = [
                'Musculoskeletal',
                'Neurological',
                'Cardiorespiratory',
            ];

            const areasOfPracticeData = {
                labels: areasOfPracticeLabels,
                datasets: [{
                    label: 'Area of Practice',
                    backgroundColor: [
                        '#0AEAA9',
                        '#0ABBEA',
                        '#A90AEA'
                    ],
                    borderColor: [
                        '#0AEAA9',
                        '#0ABBEA',
                        '#A90AEA'
                    ],
                    data: [response.data.practiceAreas.MSK, response.data.practiceAreas.Neuro, response.data.practiceAreas.CardioResp],
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