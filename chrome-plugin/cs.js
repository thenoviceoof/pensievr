// send the user to pensievr on a key-combo
$(document).ready(function() {
    $(document).keydown(function(e) {
        if(e.keyCode == 190 && e.ctrlKey)
            window.location = "https://pensievr.appspot.com/"; 
    });
});
