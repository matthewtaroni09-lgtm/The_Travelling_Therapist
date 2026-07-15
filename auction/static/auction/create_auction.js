const currencyFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

let feeSplitCalcShown = false;
let assessmentChecked = false;
let treatmentChecked = false;
let dynamicSkillCounter = 100;
let dynamicPerkCounter = 200;

const REQUIRED_SKILLS_BY_TYPE = {
    physio: [
        'Canadian Physiotherapy License',
        'PT Resident',
        'Physiotherapy Insurance',
        'First Aid/CPR/AED',
        'Digital/Software Based Charting',
        'AI Charting',
        'Working with a PTA/Rehab Assistant Experience',
        'Outpatient & Community Experience',
        'Hospital/Long Term Care/Retirement Home Experience',
        'Home care Experience',
        'Virtual Care Experience',
        'Orthopedics Experience',
        'Neurological Experience',
        'Cardiorespiratory Experience',
        'Sports Experience',
        "Women's Health & Pelvic Health Experience",
        'Acupuncture',
        'Spinal Manipulation',
        'Pelvic Internal Examination',
        'Wound Care',
        'Tracheal Suctioning',
        'Administering a Substance by Inhalation',
    ],
    pta: [
        'Diploma/Degree in PTA/OTA/Rehab Assistant',
        'Kinesiology Degree',
        'Kinesiologist Certification',
        'Personal Trainer Certification',
        'Practice Insurance',
        'First Aid/CPR/AED',
        'Digital/Software Based Charting',
        'AI Charting',
        'Working with a PT Experience',
        'Working with an OT Experience',
        'Outpatient & Community Experience',
        'Hospital/Long Term Care/Retirement Home Experience',
        'Home care Experience',
        'Virtual Care Experience',
        'Orthopedics Experience',
        'Neurological Experience',
        'Cardiorespiratory Experience',
        'Geriatrics Experience',
        'Sports Experience',
        "Women's Health & Pelvic Health Experience",
    ],
    rmt: [
        'Canadian Registered Massage Therapy License',
        'Massage Therapy Insurance',
        'First Aid/CPR/AED',
        'Digital/Software Based Charting',
        'AI Charting',
        'Outpatient & Community Experience',
        'Hospital/Long Term Care/Retirement Home',
        'Home care Experience',
        'Orthopedics Experience',
        'Sports Experience',
        "Women's Health & Pelvic Health Experience",
        'Acupuncture',
    ],
    default: [
        'Canadian License to Practice',
        'Practice Insurance',
        'First Aid/CPR/AED',
        'Hospital/Long Term Care/Retirement Home',
        'Home care Experience',
        'Orthopedics Experience',
        'Sports Experience',
        "Women's Health & Pelvic Health Experience",
    ],
};

const NON_REGULATED_TYPE_KEYWORDS = [
    'dietary aide',
    'pta',
    'ota',
    'rehab assistant',
    'psw',
    'recreation therapist',
    'dental assistant',
];

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function getSelectedClinicianTypeLabel() {
    const $type = $('#id_type');
    if ($type.length === 0) {
        return '';
    }

    const value = ($type.val() || '').trim();
    if (!value || value === '0') {
        return '';
    }

    return ($type.find(':selected').text() || '').trim();
}

function resolveClinicianSkillKey(typeLabel) {
    const normalized = (typeLabel || '').toLowerCase();

    if (normalized.includes('physio') || normalized.includes('physiotherapist') || normalized.includes('physiotherapy')) {
        return 'physio';
    }
    if (
        normalized.includes('pta')
        || normalized.includes('ota')
        || normalized.includes('rehab assistant')
        || normalized.includes('rehab assis')
        || normalized.includes('rehab ass')
    ) {
        return 'pta';
    }
    if (
        normalized.includes('rmt')
        || normalized.includes('massage therapist')
        || normalized.includes('registered massage')
        || normalized.includes('massage therapy')
    ) {
        return 'rmt';
    }

    return 'default';
}

function shouldIncludeLicenseSkill(typeLabel) {
    const normalized = (typeLabel || '').toLowerCase();
    return !NON_REGULATED_TYPE_KEYWORDS.some(function (keyword) {
        return normalized.includes(keyword);
    });
}

function buildStandardSkillRow(name, index) {
    const safeName = escapeHtml(name);
    const radioName = `skill_req_${index}`;
    const requiredId = `${radioName}_required`;
    const preferredId = `${radioName}_preferred`;

    return `
        <div class="ttt-grid-row" data-item-name="${safeName}">
            <label><input type="checkbox" class="form-check-input ttt-grid-check"> ${safeName}</label>
            <div class="ttt-grid-toggle" role="group" aria-label="${safeName} requirement">
                <input type="radio" class="btn-check" name="${radioName}" id="${requiredId}" checked>
                <label class="btn btn-sm btn-outline-secondary" for="${requiredId}">Required</label>
                <input type="radio" class="btn-check" name="${radioName}" id="${preferredId}">
                <label class="btn btn-sm btn-outline-secondary" for="${preferredId}">Preferred</label>
            </div>
        </div>
    `;
}

