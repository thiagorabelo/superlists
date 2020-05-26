var initialize = function() {
    $('input[name=text]').on('keypress', function(e) {
        $('.has-error').hide();
    });
}
