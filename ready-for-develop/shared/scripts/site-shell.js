(function () {
    var routes = [
        { id: 'formats', label: 'Formats', href: '/#models' },
        { id: 'programs', label: 'Programs', href: '/#programs' },
        { id: 'support', label: 'Support', href: '/#support' },
        { id: 'investment', label: 'Investment', href: '/#investment' },
        { id: 'resources', label: 'Franchise Guides & Resources', href: '/resources/' }
    ];

    document.querySelectorAll('[data-site-header]').forEach(function (header, index) {
        var base = header.getAttribute('data-base') || '.';
        var activeRoute = header.getAttribute('data-route') || 'home';
        var navId = 'main-nav-' + index;
        var navLinks = routes.map(function (route) {
            var current = route.id === activeRoute;
            if (route.id === 'programs') {
                return '<div class="nav-dropdown' + (current ? ' is-active' : '') + '">' +
                    '<a href="' + base + route.href + '"' + (current ? ' aria-current="page"' : '') + '>Programs</a>' +
                    '<button class="nav-dropdown-toggle" type="button" aria-expanded="false" aria-label="Open program pages"><span></span></button>' +
                    '<div class="nav-dropdown-panel">' +
                        '<a href="' + base + '/programs/mental-arithmetic/">Abacus &amp; Mental Arithmetic</a>' +
                    '</div>' +
                '</div>';
            }
            return '<a href="' + base + route.href + '" class="' + (current ? 'is-active' : '') + '"' + (current ? ' aria-current="page"' : '') + '>' + route.label + '</a>';
        }).join('');
        var cta = header.hasAttribute('data-dialog-cta')
            ? '<button class="nav-cta" type="button" data-open-lead="presentation" data-cta-location="header">Get the presentation</button>'
            : '<a class="nav-cta" href="' + base + '/#presentation" data-cta-location="header">Get the presentation</a>';

        header.innerHTML = '<div class="shell header-inner">' +
            '<a class="brand" href="' + base + '/" aria-label="AMAkids home">' +
                '<img src="' + base + '/shared/assets/brand/logo-header.webp" alt="AMAkids">' +
            '</a>' +
            '<button class="nav-cta nav-cta-mobile" type="button" data-open-lead="presentation" data-cta-location="header">Get the presentation</button>' +
            '<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="' + navId + '">' +
                '<span></span><span></span><span></span><span class="visually-hidden">Open menu</span>' +
            '</button>' +
            '<nav class="main-nav" id="' + navId + '" aria-label="Main navigation">' + navLinks + cta + '</nav>' +
        '</div>';

        var nav = header.querySelector('.main-nav');
        var menuButton = header.querySelector('.menu-toggle');
        var programDropdown = header.querySelector('.nav-dropdown');
        var programDropdownButton = header.querySelector('.nav-dropdown-toggle');

        menuButton.addEventListener('click', function () {
            var isOpen = nav.classList.toggle('is-open');
            menuButton.setAttribute('aria-expanded', String(isOpen));
        });

        programDropdownButton.addEventListener('click', function (event) {
            event.stopPropagation();
            var isOpen = programDropdown.classList.toggle('is-open');
            programDropdownButton.setAttribute('aria-expanded', String(isOpen));
        });

        document.addEventListener('click', function (event) {
            if (!programDropdown.contains(event.target)) {
                programDropdown.classList.remove('is-open');
                programDropdownButton.setAttribute('aria-expanded', 'false');
            }
        });

        nav.querySelectorAll('a, button').forEach(function (control) {
            control.addEventListener('click', function () {
                if (control.classList.contains('nav-dropdown-toggle')) return;
                nav.classList.remove('is-open');
                menuButton.setAttribute('aria-expanded', 'false');
                programDropdown.classList.remove('is-open');
                programDropdownButton.setAttribute('aria-expanded', 'false');
            });
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                nav.classList.remove('is-open');
                menuButton.setAttribute('aria-expanded', 'false');
                programDropdown.classList.remove('is-open');
                programDropdownButton.setAttribute('aria-expanded', 'false');
            }
        });
    });
}());
