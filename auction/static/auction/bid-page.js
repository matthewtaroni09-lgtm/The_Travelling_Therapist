const URL = window.location.href;
const auctionID = URL.substring(URL.lastIndexOf('/') + 1);
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
            // spinnerBox.classList.add('not-visible');

            //Update time this because it could change
            // auction_list.innerHTML += `
            // <ul>
            //     Auction Start Date: ` + auctionStartDateTime + ` <br>
            //     Auction End Date: ` + auctionEndDateTime + `<br>
            //     Current Bid: $` + currentLowBid + `<br>
            // </ul>`;

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