document.addEventListener('DOMContentLoaded', function () {
    const modalContainer = document.getElementById('tbilisicupModalContainer');
    const modalWrapper = document.getElementById('tbilisicupModalWrapper');
    const closeBtn = document.getElementById('tbilisicupModalClose');

    const MODAL_KEY = 'tbilisicupModalLastShown';
    const MODAL_DELAY = 3000;
    const MODAL_COOLDOWN = 4 * 60 * 60 * 1000; // 4 часа

    // Как у VF CUP (vfcup.js): окно не раньше 3 с после загрузки и только после первого действия
    // пользователя, иначе оно становится самым большим элементом страницы и портит LCP на мобильных.
    const INPUT_EVENTS = ['pointerdown', 'touchstart', 'wheel', 'keydown'];

    function getLastShown() {
        try {
            return parseInt(localStorage.getItem(MODAL_KEY), 10) || 0;
        } catch (e) {
            return 0;
        }
    }

    function showModal() {
        modalContainer.classList.add('active');
        try {
            localStorage.setItem(MODAL_KEY, Date.now().toString());
        } catch (e) {}
    }

    function hideModal() {
        modalContainer.classList.remove('active');
    }

    // Картинка баннера начинает грузиться только здесь
    function prepareModal() {
        modalContainer.querySelectorAll('img[data-src]').forEach(function (img) {
            img.src = img.getAttribute('data-src');
            img.removeAttribute('data-src');
        });
    }

    closeBtn.addEventListener('click', hideModal);

    modalContainer.addEventListener('click', function (e) {
        if (!modalWrapper.contains(e.target)) {
            hideModal();
        }
    });

    if (Date.now() - getLastShown() <= MODAL_COOLDOWN) {
        return;
    }

    const loadedAt = Date.now();
    let started = false;

    function onFirstInput() {
        if (started) {
            return;
        }
        started = true;
        INPUT_EVENTS.forEach(function (type) {
            window.removeEventListener(type, onFirstInput, true);
        });

        prepareModal();
        setTimeout(showModal, Math.max(0, MODAL_DELAY - (Date.now() - loadedAt)));
    }

    INPUT_EVENTS.forEach(function (type) {
        window.addEventListener(type, onFirstInput, {capture: true, passive: true});
    });
});
