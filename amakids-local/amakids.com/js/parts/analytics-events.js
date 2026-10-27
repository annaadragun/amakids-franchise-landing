// События GA4 для SEO-013 (дополнительно к существующим, существующие не меняем).
// Все события отправляются, только если на странице есть gtag (счётчики подключены).
(() => {
    // Первая страница сессии — для поля landing_url в заявках (читается в form.js, sendForm)
    try {
        if (!sessionStorage.getItem('landingUrl')) {
            sessionStorage.setItem('landingUrl', window.location.href);
        }
    } catch (e) {}

    function sendEvent(name, params) {
        if (typeof window.gtag !== 'function') return;

        try {
            window.gtag('event', name, params);
        } catch (e) {}
    }

    // Где на странице кнопка: id ближайшего блока с id, иначе класс блока верхнего уровня внутри <main>
    function getCtaLocation(element) {
        let node = element.parentElement;

        while (node && node !== document.body) {
            if (node.id) return node.id;
            node = node.parentElement;
        }

        node = element;
        while (node && node.parentElement && node.parentElement.tagName !== 'MAIN' && node.parentElement !== document.body) {
            node = node.parentElement;
        }

        if (node && node !== element && typeof node.className === 'string' && node.className.trim()) {
            return node.className.trim().split(/\s+/).slice(0, 3).join(' ');
        }

        return 'unknown';
    }

    document.addEventListener('click', (e) => {
        if (!e.target || typeof e.target.closest !== 'function') return;

        // Клик по кнопке заявки на франшизу
        const cta = e.target.closest('[data-open-form="franchise"]');
        if (cta) {
            sendEvent('franchise_cta_click', {
                cta_location: getCtaLocation(cta),
                page_path: window.location.pathname,
            });
        }

        // Скачивание PDF
        const link = e.target.closest('a[href]');
        if (link) {
            const href = link.getAttribute('href') || '';
            const path = href.split('#')[0].split('?')[0];

            if (/\.pdf$/i.test(path)) {
                let fileName = path.substring(path.lastIndexOf('/') + 1);
                try {
                    fileName = decodeURIComponent(fileName);
                } catch (err) {}

                sendEvent('file_download', {
                    file_name: fileName,
                });
            }
        }
    }, true);

    // Начало заполнения формы: первый фокус внутри каждой формы
    document.addEventListener('focusin', (e) => {
        if (!e.target || typeof e.target.closest !== 'function') return;

        const form = e.target.closest('[data-form] form');
        if (!form || form.getAttribute('data-form-started') === '1') return;

        form.setAttribute('data-form-started', '1');

        const wrapper = form.closest('[data-form]');
        const formType = wrapper ? wrapper.getAttribute('data-form') : 'unknown';

        // Форма переводчика — служебная, не заявка
        if (formType === 'translate') return;

        sendEvent('form_start', {
            form_type: formType,
        });
    });
})();
