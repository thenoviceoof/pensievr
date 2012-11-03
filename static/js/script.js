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
    if(document.post_form) {
        var $post = $(document.post_form.post);
        $post.focus();
        $(window).focus(function(e){
            $post.focus();
        });
    }

    // convert the seconds to local time
    var t = new Date(1000*$("#last-post span").html());
    $("#last-post span").html(t.toLocaleTimeString());

    $("#aboutLink, #closeAboutLink").click(function(){
        $("#about").toggle();
        return false;
    });

    // create a text/font mapping
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

    var w = $(document).width();
    var h = $(document).height();
    var paper = Raphael(0, 0, w, h);
    // display the contents with the mapping
    function gen_char(num, offset_x, offset_y, height, margin) {
        // display a character for a given number
        if(height === undefined)
            height = 60;
        if(margin === undefined)
            margin = 8;
        if(num === 0)
            return;
        var x = offset_x*(height/2 + 2*margin) + margin/2;
        var y = offset_y*(height + 2*margin) + margin/2;
        var t = paper.text(x + height/4, y + height/2, String.fromCharCode(num))
            .attr({"font-size":"20pt"});
        var r = paper.rect(x-margin/2, y-margin/2,
                           height/2+margin, height+margin, margin)
            .attr({fill:"#DDD",stroke:"#DDD"});
        var st = paper.set();
        for(var i=0; i<2; i++) {
            for(var j=0; j<4; j++) {
                if( (m[num] >> (i*4 + j)) & 1 == 1 ) {
                    var b = paper.rect(x + i*height/4,
                                       y + j*height/4,
                                       height/4,height/4).attr({fill:"black"});
                    st.push(b);
                }
            }
        }
        r.mouseover(function() {
            r.attr({opacity:0.0});
            st.attr({opacity:0.0});
        }).mouseout(function() {
            r.attr({opacity:1.0});
            st.attr({opacity:1.0});
        });
        st.mouseover(function() {
            r.attr({opacity:0.0});
            st.attr({opacity:0.0});
        }).mouseout(function() {
            r.attr({opacity:1.0});
            st.attr({opacity:1.0});
        });
        return new Array(r,st,t);
    }
    var cw = 40;
    var cm = 5;
    var char_width = (cw + 2*cm);
    var chars_wide = w / char_width;
    var chars = new Array();
    function gen_str(str) {
        chars = new Array();
        for(var c in str) {
            var chr = str[c];
            var rows = Math.floor(c / chars_wide);
            var cols = Math.floor(c % chars_wide);
            var disp = gen_char(chr.charCodeAt(0), cols, rows, cw, cm);
            // save it for later
            chars.push(disp);
        }
    }

    var current_str = "";
    function redraw() {
        // display stuff with raphael
        var str = $("#post").val();
        console.log("Refresh page");
        paper.clear();
        gen_str(str);
    }

    $("#post").keyup(redraw);

    set_time();
    get_location();
});