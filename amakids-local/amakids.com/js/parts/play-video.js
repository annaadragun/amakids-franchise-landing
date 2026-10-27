$(document).ready(function () {
        $('.play-video').on('click', function (e) {
            function getUrlVars(href) {
                var vars = {};
                href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
                    vars[key] = value;
                });
                return vars;
            }
            e.preventDefault();
            var videoId = getUrlVars($(this).attr('href')).v;
            $(this).parent().html('<iframe width="' + $(this).outerWidth() + '" height="' + $(this).outerHeight() + '" src="https://www.youtube.com/embed/' + videoId + '?rel=0&autoplay=1" frameborder="0" allowfullscreen></iframe>')
        });
    }
);