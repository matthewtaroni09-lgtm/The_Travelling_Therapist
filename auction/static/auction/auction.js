const submitBidButton = document.getElementById("submitBidButton");
const bidForm = document.getElementById("bidForm");
const spinnerBox = document.getElementById('spinner-box');
const bidAmountInput = document.getElementById("id_amount");
const auctionInfo = document.getElementById("auctionInfo");
const email = document.getElementById("email");
const csrf = document.getElementsByName('csrfmiddlewaretoken');
// const URL = window.location.href;
// const auctionID = URL.substring(URL.lastIndexOf('/') + 1);

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
    console.log(date);
    console.log(Date());
    // Set the date we're counting down to
    let countDownDate = new Date(date).getTime() + (4 * 60 * 60 * 1000);
    // Get today's date and time
    var now = new Date().getTime();
    console.log(countDownDate + " " + now)
    // Find the distance between now and the count down date
    var distance = countDownDate - now;
    console.log(distance)
    return distance;
}

let currentYear = document.getElementById('current-year');
currentYear.innerText = new Date().getFullYear();