function populateRequiredSkillsByClinicianType() {
    const $container = $('#requiredSkillsContainer');
    if ($container.length === 0) {
        return;
    }

    const $gridHead = $container.find('.ttt-grid-head');
    const $gridList = $container.find('.ttt-grid-list');
    const $addRow = $container.find('.ttt-add-row');
    const $prompt = $('#requiredSkillsTypePrompt');
    const typeLabel = getSelectedClinicianTypeLabel();

    if (!typeLabel) {
        $gridList.empty().addClass('d-none');
        $gridHead.addClass('d-none');
        $addRow.addClass('d-none');
        $prompt.removeClass('d-none');
        syncNegotiablePayloads();
        return;
    }

    const skillKey = resolveClinicianSkillKey(typeLabel);
    let skillRows = REQUIRED_SKILLS_BY_TYPE[skillKey] || REQUIRED_SKILLS_BY_TYPE.default;
    if (skillKey === 'default' && !shouldIncludeLicenseSkill(typeLabel)) {
        skillRows = skillRows.filter(function (name) {
            return name !== 'Canadian License to Practice';
        });
    }
    const markup = skillRows.map(function (itemName, i) {
        return buildStandardSkillRow(itemName, i + 1);
    }).join('');

    $gridList.html(markup).removeClass('d-none');
    $gridHead.removeClass('d-none');
    $addRow.removeClass('d-none');
    $prompt.addClass('d-none');

    syncAllGridRowsAvailability();
    syncNegotiablePayloads();
}

    function initializeTooltips(root) {
        const targetRoot = root || document;
        const tooltipTargets = targetRoot.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTargets.forEach(function (el) {
            bootstrap.Tooltip.getOrCreateInstance(el);
        });
    }

function buildCustomGridRow(name, kind, index) {
    const safeName = escapeHtml(name);
    if (kind === 'perk') {
        const perkId = `${kind}_custom_${index}`;
        return `
        <div class="ttt-grid-row" data-item-name="${safeName}" data-custom-item="true">
            <span class="ttt-grid-item-label">${safeName}</span>
            <div class="d-flex align-items-center gap-2">
                <div class="ttt-perk-switch-wrap">
                    <div class="form-check form-switch">
                        <input type="checkbox" class="form-check-input ttt-perk-switch" role="switch" aria-label="Custom perk included" checked>
                    </div>
                </div>
                <button type="button" class="ttt-perk-expand-toggle" aria-expanded="true" aria-controls="${perkId}_details" aria-label="Toggle custom perk details">
                    <span class="material-icons ttt-perk-expand-icon">chevron_right</span>
                </button>
                <button type="button" class="ttt-remove-item" aria-label="Remove custom ${kind}">Remove</button>
            </div>
        </div>
        <div class="ttt-perk-detail-panel" id="${perkId}_details">
            <div class="row g-2 align-items-end">
                <div class="col-sm-4">
                    <label class="form-label form-label-sm mb-1 ttt-perk-detail-label-wrap">
                        <span class="ttt-perk-detail-label">Amount <span class="text-muted">(optional)</span></span>
                        <button type="button" class="ttt-info-dot-sm" data-bs-toggle="tooltip" data-bs-placement="top" title="Amounts are hidden on public listings and shown only to clinicians in the offer finalization step." aria-label="Perk amount info">i</button>
                    </label>
                    <div class="input-group input-group-sm">
                        <span class="input-group-text">$</span>
                        <input type="number" min="0" class="form-control ttt-perk-amount" placeholder="0">
                    </div>
                </div>
                <div class="col-sm-8">
                    <label class="form-label form-label-sm mb-1 ttt-perk-detail-label">Additional details <span class="text-muted">(optional)</span></label>
                    <input type="text" class="form-control form-control-sm ttt-perk-details" placeholder="Example: up to $1,500 after 3 months">
                </div>
            </div>
        </div>
        `;
    }

    const radioPrefix = `${kind}_custom_req_${index}`;
    return `
        <div class="ttt-grid-row" data-item-name="${safeName}" data-custom-item="true">
            <label><input type="checkbox" class="form-check-input ttt-grid-check" checked> <span>${safeName}</span></label>
            <div class="d-flex align-items-center gap-2">
                <div class="ttt-grid-toggle" role="group" aria-label="Custom ${kind} requirement">
                    <input type="radio" class="btn-check" name="${radioPrefix}" id="${radioPrefix}_required" checked>
                    <label class="btn btn-sm btn-outline-secondary" for="${radioPrefix}_required">Required</label>
                    <input type="radio" class="btn-check" name="${radioPrefix}" id="${radioPrefix}_preferred">
                    <label class="btn btn-sm btn-outline-secondary" for="${radioPrefix}_preferred">Preferred</label>
                </div>
                <button type="button" class="ttt-remove-item" aria-label="Remove custom ${kind}">Remove</button>
            </div>
        </div>
    `;
}

