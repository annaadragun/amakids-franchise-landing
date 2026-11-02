(function () {
    var nav = document.getElementById('main-nav');
    var menuButton = document.querySelector('.menu-toggle');
    var dialog = document.getElementById('lead-dialog');
    var form = document.getElementById('partnership-form');
    var modelSelect = document.getElementById('contact-model');
    var leadType = document.getElementById('lead-type');
    var leadKicker = document.getElementById('lead-kicker');
    var leadTitle = document.getElementById('lead-title');
    var leadDescription = document.getElementById('lead-description');
    var leadSubmit = document.getElementById('lead-submit');
    var formNote = document.querySelector('#partnership-form .form-note');
    var formView = document.getElementById('lead-form-view');
    var successView = document.getElementById('lead-success');
    var successTitle = document.getElementById('success-title');
    var successDescription = document.getElementById('success-description');
    var presentationDownload = document.getElementById('presentation-download');

    if (nav && menuButton) {
        menuButton.addEventListener('click', function () {
            var isOpen = nav.classList.toggle('is-open');
            menuButton.setAttribute('aria-expanded', String(isOpen));
        });
        nav.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                nav.classList.remove('is-open');
                menuButton.setAttribute('aria-expanded', 'false');
            });
        });
    }

    document.querySelectorAll('[data-open-lead]').forEach(function (trigger) {
        trigger.addEventListener('click', function () {
            var requestedModel = trigger.getAttribute('data-model');
            var type = trigger.getAttribute('data-open-lead');
            form.reset();
            if (requestedModel) modelSelect.value = requestedModel;
            leadType.value = type;
            presentationDownload.hidden = false;
            formView.hidden = false;
            successView.hidden = true;

            if (type === 'financial') {
                leadKicker.textContent = 'Country-specific request';
                leadTitle.textContent = 'Get a financial model for your country and format';
                leadDescription.textContent = 'Tell us where you plan to operate and which partnership model you are considering.';
                leadSubmit.innerHTML = 'Request my financial model <span aria-hidden="true">↗</span>';
                formNote.textContent = 'In this local preview, your email app opens a draft. Send it to share your enquiry; contact details are not saved to a server.';
            } else if (type === 'proposal') {
                leadKicker.textContent = 'Partnership proposal';
                leadTitle.textContent = 'Request a Partnership Proposal';
                leadDescription.textContent = 'Share a few details about your market, partnership model and development plans.';
                leadSubmit.innerHTML = 'Request a proposal <span aria-hidden="true">↗</span>';
                formNote.textContent = 'In this local preview, your email app opens a draft. Send it to share your enquiry; contact details are not saved to a server.';
            } else {
                leadKicker.textContent = 'Partner overview';
                leadTitle.textContent = 'Get the AMAkids partnership presentation';
                leadDescription.textContent = 'Leave your contact details and choose the partnership model you are exploring.';
                leadSubmit.innerHTML = 'Get the presentation <span aria-hidden="true">↗</span>';
                formNote.textContent = 'The presentation downloads after the form. In this local preview, your email app opens a draft; send it to share your enquiry.';
            }

            if (!dialog.open) dialog.showModal();
            if (nav && nav.classList.contains('is-open')) {
                nav.classList.remove('is-open');
                menuButton.setAttribute('aria-expanded', 'false');
            }
        });
    });

    dialog.querySelector('.dialog-close').addEventListener('click', function () { dialog.close(); });
    dialog.querySelector('.dialog-done').addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (event) {
        if (event.target === dialog) dialog.close();
    });

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        if (!form.reportValidity()) return;

        var data = new FormData(form);
        var requestType = data.get('request_type');
        var isPresentation = requestType === 'presentation';
        var isProposal = requestType === 'proposal';
        var requestLabel = isPresentation ? 'Partnership presentation' : (isProposal ? 'Partnership proposal' : 'Country-specific financial model');
        var body = [
            'Request: ' + requestLabel,
            'Name: ' + data.get('name'),
            'Email: ' + data.get('email'),
            'Country: ' + data.get('country'),
            'Partnership model: ' + data.get('model'),
            'Existing education business: ' + (data.get('existing_business') || 'No')
        ].join('\n');
        var subject = 'AMAkids enquiry — ' + requestLabel;
        var mailto = 'mailto:info@amakids.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);

        formView.hidden = true;
        successView.hidden = false;
        if (isPresentation) {
            successTitle.textContent = 'Your partnership overview is ready';
            successDescription.textContent = 'The overview download should start. Your email app will open with a request to share your contact details; review and send the message to complete the enquiry.';
            presentationDownload.hidden = false;
            presentationDownload.click();
        } else if (isProposal) {
            successTitle.textContent = 'Your partnership proposal enquiry is prepared';
            successDescription.textContent = 'Your email app will open with your market and preferred model. Review and send the message to explore the opportunities available in your country.';
            presentationDownload.hidden = true;
        } else {
            successTitle.textContent = 'Your request is prepared';
            successDescription.textContent = 'Your email app will open with your country and selected model. Review and send the message to request a tailored financial model.';
            presentationDownload.hidden = true;
        }
        window.location.href = mailto;
    });
}());
