$(document).ready(function () {
    $('.clearButton').click(function () {
        $(this).parent().find('input[type=time]')[0].value = ''
        $(this).parent().find('input[type=time]')[1].value = ''
    });
});