function serializeGridRows(containerId) {
    const rows = [];
    $(`#${containerId} .ttt-grid-list > .ttt-grid-row`).each(function () {
        const $row = $(this);
        const itemName = ($row.attr('data-item-name') || '').trim();
        if (!itemName) {
            return;
        }
        const isPerkRow = $row.find('.ttt-perk-switch').length > 0;
        const selected = isPerkRow ? $row.find('.ttt-perk-switch').is(':checked') : $row.find('.ttt-grid-check').is(':checked');
        const requirement = isPerkRow ? '' : $row.find('.ttt-grid-toggle input[type="radio"]:checked').next('label').text().trim();
        const $detailPanel = isPerkRow ? $row.next('.ttt-perk-detail-panel') : null;
        const amountRaw = isPerkRow && $detailPanel && $detailPanel.length ? ($detailPanel.find('.ttt-perk-amount').val() || '').trim() : '';
        const details = isPerkRow && $detailPanel && $detailPanel.length ? ($detailPanel.find('.ttt-perk-details').val() || '').trim() : '';
        rows.push({
            name: itemName,
            selected: selected,
            included: selected,
            requirement: isPerkRow ? null : (requirement || 'Required'),
            amount: isPerkRow ? (amountRaw === '' ? 0 : parseInt(amountRaw, 10) || 0) : null,
            details: isPerkRow ? details : '',
            custom: $row.attr('data-custom-item') === 'true',
        });
    });
    return rows;
}

function syncNegotiablePayloads() {
    const skillsPayload = serializeGridRows('requiredSkillsContainer');
    const perksPayload = serializeGridRows('negotiablePerksContainer');
    $('#id_requiredSkillsPayload').val(JSON.stringify(skillsPayload));
    $('#id_negotiablePerksPayload').val(JSON.stringify(perksPayload));
}

function syncGridRowAvailability($row) {
    if ($row.find('.ttt-grid-check').length === 0) {
        return;
    }

    const isChecked = $row.find('.ttt-grid-check').is(':checked');
    const $toggle = $row.find('.ttt-grid-toggle');
    const $radios = $toggle.find('input[type="radio"]');
    $radios.prop('disabled', !isChecked);
    $toggle.toggleClass('is-disabled', !isChecked);
}

function syncAllGridRowsAvailability() {
    $('.ttt-grid-list .ttt-grid-row').each(function () {
        syncGridRowAvailability($(this));
    });
}

function syncPerkDetailPanel($row, animate) {
    const $switch = $row.find('.ttt-perk-switch');
    if ($switch.length === 0) {
        return;
    }

    const shouldAnimate = animate === true;
    const isIncluded = $switch.is(':checked');
    const $detailPanel = $row.next('.ttt-perk-detail-panel');
    const $toggle = $row.find('.ttt-perk-expand-toggle');

    if ($detailPanel.length > 0) {
        $detailPanel.stop(true, true);
        if (isIncluded) {
            $detailPanel.removeClass('d-none');
            if (shouldAnimate) {
                $detailPanel.slideDown(180);
            }
            else {
                $detailPanel.show();
            }
        }
        else {
            if (shouldAnimate) {
                $detailPanel.slideUp(180, function () {
                    $detailPanel.addClass('d-none');
                });
            }
            else {
                $detailPanel.hide().addClass('d-none');
            }
        }

        if (!isIncluded) {
            $detailPanel.find('.ttt-perk-amount').val('');
            $detailPanel.find('.ttt-perk-details').val('');
        }
    }

    if ($toggle.length > 0) {
        $toggle.prop('disabled', !isIncluded);
        $toggle.toggleClass('is-disabled', !isIncluded);
        $toggle.attr('aria-expanded', isIncluded ? 'true' : 'false');
    }
}

function syncAllPerkDetailPanels() {
    $('#negotiablePerksContainer .ttt-grid-list > .ttt-grid-row').each(function () {
        syncPerkDetailPanel($(this), false);
    });
}

function addCustomGridItem(containerId) {
    const $container = $(`#${containerId}`);
    const $input = $(`[data-custom-input="${containerId}"]`);
    const rawValue = ($input.val() || '').trim();
    if (!rawValue) {
        return;
    }
    const kind = containerId === 'requiredSkillsContainer' ? 'skill' : 'perk';
    const nextIndex = kind === 'skill' ? dynamicSkillCounter++ : dynamicPerkCounter++;
    $container.find('.ttt-grid-list').append(buildCustomGridRow(rawValue, kind, nextIndex));
    const $lastRow = $container.find('.ttt-grid-list > .ttt-grid-row').last();
    syncGridRowAvailability($lastRow);
    syncPerkDetailPanel($lastRow, false);
    initializeTooltips($container[0]);
    $input.val('');
    syncNegotiablePayloads();
}

function getSelectedPaymentTypes() {
    return $('input[name="paymentTypesSelection"]:checked').map(function () {
        return $(this).val();
    }).get();
}

function getSelectedFlatFeeType() {
    return $('input[name="flatFeeType"]:checked').val() || '';
}

