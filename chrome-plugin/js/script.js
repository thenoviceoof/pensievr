// auto-focus on the text field
if(document.post_form)
    document.post_form.post.focus();

// geolocation
function get_location() {
    function loc_success(position) {
        alert([position.coords.latitude, position.coords.longitude]);
        $("#loc_lat").val(position.coords.latitude);
        $("#loc_long").val(position.coords.longitude);
    }
    function loc_error(msg) {
        alert("Sorry, couldn't fetch your location");
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(loc_success, loc_error);
    } else {
        alert('not supported');
        error('not supported');
    }
}

$(document).ready(function() {
    get_location();
}
