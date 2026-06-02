// let currentYear = document.getElementById('current-year');
// currentYear.innerText = new Date().getFullYear();
// alert('hello');

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
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)'
        ],
        borderColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)'
        ],
        data: [20, 25, 55],
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
    'MSK',
    'Neuro',
    'CardioResp',
];

const areasOfPracticeData = {
    labels: areasOfPracticeLabels,
    datasets: [{
        label: 'Area of Practice',
        backgroundColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)'
        ],
        borderColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 205, 86)'
        ],
        data: [50, 300, 10],
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

// Mailchimp Newsletter Integration
$(document).ready(function () {
    $('#newsletter-form').submit(function (e) {
        e.preventDefault();
        const $form = $(this);
        const $message = $('#newsletter-message');
        const $input = $('#id_email_address');
        const $btn = $form.find('.newsletter-btn');

        // Show loading state
        $btn.prop('disabled', true).text('Submitting...');
        $message.hide().removeClass('text-success text-danger');

        $.ajax({
            type: "GET", // Mailchimp uses JSONP (GET) for cross-domain requests
            url: $form.attr('action').replace('/post?', '/post-json?'),
            data: $form.serialize(),
            cache: false,
            dataType: 'jsonp',
            jsonp: 'c', // Mailchimp expects 'c' for callback
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                $btn.prop('disabled', false).text('Subscribe');
                if (data.result === 'success') {
                    $message.html('<span class="text-success">Success! Please check your email to confirm.</span>').fadeIn();
                    $input.val(''); // Clear input
                } else {
                    // Display Mailchimp error
                    let errorMsg = data.msg || 'An error occurred. Please try again.';
                    if (errorMsg.indexOf(' - ') > 0) {
                        errorMsg = errorMsg.substring(errorMsg.indexOf(' - ') + 3);
                    }
                    $message.html('<span class="text-danger">' + errorMsg + '</span>').fadeIn();
                }
            },
            error: function () {
                $btn.prop('disabled', false).text('Subscribe');
                $message.html('<span class="text-danger">Could not connect to the server. Please try again later.</span>').fadeIn();
            }
        });
    });
});