function syncOfferGuidanceUI(selectedPaymentTypes) {
    const flatFeeType = getSelectedFlatFeeType();
    const showFeeSplitGuidance = selectedPaymentTypes.includes('Fee Split');
    const showHourlyGuidance = selectedPaymentTypes.includes('Flat Fee') && flatFeeType === 'hourly';
    const showTotalGuidance = selectedPaymentTypes.includes('Flat Fee') && flatFeeType === 'total_contract';

    $('#desiredFeeSplitContainer').toggleClass('d-none', !showFeeSplitGuidance);
    $('#flatFeeGuidanceContainer').toggleClass('d-none', !(showHourlyGuidance || showTotalGuidance));
    $('#desiredFlatFeeHourlyContainer').toggleClass('d-none', !showHourlyGuidance);
    $('#desiredFlatFeeTotalContainer').toggleClass('d-none', !showTotalGuidance);

    if (!showFeeSplitGuidance) {
        $('#id_desiredFeeSplitPercentage').val('');
        $('#id_minimumCompensation').val('');
    }
    if (!showHourlyGuidance) {
        $('#id_desiredFlatFeeHourly').val('');
    }
    if (!showTotalGuidance) {
        $('#id_desiredFlatFeeTotalContract').val('');
    }
}

function syncPaymentTypeUI() {
    const selectedPaymentTypes = getSelectedPaymentTypes();
    const feeSplitEnabled = selectedPaymentTypes.includes('Fee Split');
    const flatFeeEnabled = selectedPaymentTypes.includes('Flat Fee');
    const paymentTypeSelected = selectedPaymentTypes.length > 0;

    greyOutFields(!paymentTypeSelected);

    if (flatFeeEnabled) {
        $('#flatFeeTypeContainer').removeClass('d-none');
    }
    else {
        $('#flatFeeTypeContainer').addClass('d-none');
        $('input[name="flatFeeType"]').prop('checked', false);
    }

    syncOfferGuidanceUI(selectedPaymentTypes);

    if (feeSplitEnabled) {
        greyOutFields(false);
    }
    else {
        /* Deprecated fee split minimums UI retained in source for reference.
        $('#assessmentCheckBoxDiv').addClass('d-none');
        $('#treatmentCheckBoxDiv').addClass('d-none');
        $('#assessmentTreatmentInfoDiv').addClass('d-none');
        $('.assessmentField').addClass('d-none');
        $('.treatmentField').addClass('d-none');
        $('.feeSplitCalcFields').addClass('d-none');
        $('#assessmentCheckBox').prop('checked', false);
        $('#treatmentCheckBox').prop('checked', false);
        assessmentChecked = false;
        treatmentChecked = false;
        $('#id_assessmentCost').val('');
        $('#id_assessmentMin').val('');
        $('#id_treatmentMin').val('');
        $('#id_treatmentCost').val('');
        calculateDailyMin();
        */
    }
}

