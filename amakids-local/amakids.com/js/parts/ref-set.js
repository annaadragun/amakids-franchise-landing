(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const ref = urlParams.get('ref');

    if (ref) {
        localStorage.setItem('ref', ref);
    }
})();

function getRefFromStorage() {
    return localStorage.getItem('ref');
}
