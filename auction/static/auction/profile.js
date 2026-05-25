$(document).ready(function () {
    const showTab = (selector) => {
        const el = document.querySelector(selector);
        if (el) {
            const tab = new bootstrap.Tab(el);
            tab.show();
        }
    };

    if ($('.alert-block').css("display") === "block") {
        showTab('#profile-tab');
    }

    if ($('#error_1_id_imageOne').css("display") === "block") {
        showTab('#profile-tab');
    }
    if ($('#error_1_id_imageTwo').css("display") === "block") {
        showTab('#profile-tab');
    }
    if ($('#error_1_id_imageThree').css("display") === "block") {
        showTab('#profile-tab');
    }
    if ($('#error_1_id_imageFour').css("display") === "block") {
        showTab('#profile-tab');
    }

    // Handle hash in URL to show specific tab
    var hash = window.location.hash;
    if (hash) {
        showTab('button[data-bs-target="' + hash + '"]');
    }

    // Raffle Modal Logic
    $('.raffle-details-btn').on('click', function() {
        const title = $(this).data('title');
        const description = $(this).data('description');
        const tickets = $(this).data('tickets');
        const endDate = $(this).data('end-date');
        
        $('#modal-raffle-title').text(title);
        $('#modal-raffle-description').text(description);
        $('#modal-raffle-tickets-required').text('Tickets Required per Entry: ' + tickets);
        if (endDate) {
            $('#modal-raffle-end-date').html('<span class="material-icons fs-6 align-middle">timer</span> Ends: ' + endDate).show();
        } else {
            $('#modal-raffle-end-date').hide();
        }
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

    // Referral Modal Copy Logic
    $('#copyReferralBtn').on('click', function() {
        const copyText = document.getElementById("referralLinkInput");
        copyText.select();
        copyText.setSelectionRange(0, 99999); // For mobile devices
        
        navigator.clipboard.writeText(copyText.value).then(() => {
            const feedback = $('#copyFeedback');
            feedback.fadeIn();
            setTimeout(() => {
                feedback.fadeOut();
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
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
                        // Set hash to load the raffles tab and refresh page
                        window.location.hash = '#raffles';
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
