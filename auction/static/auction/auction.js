const submitBidButton = document.getElementById("submitBidButton");
const bidForm = document.getElementById("bidForm");
const spinnerBox = document.getElementById('spinner-box');
const bidAmountInput = document.getElementById("id_amount");
const auctionInfo = document.getElementById("auctionInfo");
const email = document.getElementById("email");
const csrf = document.getElementsByName('csrfmiddlewaretoken');
const URL = window.location.href;
const auctionID = URL.substring(URL.lastIndexOf('/') + 1);
console.log("auctionID = " + auctionID);

const auction_list = document.getElementById("auction_list");

let timer = "";
let auctionStartDateTime = 0;
let auctionEndDateTime = 0;
let reservePrice = 0;

const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// const getAuction = () => {
//     $.ajax({
//         type: "GET",
//         url: "/auction/data/auction/" + auctionID,
//         success: function (response) {
//             console.log(response);
//             auctionStartDateTime = response.data.auctionStart;
//             auctionEndDateTime = response.data.auctionEnd;
//             currentLowBid = response.data.currentLowBid;
//             countDown(auctionEndDateTime);
//             // spinnerBox.classList.add('not-visible');

//             //Update time this because it could change
//             // auction_list.innerHTML += `
//             // <ul>
//             //     Auction Start Date: ` + auctionStartDateTime + ` <br>
//             //     Auction End Date: ` + auctionEndDateTime + `<br>
//             //     Current Bid: $` + currentLowBid + `<br>
//             // </ul>`;

//             //Demographics Chart
//             const demographicsLabels = [
//                 'Under 18',
//                 '18 - 65',
//                 'Over 65',
//             ];

//             const data = {
//                 labels: demographicsLabels,
//                 datasets: [{
//                     label: 'Client Demographics',
//                     backgroundColor: [
//                         'rgb(255, 99, 132)',
//                         'rgb(54, 162, 235)',
//                         'rgb(255, 205, 86)'
//                     ],
//                     borderColor: [
//                         'rgb(255, 99, 132)',
//                         'rgb(54, 162, 235)',
//                         'rgb(255, 205, 86)'
//                     ],
//                     data: [response.data.demogrpahics.Under18, response.data.demogrpahics.eighteenToSixtyFive, response.data.demogrpahics.Over65],
//                 }]
//             };

//             const config = {
//                 type: 'doughnut',
//                 data: data,
//                 options: {
//                     responsive: true,
//                     layout: {
//                         padding: 20
//                     },
//                     plugins: {
//                         title: {
//                             display: true,
//                             text: 'Client Demographics',
//                             font: {
//                                 size: 16
//                             },
//                             color: '#000',
//                             padding: {
//                                 bottom: 30
//                             }
//                         },
//                         legend: {
//                             display: true,
//                             position: 'bottom',
//                         }
//                     }
//                 }
//             };

//             const demographics = new Chart(
//                 document.getElementById('demographics'),
//                 config
//             );


//             // Area of Practice Chart
//             const areasOfPracticeLabels = [
//                 'MSK',
//                 'Neuro',
//                 'CardioResp',
//             ];

//             const areasOfPracticeData = {
//                 labels: areasOfPracticeLabels,
//                 datasets: [{
//                     label: 'Area of Practice',
//                     backgroundColor: [
//                         'rgb(255, 99, 132)',
//                         'rgb(54, 162, 235)',
//                         'rgb(255, 205, 86)'
//                     ],
//                     borderColor: [
//                         'rgb(255, 99, 132)',
//                         'rgb(54, 162, 235)',
//                         'rgb(255, 205, 86)'
//                     ],
//                     data: [response.data.practiceAreas.MSK, response.data.practiceAreas.Neuro, response.data.practiceAreas.CardioResp],
//                 }]
//             };

//             const areasOfPracticeConfig = {
//                 type: 'doughnut',
//                 data: areasOfPracticeData,
//                 options: {
//                     responsive: true,
//                     layout: {
//                         padding: 20
//                     },
//                     plugins: {
//                         title: {
//                             display: true,
//                             text: 'Area of Practice',
//                             font: {
//                                 size: 16
//                             },
//                             color: '#000',
//                             padding: {
//                                 bottom: 30
//                             }
//                         },
//                         legend: {
//                             display: true,
//                             position: 'bottom'
//                         }
//                     }
//                 }
//             };