$(document).ready(function () {
    $('.alert.alert-block.alert-danger').hide();
    $('.feeSplitFields').hide();
    greyOutFields(true);
    // Prevent pressing enter from submitting the form
    $(document).keypress(
        function (event) {
            if (event.which == '13') {
                event.preventDefault();
            }
        });

    $('#id_type').change(function () {
        populateRequiredSkillsByClinicianType();

        if ($('#id_type').find(":selected").text() != '---------') {
            $('#practiceAreaCheckBoxDiv').removeClass('d-none');
            $("#optionsMessage").hide();

            if ($("#practiceAreaCheckBox").is(':checked')) {
                $('#practiceAreaDiv').hide();
                $('#practiceAreaCheckBox').prop('checked', false);
            }

            syncPaymentTypeUI();

            $.ajax({
                type: "GET",
                url: "/auction/data/check_user_payment_type",
                data: {
                    'name': $('#id_type').find(":selected").text()
                },
                success: function (response) {
                    console.log(response);
                    $('#id_paymentTypesSelection_0').prop('disabled', false);
                    syncPaymentTypeUI();

                },
                error: function (error) {
                    console.log('error: ', error);
                }
            });
        }
        else {
            $("#optionsMessage").hide();
            $('input[name="paymentTypesSelection"]').prop('checked', false).prop('disabled', false);
            syncPaymentTypeUI();
        }
    });

    $('input[name="paymentTypesSelection"]').change(function () {
        syncPaymentTypeUI();
    });

    $('input[name="flatFeeType"]').change(function () {
        syncOfferGuidanceUI(getSelectedPaymentTypes());
    });

    $('.ttt-add-trigger').on('click', function () {
        addCustomGridItem($(this).data('grid-target'));
    });

    $('[data-custom-input]').on('keypress', function (event) {
        if (event.which === 13) {
            event.preventDefault();
            addCustomGridItem($(this).data('custom-input'));
        }
    });

    $(document).on('click', '.ttt-remove-item', function () {
        const $row = $(this).closest('.ttt-grid-row');
        const $detailPanel = $row.next('.ttt-perk-detail-panel');
        if ($detailPanel.length > 0) {
            $detailPanel.remove();
        }
        $row.remove();
        syncNegotiablePayloads();
    });

    $(document).on('change', '.ttt-grid-check', function () {
        syncGridRowAvailability($(this).closest('.ttt-grid-row'));
        syncNegotiablePayloads();
    });

    $(document).on('change', '.ttt-grid-toggle input[type="radio"]', function () {
        syncNegotiablePayloads();
    });

    $(document).on('change', '.ttt-perk-switch', function () {
        syncPerkDetailPanel($(this).closest('.ttt-grid-row'), true);
        syncNegotiablePayloads();
    });

    $(document).on('click', '.ttt-perk-expand-toggle', function () {
        const $row = $(this).closest('.ttt-grid-row');
        const $panel = $row.next('.ttt-perk-detail-panel');
        if ($panel.length === 0 || $(this).prop('disabled')) {
            return;
        }
        const isExpanded = $(this).attr('aria-expanded') === 'true';
        $panel.stop(true, true);
        if (isExpanded) {
            $panel.slideUp(180, function () {
                $panel.addClass('d-none');
            });
        }
        else {
            $panel.removeClass('d-none').hide().slideDown(180);
        }
        $(this).attr('aria-expanded', isExpanded ? 'false' : 'true');
    });

    $(document).on('input', '.ttt-perk-amount, .ttt-perk-details', function () {
        syncNegotiablePayloads();
    });

    //Show assessment fields checkbox
    $('#assessmentCheckBox').change(function () {
        if (this.checked) {
            $('.assessmentField').removeClass('d-none');
            $('.feeSplitCalcFields').removeClass('d-none');
            assessmentChecked = true;
        }
        else {
            $('.assessmentField').addClass('d-none');
            $('#id_assessmentCost').val('');
            $('#id_assessmentMin').val('');
            calculateDailyMin();
            assessmentChecked = false;
            // If treatment check and assessment check are both unchecked then hide the calculated fields
            if (!treatmentChecked) {
                $('.feeSplitCalcFields').addClass('d-none');
            }
        }
    });

    //Show treatment fields checkbox
    $('#treatmentCheckBox').change(function () {
        if (this.checked) {
            $('.treatmentField').removeClass('d-none');
            $('.feeSplitCalcFields').removeClass('d-none');
            treatmentChecked = true;
        }
        else {
            $('.treatmentField').addClass('d-none');
            $('#id_treatmentCost').val('');
            $('#id_treatmentMin').val('');
            calculateDailyMin();
            treatmentChecked = false;
            // If treatment check and assessment check are both unchecked then hide the calculated fields
            if (!assessmentChecked) {
                $('.feeSplitCalcFields').addClass('d-none');
            }
        }
    });

    $('#id_treatmentCost, #id_treatmentMin, #id_assessmentCost, #id_assessmentMin').change(function () {
        // If a negative number is entered blank out that input
        if ($(this).val() < 0) {
            $(this).val('');
        }

        calculateDailyMin();
    });

    // Prevent decimal numbers from being added to the number of treatments/assessments
    $('#id_treatmentMin, #id_assessmentMin').on('keyup', function (e) {
        if (e.which === 46) return false;
    }).on('input', function () {
        var self = this;
        setTimeout(function () {
            if (self.value.indexOf('.') != -1) self.value = parseInt(self.value, 10);
        }, 0);
    });

    $('[id^=id_demogrpahic_auction-]').each(function (i, el) {
        if ($(this).is('select')) {
            $(this).attr("disabled", true);
            $(this).val(parseInt($(this).attr('id').match(/\d/)[0]) + 1);
        }
        else if ($(this).is('input') && $(this).attr('type') === "hidden" && $(this).val().indexOf('-') >= 0) {
            $(this).val('');
        }
    });

    $('[id^=id_practice_area_auction-]').each(function (i, el) {
        if ($(this).is('select')) {
            $(this).attr("disabled", true);
        }
        else if ($(this).is('input') && $(this).attr('type') === "hidden" && $(this).val().indexOf('-') >= 0) {
            $(this).val('');
        }
    });

    $("#practiceAreaCheckBox").change(function () {
        if (this.checked) {
            $('#practiceAreaDiv').show();
        }
        else {
            $('#practiceAreaDiv').hide();
            $('#AOPOpen').text("Yes");
        }
    });

    //Clinic is not a selectable option. If the user selects clinic it will be picked automatically
    let clinicVal = '';
    $('#id_type option').each(function () {
        if ($(this).text() == 'Clinic') {
            clinicVal = $(this).val();
        }
    });
    $("#id_type option[value='" + clinicVal + "']").remove();

    syncPaymentTypeUI();
    populateRequiredSkillsByClinicianType();
    syncAllGridRowsAvailability();
    syncAllPerkDetailPanels();
    initializeTooltips(document);
    syncNegotiablePayloads();
});

$('#id_placementStart').change(function () {
    getDateDiff();
});
$('#id_placementEnd').change(function () {
    getDateDiff();
});
$('.clearButton').click(function () {
    $(this).parent().find('input[type=time]')[0].value = '';
    $(this).parent().find('input[type=time]')[1].value = '';
});

$('#priceInfoIcon').click(function () {
    popUps('priceInfoIcon');
});

$('#reservePriceInfoIcon').click(function () {
    popUps('reservePriceInfoIcon');
});

$('#assessmentTreatmentInfoIcon').click(function () {
    popUps('assessmentTreatmentInfoIcon');
});

