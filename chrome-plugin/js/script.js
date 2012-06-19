function error(str) {
    $("#error-msg").text(str);
}

// geolocation
function get_location() {
    function loc_success(position) {
        // maybe find the general city?
        //alert([position.coords.latitude, position.coords.longitude]);
        $("#loc_lat").val(position.coords.latitude);
        $("#loc_long").val(position.coords.longitude);
    }
    function loc_error(msg) {
        error("Sorry, couldn't fetch your location");
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(loc_success, loc_error);
    } else {
        alert('not supported');
        error('not supported');
    }
}

var pensievr_url = "http://pensievr.appspot.com/";

$(document).ready(function() {
    get_location();

    // auto-focus on the text field
    if(document.post_form)
        document.post_form.post.focus();

    // restore from localStorage
    if(localStorage.cpost)
        $("#post").val(JSON.parse(localStorage.cpost));
    // save to localStorage
    $("#post").change(function(e){
        localStorage.cpost = JSON.stringify($("#post").val());
    });
    $("#post_form").submit(function(e){
        var d = {
            loc_lat: $("#loc_lat").val(),
            loc_long: $("#loc_lat").val(),
            time: $("#time").val(),
            post: $("#post").val()
        };
        localStorage.cpost = undefined;
        $("#post").val("");
        $.ajax({
            url: pensievr_url + "post",
            data: d
        });
        e.preventDefault();
        return false;
    });
});
