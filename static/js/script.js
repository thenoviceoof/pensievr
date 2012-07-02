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
    if(!localStorage.mapping) {
        // !!! replace with fischer-yates shuffle
        for(var i=0; i<256; i+=1) {
            r = Math.floor(Math.random() * 256);
            while(uniq[r]) {
                r = Math.floor(Math.random() * 256);
            }
            m[i] = r;
        }
        localStorage.mapping = JSON.stringify(m);
    } else {
        m = JSON.parse(localStorage.mapping);
    }

    var paper = Raphael(10, 10, 1000, 200);
    // display the contents with the mapping
    function gen_char(num, offset_x, offset_y, height, margin) {
        if(height === undefined)
            height = 60;
        if(margin === undefined)
            margin = 8;
        if(num === 0)
            return;
        var x = offset_x*(height/2 + 2*margin);
        var y = offset_y*(height + 2*margin);
        paper.rect(x-margin/2, y-margin/2, height/2+margin, height+margin, margin)
            .attr({fill:"#DDD",stroke:"#DDD"});
        for(var i=0; i<2; i++) {
            for(var j=0; j<4; j++) {
                if( (m[num] >> (i*4 + j)) & 1 == 1 ) {
                    paper.rect(x + i*height/4,
                               y + j*height/4,
                               height/4,height/4).attr({fill:"black"});
                }
            }
        }
    }
    function gen_str(str) {
        for(var c in str) {
            var chr = str[c];
            gen_char(chr.charCodeAt(0), c, 0, 40, 5);
        }
    }

    function redraw() {
        // display stuff with raphael
        paper.clear();
        var str = $("#post").val();
        gen_str(str);
    }

    $("#post").keyup(redraw).keydown(redraw);

    set_time();
    get_location();
});