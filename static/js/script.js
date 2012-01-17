////////////////////////////////////////////////////////////////////////////////
// index.html

////////////////////////////////////////////////////////////////////////////////
// post.html

// auto-focus on the text field
if(document.post_form)
    document.post_form.post.focus();

// convert the seconds to local time
var t = new Date(1000*$("#last-post span").html());
$("#last-post span").html(t.toLocaleTimeString());

$("#aboutLink, #closeAboutLink").click(function(){
    $("#about").toggle();
    return false;
});

// geolocation
function get_location() {
    function loc_success(position) {
	$("#loc_lat").val(position.coords.latitude);
	$("#loc_long").val(position.coords.longitude);
    }

    function loc_error(msg) {
	alert("Sorry, couldn't fetch your location");
    }

    if (navigator.geolocation) {
	navigator.geolocation.getCurrentPosition(loc_success, loc_error);
    } else {
	error('not supported');
    }
}

// get current date stamp
function set_time() {
    var dobj = new Date();
    var y = dobj.getFullYear();
    var m = dobj.getMonth() + 1; // because js is silly
    var d = dobj.getDate();
    y = (y<10 ? "0" : "")+y;
    m = (m<10 ? "0" : "")+m;
    d = (d<10 ? "0" : "")+d
    $("#time").val(y+"-"+m+"-"+d);
}