//             const areasOfPracticeChart = new Chart(
//                 document.getElementById('areaOfPractice'),
//                 areasOfPracticeConfig
//             );
//         },
//         error: function (error) {
//             console.log('error: ', error);
//         }
//     })
// }


const getAuction = () => {
    $.ajax({
        type: "GET",
        url: "/auction/data/all_auctions",
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
getAuction();

// const getDemographics = () => {
//     $.ajax({
//         type: "GET",
//         url: "/auction/data/auction/" + auctionID,
//         success: function (response) {
//             console.log(response);
//             auctionStartDateTime = response.data.auctionStart;
//             auctionEndDateTime = response.data.auctionEnd;
//             currentLowBid = response.data.currentLowBid;
//             countDown(auctionEndDateTime);
//             // spinnerBox.classList.add('not-visible');
//             auction_list.innerHTML += `
//             <ul>
//                 Auction Start Date: ` + auctionStartDateTime + ` <br>
//                 Auction End Date: ` + auctionEndDateTime + `<br>
//                 Current Bid: $` + currentLowBid + `<br>
//             </ul>`;
//         },
//         error: function (error) {
//             console.log('error: ', error);
//         }
//     })
// }



// bidForm.addEventListener('submit', e => {
//     console.log("submitted");
//     e.preventDefault();

//     let auctionEndDate = 0;
//     if (getTimeDistance(auctionEndDateTime) < 60000000 & getTimeDistance(auctionEndDateTime) > 0) {
//         clearInterval(timer);
//         auctionEndDateTime = new Date(new Date(auctionEndDateTime).getTime() + 5000000);
//         countDown(auctionEndDateTime);
//         auctionEndDate = auctionEndDateTime;
//     }

//     auctionInfo.innerHTML =
//         `<ul>
//             Auction Start Date: ` + auctionStartDateTime + ` <br>
//             Auction End Date: ` + auctionEndDateTime + `<br>
//             Current Bid: $` + bidAmountInput.value + `<br>
//         </ul>`;

//     $.ajax({
//         type: 'POST',
//         url: "/auction/create_bid/" + auctionID,
//         data: {
//             'csrfmiddlewaretoken': csrf[0].value,
//             'bidAmount': bidAmountInput.value,
//             'auctionEnd': auctionEndDate
//         },
//         success: function (response) {
//             console.log(response)
//         },
//         error: function (error) {
//             console.log(error)
//         }
//     })
// });

// email.addEventListener('click', e => {
//     $.ajax({
//         type: 'POST',
//         url: "/auction/send_email_message/",
//         data: {
//             'csrfmiddlewaretoken': csrf[0].value
//         },
//         success: function (response) {
//             console.log(response)
//         },
//         error: function (error) {
//             console.log(error)
//         }
//     })
// });

function countDown(date, auctionID) {
    // Update the count down every 1 second
    timer = setInterval(function () {

        let distance = getTimeDistance(date);

        // Time calculations for days, hours, minutes and seconds
        let days = Math.floor(distance / (1000 * 60 * 60 * 24));
        let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);
        let timeLeft = "";

        if (days >= 0 && hours >= 0 && minutes >= 0 && seconds >= 0) {
            if (days > 0) {
                timeLeft += days + "d ";
            }
            if (hours > 0) {
                timeLeft += hours + "h ";
            }

            // Output the result in an element with id="demo"
            document.getElementById("auctionTimer-" + auctionID).innerHTML = timeLeft + minutes + "m " + seconds + "s";

            // If the count down is over, write some text 
            if (distance < 0) {
                clearInterval(x);
                document.getElementById("auctionTimer-" + auctionID).innerHTML = "Auction Closed";
            }
        }
        else {
            document.getElementById("auctionTimer-" + auctionID).innerHTML = "Auction Closed";
        }
    }, 1000);
}

function getTimeDistance(date) {
    // Set the date we're counting down to
    let countDownDate = new Date(date).getTime();
    // Get today's date and time
    var now = new Date().getTime();

    // Find the distance between now and the count down date
    var distance = countDownDate - now;
    return distance;
}