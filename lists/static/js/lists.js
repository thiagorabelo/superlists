(function(window) {
    let superlists = window.Superlists || {};

    superlists.initialize = () => {
        $('input[name=text]').on('keypress', function(e) {
            $('.has-error').hide();
        });
    };

    window.Superlists = superlists;
}(window));
