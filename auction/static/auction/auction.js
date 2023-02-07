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

$(document).ready(function () {
    //Check if the province of the clinic matches the province of the therapist, if not show pop-p
    let page = $("#pageTitle").text();
    $.ajax({
        type: "GET",
        url: "/auction/data/get_popups",
        data: {
            'page': page
        },
        success: function (response) {
            console.log(response);
            if (response.message != "") {
                $("#modalTitle").text(response.title);
                $("#modalParagraph").text(response.message);
                $("#popupModal").modal('show');
            }
        },
        error: function (error) {
            console.log('error: ', error);
        }
    });

    $("#modalPopupOKButton").click(function () {
        console.log("ggg");
        $.ajax({
            type: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            url: "/auction/data/set_acknowledgement",
            data: {
                'page': page
            },
            success: function (response) {
                console.log(response);
                if (response.message != "") {
                    $("#modalTitle").text(response.title);
                    $("#modalParagraph").text(response.message);
                    $("#popupModal").modal('show');
                }
            },
            error: function (error) {
                console.log('error: ', error);
            }
        });
    });

});

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
                timeLeft += days + "d " + hours + "h ";
            }
            else if (days == 0 && hours > 0) {
                timeLeft += hours + "h " + minutes + "m ";
            }
            else if (days == 0 && hours == 0 && minutes > 0) {
                timeLeft += minutes + "m " + seconds + "s";
            }
            else {
                timeLeft += seconds + "s"
            }

            // Output the result in an element with id="demo"
            document.getElementById("auctionTimer-" + auctionID).innerHTML = timeLeft;

            // If the count down is over, write some text 
            if (distance < 0) {
                clearInterval(x);
                document.getElementById("auctionTimer-" + auctionID).innerHTML = "Auction Completed";
            }
        }
        else {
            document.getElementById("auctionTimer-" + auctionID).innerHTML = "Auction Completed";
        }
    }, 1000);
}

function getTimeDistance(date) {
    // console.log(date);
    // console.log(Date());
    // Set the date we're counting down to
    let countDownDate = new Date(date).getTime();
    // Get today's date and time
    var now = new Date().getTime();
    // console.log(countDownDate + " " + now)
    // Find the distance between now and the count down date
    var distance = countDownDate - now;
    // console.log(distance)
    return distance;
}

// let currentYear = document.getElementById('current-year');
// currentYear.innerText = new Date().getFullYear();