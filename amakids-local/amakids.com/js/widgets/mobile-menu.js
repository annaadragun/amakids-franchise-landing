$(document).ready(function() {
    const mobileMenu = $('.mobile-top-menu-content');

    document.addEventListener('click', (e) => {
        const target = e.target;

        if($(mobileMenu).hasClass('show') && !target.closest('.mobile-top-menu-content') && !target.closest('#mobile-top-menu-trigger')){
            $(mobileMenu).removeClass('show');
        }
    })

    $('#mobile-top-menu-trigger').click(function (e) {
        e.preventDefault();

        if($(mobileMenu).hasClass('show')){
            $(mobileMenu).removeClass('show');
        }else{
            $(mobileMenu).addClass('show');
        }
    });

    $('.dropdown-mobile-wrapper').on('click', (e) => {
        const wrapper = e.target.closest('.dropdown-mobile-wrapper');
        if($(wrapper).hasClass('open')){
            $(wrapper).removeClass('open');
        }else{
            $(wrapper).addClass('open');
        }

    });
});