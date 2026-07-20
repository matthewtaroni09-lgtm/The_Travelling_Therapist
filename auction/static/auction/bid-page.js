(() => {
const pageUrl = window.location.href;
const auctionID = pageUrl.substring(pageUrl.lastIndexOf('/') + 1);
let currentLowBid = 0;
let paymentType = '';
let minBidIncrement = 0;
let reservePrice = null;
let paymentTypes = [];
let currentOfferTabIndex = 0;
let isAuctionActive = false;

$(document).ready(function () {
    $("#warningMessage").hide();
    let auctionEnd = "";
    const confirmButton = document.getElementById('confirmBidButton');
    const confirmTooltipWrap = document.getElementById('confirmBidTooltipWrap');
    const confirmTooltipText = 'You must enter at least one offer before confirming.';
    let confirmDisabledTooltip = null;

    if (window.bootstrap) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            bootstrap.Tooltip.getOrCreateInstance(el);
        });
    }

    if (confirmTooltipWrap && window.bootstrap) {
        confirmDisabledTooltip = bootstrap.Tooltip.getOrCreateInstance(confirmTooltipWrap);
    }

    $(document).keypress(function (event) {
        if (event.which === 13) {
            event.preventDefault();
        }
    });

    function enabledOfferTabs() {
        return $('#offerTabs .nav-link').map(function () {
            return $(this).data('offer-tab');
        }).get();
    }

    function activeTabKey() {
        return $('#offerTabs .nav-link.active').data('offer-tab') || enabledOfferTabs()[0];
    }

    function showWarning(level, message) {
        $('#warningMessage')
            .removeClass('alert-danger alert-warning')
            .addClass(level === 'danger' ? 'alert-danger' : 'alert-warning')
            .text(message)
            .show();
    }

    function clearWarning() {
        $('#warningMessage').hide().text('').removeClass('alert-danger alert-warning');
    }

    function isValidFlatFeeOffer() {
        if ($('#flatFeeAmount').length === 0) {
            return false;
        }
        const value = parseFloat($('#flatFeeAmount').val() || '0');
        if ($('#flatFeeHourlySlider').length) {
            return value >= 15 && value <= 1000;
        }
        return value > 0;
    }

    function normalizeFlatFeeValue(rawValue) {
        const parsed = parseFloat(rawValue);
        if (Number.isNaN(parsed)) {
            return null;
        }
        if (parsed < 0) {
            return 0;
        }
        return parsed;
    }

    function setFlatFeeValue(rawValue) {
        const normalizedValue = normalizeFlatFeeValue(rawValue);
        if (normalizedValue === null) {
            return;
        }
        $('#flatFeeAmount').val(normalizedValue);
        if ($('#flatFeeHourlySlider').length) {
            $('#flatFeeHourlySlider').val(normalizedValue);
        }
    }

    function isValidFeeSplitOffer() {
        if ($('#feeSplitAmountInput').length === 0) {
            return false;
        }
        const value = parseInt($('#feeSplitAmountInput').val() || '0', 10);
        return value > 0 && value <= 100;
    }

    function normalizeFeeSplitValue(rawValue) {
        const parsed = parseInt(rawValue, 10);
        if (Number.isNaN(parsed)) {
            return null;
        }
        if (parsed < 0) {
            return 0;
        }
        if (parsed > 100) {
            return 100;
        }
        return parsed;
    }

    function setFeeSplitValue(rawValue) {
        const normalizedValue = normalizeFeeSplitValue(rawValue);
        if (normalizedValue === null) {
            return;
        }
        $('#feeSplitSlider').val(normalizedValue);
        $('#feeSplitValue').text(normalizedValue);
        $('#feeSplitAmountInput').val(normalizedValue);
        if ($('#feeSplitAmountTyped').length) {
            $('#feeSplitAmountTyped').val(normalizedValue);
        }
    }

    function hasAnyValidOffer() {
        return isValidFlatFeeOffer() || isValidFeeSplitOffer();
    }

    function hasSingleOfferInputTab() {
        const offerInputTabs = enabledOfferTabs().filter(function (tabKey) {
            return tabKey !== 'offer-finalize';
        });
        return offerInputTabs.length === 1;
    }

    function updateSummary() {
        if ($('#summaryFlatFee').length) {
            if (isValidFlatFeeOffer()) {
                const suffix = $('#flatFeeAmount').siblings('.input-group-text').last().text() === '/hr' ? ' /hr' : '';
                $('#summaryFlatFee').text('$' + Number($('#flatFeeAmount').val()).toLocaleString() + suffix);
            }
            else {
                $('#summaryFlatFee').text('Not entered');
            }
        }

        if ($('#summaryFeeSplit').length) {
            if (isValidFeeSplitOffer()) {
                $('#summaryFeeSplit').text($('#feeSplitAmountInput').val() + '%');
            }
            else {
                $('#summaryFeeSplit').text('Not entered');
            }
        }

        const hasValidOffer = hasAnyValidOffer();
        $('#confirmBidButton').prop('disabled', !hasValidOffer);

        if (hasSingleOfferInputTab()) {
            const isFinalizeActive = activeTabKey() === 'offer-finalize';
            $('#nextTabButton').prop('disabled', !hasValidOffer && !isFinalizeActive);
        }
        else {
            $('#nextTabButton').prop('disabled', false);
        }

        if (confirmTooltipWrap && confirmDisabledTooltip && confirmButton) {
            if (confirmButton.disabled) {
                confirmTooltipWrap.setAttribute('tabindex', '0');
                confirmTooltipWrap.setAttribute('data-bs-toggle', 'tooltip');
                confirmTooltipWrap.setAttribute('title', confirmTooltipText);
                confirmTooltipWrap.style.pointerEvents = 'auto';
                confirmDisabledTooltip.enable();
            }
            else {
                confirmDisabledTooltip.hide();
                confirmDisabledTooltip.disable();
                confirmTooltipWrap.removeAttribute('tabindex');
                confirmTooltipWrap.removeAttribute('data-bs-toggle');
                confirmTooltipWrap.removeAttribute('title');
                confirmTooltipWrap.style.pointerEvents = 'auto';
            }
        }
    }

    function setFooterState() {
        const tabs = enabledOfferTabs();
        const current = activeTabKey();
        const index = tabs.indexOf(current);
        const isFinalize = current === 'offer-finalize';
        const singleOfferTab = hasSingleOfferInputTab();

        $('#backTabButton').toggle(index > 0);
        $('#nextTabButton').toggle(!isFinalize);
        $('#skipTabButton').toggle(!isFinalize && !singleOfferTab);
        $('#confirmBidTooltipWrap').toggle(isFinalize);
        $('#confirmBidButton').toggle(isFinalize);
        $('#offerFaqHelper').toggle(!isFinalize);

        if (!isFinalize && singleOfferTab) {
            $('#nextTabButton').prop('disabled', !hasAnyValidOffer());
        }
        else {
            $('#nextTabButton').prop('disabled', false);
        }
    }

    function activateOfferTab(tabKey) {
        $('#offerTabs .nav-link').removeClass('active').attr('aria-selected', 'false');
        $('#offerTabs .nav-link[data-offer-tab="' + tabKey + '"]').addClass('active').attr('aria-selected', 'true');
        $('.ttt-offer-pane').removeClass('show active');
        $('#' + tabKey).addClass('show active');
        setFooterState();
        updateSummary();
        clearWarning();
    }

    function moveTab(direction) {
        const tabs = enabledOfferTabs();
        const currentIndex = tabs.indexOf(activeTabKey());
        const targetIndex = currentIndex + direction;
        if (targetIndex >= 0 && targetIndex < tabs.length) {
            activateOfferTab(tabs[targetIndex]);
        }
    }

    $('#offerTabs .nav-link').on('click', function () {
        const selectedTab = $(this).data('offer-tab');
        if (selectedTab === 'offer-finalize' && hasSingleOfferInputTab() && !hasAnyValidOffer()) {
            showWarning('warning', 'Enter an offer before moving to Finalize.');
            return;
        }
        activateOfferTab(selectedTab);
    });

    $('#nextTabButton').on('click', function () {
        const currentTab = activeTabKey();
        if (currentTab === 'offer-flat-fee' && $('#flatFeeHourlySlider').length) {
            const rawValue = ($('#flatFeeAmount').val() || '').trim();
            if (rawValue !== '') {
                const typedValue = parseFloat(rawValue);
                if (Number.isNaN(typedValue) || typedValue < 15 || typedValue > 1000) {
                    showWarning('warning', 'Hourly flat fee offers must be between $15 and $1000');
                    return;
                }
            }
        }
        moveTab(1);
    });

    $('#skipTabButton').on('click', function () {
        const currentTab = activeTabKey();
        if (currentTab === 'offer-flat-fee' && $('#flatFeeAmount').length) {
            $('#flatFeeAmount').val('');
            if ($('#flatFeeHourlySlider').length) {
                $('#flatFeeHourlySlider').val(15);
            }
        }
        if (currentTab === 'offer-fee-split' && $('#feeSplitAmountInput').length) {
            $('#feeSplitSlider').val(0);
            $('#feeSplitValue').text('0');
            $('#feeSplitAmountInput').val('');
            if ($('#feeSplitAmountTyped').length) {
                $('#feeSplitAmountTyped').val('');
            }
        }
        updateSummary();
        moveTab(1);
    });

    $('#backTabButton').on('click', function () {
        moveTab(-1);
    });

    $('#feeSplitSlider').on('input change', function () {
        setFeeSplitValue($(this).val());
        updateSummary();
        clearWarning();
    });

    $('#feeSplitAmountTyped').on('input change', function () {
        setFeeSplitValue($(this).val());
        updateSummary();
        clearWarning();
    });

    $('#flatFeeAmount').on('input change', function () {
        if ($('#flatFeeHourlySlider').length && $(this).val() !== '') {
            const typedValue = parseFloat($(this).val());
            if (!Number.isNaN(typedValue) && typedValue >= 15 && typedValue <= 1000) {
                $('#flatFeeHourlySlider').val(typedValue);
            }
        }
        updateSummary();
        clearWarning();
    });

    $('#flatFeeHourlySlider').on('input change', function () {
        setFlatFeeValue($(this).val());
        updateSummary();
        clearWarning();
    });

    $('#confirmBidButton').on('click', function (event) {
        clearWarning();
        if (!isValidFlatFeeOffer() && !isValidFeeSplitOffer()) {
            event.preventDefault();
            showWarning('danger', 'You must enter at least one offer before confirming.');
        }
    });

    $.ajax({
        type: 'GET',
        url: '/auction/data/view_auction_data',
        data: {
            auctionID: auctionID
        },
        success: function (response) {
            currentLowBid = response.currentLowBid;
            auctionEnd = new Date(response.auctionEnd);
            reservePrice = response.reservePrice;
            paymentType = response.paymentType;
            paymentTypes = response.paymentTypes || [];
            minBidIncrement = response.minimumBidIncrement;
            isAuctionActive = !!response.active;

            if (isAuctionActive) {
                const currentTime = new Date().getTime();
                const subtractMilliSecondsValue = auctionEnd.getTime() - currentTime;
                setTimeout(auctionEnded, subtractMilliSecondsValue);
            }

            if ($('#feeSplitSlider').length) {
                const feeSplitStart = 0;
                setFeeSplitValue(feeSplitStart);
            }

            if ($('#flatFeeHourlySlider').length) {
                $('#flatFeeHourlySlider').val(15);
                if (($('#flatFeeAmount').val() || '').trim() !== '') {
                    setFlatFeeValue($('#flatFeeAmount').val());
                }
            }

            const tabs = enabledOfferTabs();
            if (tabs.length > 0) {
                activateOfferTab(tabs[0]);
            }
        },
        error: function (error) {
            console.log('error: ', error);
        }
    });

    function auctionEnded() {
        $('#bidButton').hide();
        $('#exampleModal').modal('hide');
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
            if (isAuctionActive) {
                countDown(auctionEndDateTime, auctionID);
            }

            if (response.data.practice_area_valid) {
                $('#demographicAOPDiv').removeClass('d-none');
            }
            else {
                $('#demographicsOnlyDiv').removeClass('d-none');
            }

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

            if (response.data.practice_area_valid) {
                const demographics = new Chart(
                    document.getElementById('demographics'),
                    config
                );
            }
            else {
                const demographics = new Chart(
                    document.getElementById('demographicsOnly'),
                    config
                );
            }


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

})();