$("#submitButton").click(function () {
    let errorList = '';
    syncNegotiablePayloads();

    if ($("#id_type").val() === "0") {
        errorList += "<li>Please select a clinician type.</li>";
    }

    if (getSelectedPaymentTypes().length === 0) {
        errorList += "<li>Please select a payment type.</li>";
    }

    if (getSelectedPaymentTypes().includes('Flat Fee') && getSelectedFlatFeeType() === "") {
        errorList += "<li>Please select how flat fee offers should be priced.</li>";
    }

    let placementStart = new Date($("#id_placementStart").val());
    let placementEnd = new Date($("#id_placementEnd").val());

    let mondayStart = '';
    let mondayEnd = '';
    let tuesdayStart = '';
    let tuesdayEnd = '';
    let wednesdayStart = '';
    let wednesdayEnd = '';
    let thursdayStart = '';
    let thursdayEnd = '';
    let fridayStart = '';
    let fridayEnd = '';
    let saturdayStart = '';
    let saturdayEnd = '';
    let sundayStart = '';
    let sundayEnd = '';

    //JS has not Time object so use the Date object with a dummy date
    if ($("#id_mondayStart").val() !== '') {
        mondayStart = new Date('1970-01-01T' + $("#id_mondayStart").val() + 'Z');
    }
    if ($("#id_mondayEnd").val() !== '') {
        mondayEnd = new Date('1970-01-01T' + $("#id_mondayEnd").val() + 'Z');
    }

    if ($("#id_tuesdayStart").val() !== '') {
        tuesdayStart = new Date('1970-01-01T' + $("#id_tuesdayStart").val() + 'Z');
    }
    if ($("#id_tuesdayEnd").val() !== '') {
        tuesdayEnd = new Date('1970-01-01T' + $("#id_tuesdayEnd").val() + 'Z');
    }

    if ($("#id_wednesdayStart").val() !== '') {
        wednesdayStart = new Date('1970-01-01T' + $("#id_wednesdayStart").val() + 'Z');
    }
    if ($("#id_wednesdayEnd").val() !== '') {
        wednesdayEnd = new Date('1970-01-01T' + $("#id_wednesdayEnd").val() + 'Z');
    }

    if ($("#id_thursdayStart").val() !== '') {
        thursdayStart = new Date('1970-01-01T' + $("#id_thursdayStart").val() + 'Z');
    }
    if ($("#id_thursdayEnd").val() !== '') {
        thursdayEnd = new Date('1970-01-01T' + $("#id_thursdayEnd").val() + 'Z');
    }

    if ($("#id_fridayStart").val() !== '') {
        fridayStart = new Date('1970-01-01T' + $("#id_fridayStart").val() + 'Z');
    }
    if ($("#id_fridayEnd").val() !== '') {
        fridayEnd = new Date('1970-01-01T' + $("#id_fridayEnd").val() + 'Z');
    }

    if ($("#id_saturdayStart").val() !== '') {
        saturdayStart = new Date('1970-01-01T' + $("#id_saturdayStart").val() + 'Z');
    }
    if ($("#id_saturdayEnd").val() !== '') {
        saturdayEnd = new Date('1970-01-01T' + $("#id_saturdayEnd").val() + 'Z');
    }

    if ($("#id_sundayStart").val() !== '') {
        sundayStart = new Date('1970-01-01T' + $("#id_sundayStart").val() + 'Z');
    }
    if ($("#id_sundayEnd").val() !== '') {
        sundayEnd = new Date('1970-01-01T' + $("#id_sundayEnd").val() + 'Z');
    }

    let noneCount = 0

    let demographicTotal = 0;
    let practiceTotal = 0;
    let demographicCategory = '';
    let practiceCategory = '';

    let treatmentCost = $('#id_treatmentCost').val();
    let treatmentMin = $('#id_treatmentMin').val();
    let assessmentCost = $('#id_assessmentCost').val();
    let assessmentMin = $('#id_assessmentMin').val();

    let costMax = 500;
    let sessionMax = 10;

    //Validate Start/End date
    var now = new Date();
    let oneYear = new Date(now);
    oneYear.setDate(now.getDate() + 365)

    if (days_between(placementStart, placementEnd, false) === 0) {
        errorList += '<li>The placement must be at least one day long.</li>';
    }
    else {
        if (days_between(placementStart, now, false) < 0) {
            errorList += '<li>Clinician Start Date cannot be in the past.</li>';
        }

        if (days_between(placementEnd, now, false) < 0) {
            errorList += '<li>Clinician End Date cannot be in the past.</li>';
        }
    }

    if (placementStart === NaN) {
        errorList += '<li>Please enter a valid Clinician Start Date.</li>';
    }
    if (placementEnd === NaN) {
        errorList += '<li>Please enter a valid Clinician End Date.</li>';
    }
    if (placementEnd < placementStart) {
        errorList += '<li>The Clinician End Date must be after the Clinician Start Date.</li>';
    }
    if (placementStart > oneYear) {
        errorList += '<li>Placements must start within the next 12 months.</li>';
    }
    if (days_between(placementStart, placementEnd, true) > 548) {
        errorList += '<li>Looks like you are trying to create an ad for an opening longer than 18 months! Please contact us to help you set this up.</li>';
    }

    let minimumCompensation = $('#id_minimumCompensation').val();

    // Validate optional minimum compensation for fee split listings.
    if (getSelectedPaymentTypes().includes('Fee Split')) {
        if (minimumCompensation !== '' && parseInt(minimumCompensation, 10) < 1) {
            errorList += '<li>Minimum compensation must be at least $1.</li>';
        }
    }

    /* Deprecated fee split assessment/treatment validation retained in source for reference.
    if (getSelectedPaymentTypes().includes('Fee Split')) {
        ...
    }
    */


    //Validate Therapist Schedule
    let mondayVal = check_times(mondayStart, mondayEnd, 'Monday');
    let tuesdayVal = check_times(tuesdayStart, tuesdayEnd, 'Tuesday');
    let wednesdayVal = check_times(wednesdayStart, wednesdayEnd, 'Wednesday');
    let thursdayVal = check_times(thursdayStart, thursdayEnd, 'Thursday');
    let fridayVal = check_times(fridayStart, fridayEnd, 'Friday');
    let saturdayVal = check_times(saturdayStart, saturdayEnd, 'Saturday');
    let sundayVal = check_times(sundayStart, sundayEnd, 'Sunday');

    if (mondayVal === 'None') {
        noneCount++;
    }
    else if (mondayVal != '' && mondayVal != 'None') {
        errorList += mondayVal;
    }

    if (tuesdayVal === 'None') {
        noneCount++;
    }
    else if (tuesdayVal != '' && tuesdayVal != 'None') {
        errorList += tuesdayVal;
    }

    if (wednesdayVal === 'None') {
        noneCount++;
    }
    else if (wednesdayVal != '' && wednesdayVal != 'None') {
        errorList += wednesdayVal;
    }

    if (thursdayVal === 'None') {
        noneCount++;
    }
    else if (thursdayVal != '' && thursdayVal != 'None') {
        errorList += thursdayVal;
    }

    if (fridayVal === 'None') {
        noneCount++;
    }
    else if (fridayVal != '' && fridayVal != 'None') {
        errorList += fridayVal;
    }

    if (saturdayVal === 'None') {
        noneCount++;
    }
    else if (saturdayVal != '' && saturdayVal != 'None') {
        errorList += saturdayVal;
    }

    if (sundayVal === 'None') {
        noneCount++;
    }
    else if (sundayVal != '' && sundayVal != 'None') {
        errorList += sundayVal;
    }

    //All day's have been left blank
    if (noneCount === 7) {
        errorList += "<li>You're trying to create a posting, but you've left the Clinician schedule blank.  This would indicate to bidding Clinicians that they have a start and end date, but no days to actual be at your healthcare facility. Please complete at least 1 day showing the start and end time for the Clinician before you can submit your listing.</li>";
    }

    //Validate Demographics
    $('[id^=id_demogrpahic_auction-]').each(function (i, el) {
        if ($(this).is('select')) {
            demographicCategory = $(this).find(":selected").text();
        }
        if ($(this).attr('type') === 'number') {
            if ($(this).val() === '') {
                errorList += '<li>Please enter a value for ' + demographicCategory + '.</li>';
            }
            else if (parseInt($(this).val()) > 100) {
                errorList += '<li>' + demographicCategory + ' must be less than 100%.</li>';
            }
            else if (parseInt($(this).val()) < 0) {
                errorList += '<li>' + demographicCategory + ' cannot be negative.</li>';
            }
            demographicTotal += parseInt($(this).val());
        }
    });
    if (demographicTotal !== 100) {
        errorList += '<li>Demographic percentages must add up to 100%.</li>';
    }

    //Validate Areas of Practice
    if ($("#practiceAreaCheckBox").is(':checked')) {
        $('[id^=id_practice_area_auction-]').each(function (i, el) {
            if ($(this).is('select')) {
                practiceCategory = $(this).find(":selected").text();
            }
            if ($(this).attr('type') === 'number') {
                if ($(this).val() === '') {
                    errorList += '<li>Please enter a value for ' + practiceCategory + '.</li>';
                }
                else if (parseInt($(this).val()) > 100) {
                    errorList += '<li>' + practiceCategory + ' must be less than 100%.</li>';
                }
                else if (parseInt($(this).val()) < 0) {
                    errorList += '<li>' + practiceCategory + ' cannot be negative.</li>';
                }
                practiceTotal += parseInt($(this).val());
            }
        });
        if (practiceTotal !== 100) {
            errorList += '<li>Practice area percentages must add up to 100%.</li>';
        }
        console.log(practiceTotal);
        console.log(errorList);
        $('#AOPPopulated').val("Yes");
    }

    if (errorList !== '') {
        $('.alert.alert-block.alert-danger').show();
        $('#errorList').html(errorList);
        window.scrollTo(0, 0);
        return false;
    }
    //Django cannot get the values from disabled fields so re-enabled them on submit
    $("form :disabled").removeAttr('disabled');
});

