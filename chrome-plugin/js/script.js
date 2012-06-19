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

function save() {
    localStorage.cpost = JSON.stringify($("#post").val());
}

$(document).ready(function() {
    get_location();

    // dismissal keycombo
    $(document).keydown(function(e){
        if(e.ctrlKey && e.keyCode == 103) {
            alert('mu');
        }
    });

    // auto-focus on the text field
    function autofocus() {
        if(document.post_form)
            document.post_form.post.focus();
    }
    autofocus();

    // restore from localStorage
    if(localStorage.cpost)
        $("#post").val(JSON.parse(localStorage.cpost));
    // save to localStorage
    $("#post").change(save).bind('keyup', save);

    $("#post_form").submit(function(e){
        var d = {
            loc_lat: $("#loc_lat").val(),
            loc_long: $("#loc_lat").val(),
            // need better time structure? evernote?
            time: $("#time").val(),
            post: $("#post").val()
        };
        if(!localStorage.posts)
            localStorage.posts = JSON.stringify({});
        var ps = JSON.parse(localStorage.posts);
        ps[d['time']] = d; // using time as the index??
        localStorage.posts = JSON.stringify(d);

        localStorage.cpost = undefined;
        $("#post").val("");
        $.ajax({
            url: pensievr_url + "post",
            data: d,
            success: function() {
                var ps = JSON.parse(localStorage.posts);
                ps[d['time']] = undefined;
                localStorage.posts = JSON.stringify(d);
            }
        });
        autofocus();
        e.preventDefault();
        return false;
    });
});
