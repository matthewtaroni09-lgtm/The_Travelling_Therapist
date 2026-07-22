$(document).ready(function () {
    const maxImageSizeBytes = 10 * 1024 * 1024;
    const defaultTabTargets = new Set(['#auction-history', '#auction-history-t']);

    function showImageSizeError(fieldLabel) {
        Swal.fire({
            title: 'Image too large',
            text: fieldLabel + ' must be 10 MB or smaller. Please choose a smaller image.',
            icon: 'error',
            confirmButtonText: 'OK',
            confirmButtonColor: '#0f9972'
        });
    }

    function validateImageFieldSize(inputId, fieldLabel) {
        const input = document.getElementById(inputId);
        if (!input || !input.files || input.files.length === 0) {
            return true;
        }
        const file = input.files[0];
        if (file.size > maxImageSizeBytes) {
            input.value = '';
            showImageSizeError(fieldLabel);
            return false;
        }
        return true;
    }

    const tooltipEls = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipEls.forEach(function (el) {
        bootstrap.Tooltip.getOrCreateInstance(el);
    });

    const showTab = (selector) => {
        const el = document.querySelector(selector);
        if (el) {
            const tab = new bootstrap.Tab(el);
            tab.show();
        }
    };

    const openChallengesAccordion = () => {
        const challengeCollapse = document.getElementById('collapseChallengesT') || document.getElementById('collapseChallenges');
        if (!challengeCollapse) {
            return;
        }
        const collapseInstance = bootstrap.Collapse.getOrCreateInstance(challengeCollapse, { toggle: false });
        collapseInstance.show();
    };

    const syncUrlHashToActiveTab = (tabTrigger) => {
        if (!tabTrigger || !tabTrigger.getAttribute) {
            return;
        }

        const target = tabTrigger.getAttribute('data-bs-target');
        if (!target) {
            return;
        }

        const nextUrl = new URL(window.location.href);
        if (defaultTabTargets.has(target)) {
            nextUrl.hash = '';
        }
        else {
            nextUrl.hash = target;
        }

        window.history.replaceState({}, '', nextUrl.toString());
    };

    document.querySelectorAll('.nav-link[data-bs-toggle="tab"]').forEach(function (tabTrigger) {
        tabTrigger.addEventListener('shown.bs.tab', function (event) {
            syncUrlHashToActiveTab(event.target);
        });
    });

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
        if (hash.indexOf('#raffles') === 0) {
            if (document.querySelector('button[data-bs-target="#raffles-t"]')) {
                showTab('button[data-bs-target="#raffles-t"]');
            }
            else {
                showTab('button[data-bs-target="#raffles"]');
            }

            if (hash.indexOf('challenges') !== -1) {
                openChallengesAccordion();
            }
        }
        else {
            showTab('button[data-bs-target="' + hash + '"]');
        }
    }

    // Raffle Modal Logic
    $('.raffle-details-btn').on('click', function() {
        const title = $(this).data('title');
        const description = $(this).data('description');
        const tickets = parseInt($(this).data('tickets')) || 1;
        const endDate = $(this).data('end-date');
        
        $('#modal-raffle-title').text(title);
        $('#modal-raffle-description').text(description);
        $('#modal-raffle-tickets-required').text('Tickets Required per Entry: ' + tickets);
        if (endDate) {
            $('#modal-raffle-end-date').html('<span class="material-icons fs-6 align-middle">timer</span> Ends: ' + endDate).show();
        } else {
            $('#modal-raffle-end-date').hide();
        }
        
        // Save tickets required as the 'step' for this raffle
        $('#ticket-count').attr('data-step', tickets);
        $('#ticket-count').attr('min', tickets);
        $('#ticket-count').attr('step', tickets);
        $('#ticket-count').attr('inputmode', 'numeric');
        $('#ticket-count').val(tickets);
    });

    $('#ticket-count').on('keydown', function (event) {
        if (
            event.key === '-' || event.key === '+' || event.key === 'e' || event.key === 'E'
            || event.code === 'NumpadSubtract' || event.code === 'NumpadAdd'
        ) {
            event.preventDefault();
        }
    });

    $('#ticket-count').on('beforeinput', function (event) {
        const rawEvent = event.originalEvent;
        const inputData = rawEvent && rawEvent.data ? rawEvent.data : '';
        if (/[-+eE]/.test(inputData)) {
            event.preventDefault();
        }
    });

    $('#ticket-count').on('input', function () {
        const step = parseInt($(this).attr('data-step')) || 1;
        let value = parseInt($(this).val(), 10);
        if (Number.isNaN(value) || value < step) {
            value = step;
        }
        $(this).val(value);
    });

    $('#increment-tickets').on('click', function() {
        let step = parseInt($('#ticket-count').attr('data-step')) || 1;
        let currentVal = parseInt($('#ticket-count').val());
        if (!isNaN(currentVal)) {
            $('#ticket-count').val(currentVal + step);
        } else {
            $('#ticket-count').val(step);
        }
    });

    $('#decrement-tickets').on('click', function() {
        let step = parseInt($('#ticket-count').attr('data-step')) || 1;
        let currentVal = parseInt($('#ticket-count').val());
        if (!isNaN(currentVal) && currentVal > step) {
            $('#ticket-count').val(currentVal - step);
        } else {
            $('#ticket-count').val(step);
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
        let ticketCount = parseInt($('#ticket-count').val());
        const step = parseInt($('#ticket-count').attr('data-step')) || 1;
        const raffleTitle = $('#modal-raffle-title').text();
        const csrfToken = $('[name=csrfmiddlewaretoken]').val();

        // Rounding Logic: Ensure multiples of 'step' (tickets_required)
        if (ticketCount % step !== 0) {
            const recommended = Math.floor(ticketCount / step) * step;
            if (recommended === 0) {
                Swal.fire('Invalid Amount', 'This raffle requires at least ' + step + ' tickets for one entry.', 'error');
                $('#ticket-count').val(step);
                return;
            }

            Swal.fire({
                title: 'Adjust Ticket Amount?',
                text: 'This raffle requires ' + step + ' tickets per entry. Would you like to use ' + recommended + ' tickets instead to get ' + (recommended/step) + ' entries?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#0f9972',
                confirmButtonText: 'Yes, use ' + recommended + ' tickets',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    $('#ticket-count').val(recommended);
                    $('#confirm-purchase').click(); // Re-trigger with rounded value
                }
            });
            return;
        }
        
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

    // --- Challenges Section Logic ---

    // 1. Weekly Reward Countdown
    const updateWeeklyTimer = () => {
        const nextDateStr = $('#next-award-date').val() || $('#next-award-date-t').val();
        if (!nextDateStr) return;

        const nextDate = new Date(nextDateStr).getTime();
        const timerEls = $('#weekly-timer, #weekly-timer-t');

        const interval = setInterval(() => {
            const now = new Date().getTime();
            const distance = nextDate - now;

            if (distance < 0) {
                clearInterval(interval);
                timerEls.text("Available Now!");
                return;
            }

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            timerEls.text(`${days}d ${hours}h ${minutes}m ${seconds}s`);
        }, 1000);
    };
    updateWeeklyTimer();

    // 2. Challenge Referral Link Copy (Clinic)
    $('#copyChallengeLink').on('click', function() {
        const copyText = document.getElementById("challengeReferralLink");
        copyText.select();
        copyText.setSelectionRange(0, 99999);
        navigator.clipboard.writeText(copyText.value).then(() => {
            const feedback = $('#copyChallengeFeedback');
            feedback.fadeIn();
            setTimeout(() => feedback.fadeOut(), 2000);
        });
    });

    // 3. Challenge Referral Link Copy (Therapist)
    $('#copyChallengeLinkT').on('click', function() {
        const copyText = document.getElementById("challengeReferralLinkT");
        copyText.select();
        copyText.setSelectionRange(0, 99999);
        navigator.clipboard.writeText(copyText.value).then(() => {
            const feedback = $('#copyChallengeFeedbackT');
            feedback.fadeIn();
            setTimeout(() => feedback.fadeOut(), 2000);
        });
    });

    $('form[method="post"][enctype="multipart/form-data"]').on('submit', function (event) {
        const isClinicProfileForm = !!document.getElementById('div_id_imageOne') || !!document.getElementById('id_imageOne');
        if (!isClinicProfileForm) {
            return;
        }

        const imageFields = [
            ['id_imageOne', 'Image 1'],
            ['id_imageTwo', 'Image 2'],
            ['id_imageThree', 'Image 3'],
            ['id_imageFour', 'Image 4'],
        ];

        for (const [inputId, label] of imageFields) {
            if (!validateImageFieldSize(inputId, label)) {
                event.preventDefault();
                return false;
            }
        }
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