function greyOutFields(val) {
    $("#id_placementStart, #id_placementEnd, #id_demogrpahic_auction-0-percentage, #id_demogrpahic_auction-1-percentage, #id_demogrpahic_auction-2-percentage").attr("disabled", val);
}

function calculateDailyMin() {
    let treatmentCost = $('#id_treatmentCost').val();
    let treatmentMin = $('#id_treatmentMin').val();
    let assessmentCost = $('#id_assessmentCost').val();
    let assessmentMin = $('#id_assessmentMin').val();
    let dailyMin = 0;
    let userType = '';

    if ((treatmentCost !== '' && treatmentMin !== '') || (assessmentCost !== '' && assessmentMin !== '')) {
        if ($('#id_type').find(":selected").text() === '---------') {
            userType = 'position: ';
        }
        else {
            userType = $('#id_type').find(":selected").text();
        }
        if ($('#assessmentCheckBox').prop('checked') == true && $('#treatmentCheckBox').prop('checked') == true && (treatmentCost !== '' && treatmentMin !== '' && assessmentCost !== '' && assessmentMin !== '')) {
            dailyMin = (parseFloat(treatmentCost) * parseFloat(treatmentMin)) + (parseFloat(assessmentCost) * parseFloat(assessmentMin));
        }
        else if ($('#assessmentCheckBox').prop('checked') == true && $('#treatmentCheckBox').prop('checked') == false) {
            dailyMin = parseFloat(assessmentCost) * parseFloat(assessmentMin);
        }
        else if ($('#assessmentCheckBox').prop('checked') == false && $('#treatmentCheckBox').prop('checked') == true) {
            dailyMin = parseFloat(treatmentCost) * parseFloat(treatmentMin);
        }
        if (dailyMin <= 0) {
            $('#dailyMinimum').text('Daily Minimum paid to your temporary position: $-');
        }
        else {
            $('#dailyMinimum').text('Daily Minimum paid to your temporary ' + userType + '  : ' + currencyFormatter.format(dailyMin));
        }
    }
    else {
        $('#dailyMinimum').text('Daily Minimum paid to your temporary position: $-');
    }
}

