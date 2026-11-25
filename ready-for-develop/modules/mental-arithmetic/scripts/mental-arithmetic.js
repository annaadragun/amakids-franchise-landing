(function () {
    var focusBeforeModal = null;

    function closeDropdowns(except) {
        document.querySelectorAll('[data-dropdown].is-open').forEach(function (dropdown) {
            if (dropdown !== except) {
                dropdown.classList.remove('is-open');
                dropdown.querySelector('[data-dropdown-trigger]').setAttribute('aria-expanded', 'false');
            }
        });
    }

    document.querySelectorAll('[data-dropdown]').forEach(function (dropdown) {
        var trigger = dropdown.querySelector('[data-dropdown-trigger]');
        trigger.addEventListener('click', function (event) {
            event.stopPropagation();
            var willOpen = !dropdown.classList.contains('is-open');
            closeDropdowns(dropdown);
            dropdown.classList.toggle('is-open', willOpen);
            trigger.setAttribute('aria-expanded', String(willOpen));
        });
    });

    document.addEventListener('click', function () {
        closeDropdowns();
    });

    var mobileTrigger = document.querySelector('[data-mobile-menu-trigger]');
    var mobileMenu = document.querySelector('[data-mobile-menu]');
    var mobileProgramsTrigger = document.querySelector('[data-mobile-programs-trigger]');
    var mobilePrograms = document.querySelector('[data-mobile-programs]');

    mobileTrigger.addEventListener('click', function () {
        var open = mobileMenu.classList.toggle('is-open');
        mobileTrigger.setAttribute('aria-expanded', String(open));
    });

    mobileProgramsTrigger.addEventListener('click', function () {
        var open = mobilePrograms.classList.toggle('is-collapsed');
        mobileProgramsTrigger.setAttribute('aria-expanded', String(!open));
    });

    mobileMenu.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            mobileMenu.classList.remove('is-open');
            mobileTrigger.setAttribute('aria-expanded', 'false');
        });
    });

    var modal = document.querySelector('[data-enrollment-modal]');
    var dialog = modal.querySelector('.enrollment-dialog');
    var form = modal.querySelector('[data-enrollment-form]');
    var success = modal.querySelector('[data-enrollment-success]');

    function openModal() {
        focusBeforeModal = document.activeElement;
        modal.hidden = false;
        document.body.classList.add('modal-open');
        form.hidden = false;
        success.hidden = true;
        window.requestAnimationFrame(function () {
            modal.classList.add('is-open');
            dialog.querySelector('input').focus();
        });
    }

    function closeModal() {
        modal.classList.remove('is-open');
        document.body.classList.remove('modal-open');
        window.setTimeout(function () {
            modal.hidden = true;
            if (focusBeforeModal) focusBeforeModal.focus();
        }, 180);
    }

    document.querySelectorAll('[data-open-enrollment]').forEach(function (button) {
        button.addEventListener('click', openModal);
    });

    document.querySelectorAll('[data-close-enrollment]').forEach(function (button) {
        button.addEventListener('click', closeModal);
    });

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        if (!form.reportValidity()) return;
        form.hidden = true;
        success.hidden = false;
        success.querySelector('button').focus();
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeDropdowns();
            mobileMenu.classList.remove('is-open');
            mobileTrigger.setAttribute('aria-expanded', 'false');
            if (!modal.hidden) closeModal();
        }
    });
}());
