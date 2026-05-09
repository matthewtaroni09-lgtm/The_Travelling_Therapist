$(document).ready(function () {
    if ($('.alert-block').css("display") === "block") {
        $('#profile-tab').tab('show');
    }

    if ($('#error_1_id_imageOne').css("display") === "block") {
        $('#profile-tab').tab('show');
    }
    if ($('#error_1_id_imageTwo').css("display") === "block") {
        $('#profile-tab').tab('show');
    }
    if ($('#error_1_id_imageThree').css("display") === "block") {
        $('#profile-tab').tab('show');
    }
    if ($('#error_1_id_imageFour').css("display") === "block") {
        $('#profile-tab').tab('show');
    }

    // Handle hash in URL to show specific tab
    var hash = window.location.hash;
    if (hash) {
        $('.nav-tabs button[data-bs-target="' + hash + '"]').tab('show');
    }

    // Raffle Modal Logic
    $('.raffle-details-btn').on('click', function() {
        const title = $(this).data('title');
        const description = $(this).data('description');
        const tickets = $(this).data('tickets');
        
        $('#modal-raffle-title').text(title);
        $('#modal-raffle-description').text(description);
        $('#modal-raffle-tickets-required').text('Tickets Required per Entry: ' + tickets);
        $('#ticket-count').val(1);
    });

    $('#increment-tickets').on('click', function() {
        let currentVal = parseInt($('#ticket-count').val());
        if (!isNaN(currentVal)) {
            $('#ticket-count').val(currentVal + 1);
        } else {
            $('#ticket-count').val(1);
        }
    });

    $('#decrement-tickets').on('click', function() {
        let currentVal = parseInt($('#ticket-count').val());
        if (!isNaN(currentVal) && currentVal > 1) {
            $('#ticket-count').val(currentVal - 1);
        } else {
            $('#ticket-count').val(1);
        }
    });

    $('#confirm-purchase').on('click', function() {
        const ticketCount = $('#ticket-count').val();
        const raffleTitle = $('#modal-raffle-title').text();
        const csrfToken = $('[name=csrfmiddlewaretoken]').val();
        
        $.ajax({
            type: "POST",
            url: "/auction/data/join_raffle",
            data: JSON.stringify({
                'raffle_title': raffleTitle,
                'ticket_count': ticketCount
            }),
            contentType: "application/json",
            headers: {
                "X-CSRFToken": csrfToken
            },
            success: function (response) {
                if (response.status === 'success') {
                    Swal.fire({
                        title: 'Success!',
                        text: response.message,
                        icon: 'success',
                        confirmButtonText: 'Great!',
                        confirmButtonColor: '#0f9972'
                    }).then(() => {
                        // Update the balance in the UI
                        $('h2:contains("Available Tickets")').next().text(response.new_balance);
                        // Refresh page to show new entry in Participating Raffles
                        location.reload(); 
                    });
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: response.message,
                        icon: 'error',
                        confirmButtonText: 'Understood',
                        confirmButtonColor: '#d33'
                    });
                }
            },
            error: function (error) {
                console.log('error: ', error);
                Swal.fire({
                    title: 'System Error',
                    text: 'Could not process your request. Please try again later.',
                    icon: 'error'
                });
            }
        });
    });
});

const getActiveAuctionsClinic = () => {
    $.ajax({
        type: "GET",
        url: "/auction/data/active_auctions_clinic",
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

getActiveAuctionsClinic();
