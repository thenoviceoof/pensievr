////////////////////////////////////////////////////////////////////////////////
// index.html

////////////////////////////////////////////////////////////////////////////////
// post.html

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

$(document).ready(function(){
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

    // create a mapping
    var m = new Array();
    var uniq = new Array();
    var r;
    // !!! replace with fischer-yates shuffle
    for(var i=0; i<256; i+=1) {
        r = Math.floor(Math.random() * 256);
        while(uniq[r]) {
            r = Math.floor(Math.random() * 256);
        }
        m[i] = r;
    }

    var paper = Raphael(10, 10, 1000, 100);
    var count = 0;
    // display the contents with the mapping
    function gen_char(num) {
        paper.rect(count*30 - 2, -2, 24, 44, 4)
            .attr({fill:"#DDD",stroke:"#DDD"});
        for(var i=0; i<2; i++) {
            for(var j=0; j<4; j++) {
                if( (m[num] >> (i*4 + j)) & 1 == 1 ) {
                    paper.rect(count*30 + i*10, j*10, 8,8).attr({fill:"black"});
                }
            }
        }
        count += 1;
    }

    $("#post").keydown(function(e){
        // display stuff with raphael
        gen_char(e.keyCode);
    });
});