function getDateDiff() {
    let start = "";
    let end = "";
    let startDate = "";
    let endDate = "";
    let contractCost = 0

    if ($('#id_placementStart')[0].value != "") {
        start = $('#id_placementStart')[0].value.split("-");
        startDate = new Date(start[0], start[1] - 1, start[2]);
    }

    if ($('#id_placementEnd')[0].value != "") {
        end = $('#id_placementEnd')[0].value.split("-");
        endDate = new Date(end[0], end[1] - 1, end[2]);
    }

    let dateDiff = days_between(startDate, endDate, true);
    // if (dateDiff < 30) {
    //     $("#id_payFrequency option[value='3']").remove();
    // }
    // else {
    //     let monthlyPresent = false;
    //     $("#id_payFrequency > option").each(function () {
    //         if (this.text == "Monthly") {
    //             monthlyPresent = true;
    //         }
    //     });
    //     if (!monthlyPresent) {
    //         $('#id_payFrequency').append($('<option>', {
    //             value: 3,
    //             text: "Monthly"
    //         }));
    //     }
    // }
    if (endDate > startDate) {
        if (dateDiff * 25 < 300) {
            contractCost = 300;
        }
        else if (dateDiff * 25 > 5000) {
            contractCost = 5000;
        }
        else {
            contractCost = dateDiff * 25;
        }
        $('#contractCost').text('Contract price if matched: ' + currencyFormatter.format(contractCost) + ' + HST');
    }
}

function popUps(id) {
    let page = $("#pageTitle").text();
    $.ajax({
        type: "GET",
        url: "/auction/data/get_popups",
        data: {
            'page': page,
            'clickID': id
        },
        success: function (response) {
            console.log(response);
            if (response.message != "") {
                $("#modalTitle").text(response.title);
                $("#modalParagraph").html(response.message);
                $("#popupModal").modal('show');
            }
        },
        error: function (error) {
            console.log('error: ', error);
        }
    });
}

function check_times(start_time, end_time, day) {
    if ((start_time === '' && end_time !== '') || (start_time !== '' && end_time === '')) {
        return "<li>Please ensure that the start and end times are completed for " + day + ". If this is not a working day please remove both start and end times.</li>";
    }
    else if (start_time !== '' && end_time !== '') {
        if (start_time >= end_time) {
            return "<li>" + day + "'s start time is after the end time.</li>";
        }
        else {
            return '';
        }
    }
    else if (start_time === '' && end_time === '') {
        return 'None';
    }
    else {
        return ''
    }
}

function days_between(date1, date2, abs) {
    // The number of milliseconds in one day
    const ONE_DAY = 1000 * 60 * 60 * 24;
    let differenceMs = '';
    if (abs) {
        // Calculate the difference in milliseconds
        differenceMs = Math.abs(date1 - date2);
    }
    else {
        differenceMs = date1 - date2;
    }

    // Convert back to days and return
    return Math.round(differenceMs / ONE_DAY);

}