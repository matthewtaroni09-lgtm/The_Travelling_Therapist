$(document).ready(function () {
    let check = window.location.href.indexOf('#');
    if (check >= 0) {
        let split = window.location.href.split('#');
        // Use heading L to prevent over shooting
        if (split[1] == 'headingL') {
            $("#collapseN").collapse('toggle');
        }
    }
});