let formCaptchaV2 = false;

$(() => {
    const intTelInputs = $('[data-intl-tel]');

    const iti = intTelInputs.intlTelInput({
        utilsScript: '/modules/intl-tel-input/js/utils.js',
        initialCountry: 'auto',
        showFlags: false,
        nationalMode: false,
        autoPlaceholder: 'aggressive',
        geoIpLookup: function(callback) {
            fetch("https://ipapi.co/json")
                .then(function(res) { return res.json(); })
                .then(function(data) { callback(data.country_code); })
                .catch(function() { callback('us'); });
        },
        separateDialCode: true,
    });

    intTelInputs.on('countrychange', (e) => {
        const input = $(e.target);
        const placeholder = input.attr('placeholder');
        const country = input.intlTelInput('getSelectedCountryData');

        if(placeholder !== undefined){
            let mask = placeholder.replace(new RegExp("[0-9]", "g"), "9");

            //TODO добавлять страны с корявыми номерами сюда
            if(country.iso2 === 'bg'){
                mask = mask + '?99';
            }

            input.mask(mask);
        }
    })

    $('[data-form] form').on('submit', function (e) {
        e.preventDefault();

        validateForm(this);
    });

    $('[data-open-form]').on('click', function (e) {
        const formType = $(e.target).attr('data-open-form');
        const conditionsString = $(e.target).attr('data-form-selected-values');
        const targetForm = $(`[data-form="${formType}"]`);

        if(conditionsString){
            const conditions = JSON.parse(conditionsString);
            targetForm.find('[name="conditions"]').val(conditionsString);

            updateInputsByConditions(targetForm.find('form'), conditions).then(() => {
                for(let conditionName in conditions){
                    const conditionValue = conditions[conditionName];
                    const currentSelect = targetForm.find(`[data-select-name="${conditionName}"]`);
                    const selectedOption = currentSelect.find(`[data-value-id="${conditionValue}"]`);
                    const value = selectedOption.attr('data-value');

                    //Значения нет в списке (например, язык сайта, которого нет в онлайн-форме) - не подставляем
                    if(!selectedOption.length){
                        openForm(targetForm);
                        continue;
                    }

                    if(conditionValue > 0){
                        currentSelect.attr('disabled', 'disabled');
                        currentSelect.find('[name="search-data"]').attr('readonly', '');
                    }

                    changeInput(currentSelect, conditionValue, value, false);
                    openForm(targetForm);
                }
            });
        }else{
            openForm(targetForm);
        }

    });

    $('[data-form-close]').on('click', function (e) {
        //Закрытие формы
        $(e.target).closest('[data-form]').fadeOut(100, function () {
            $(document.body).removeClass('modal-open');

            $(this).find('[data-select-name]').each(function (index, item) {
                clearInput($(item));

                if(item.hasAttribute('data-depended-select')){
                    hideSelect('', '', $(item));
                }
            });
        });
    });

    $(document).on('click', function (e){
        if(!e.target.closest('.custom-select-container')){
            let selectContainer = $('.custom-select-wrapper');

            if(selectContainer.hasClass('opened')){
                selectContainer.find('input[name="search-data"]').val('').trigger('keyup');
                selectContainer.removeClass('opened');
            }
        }

        if(e.target.closest('.errorInput')){
            $(e.target).closest('.errorInput').removeClass('errorInput');
        }
    });

    //Клик по селекту
    $('.custom-select-container[data-select-name]').click(function (e){
        removeError(e.target);
        if(this.hasAttribute('disabled')) return;

        //Закрыть другие селекты
        $('.custom-select-wrapper').removeClass('opened');

        let selectOption = $(e.target),
            value = selectOption.data('value'),
            container = selectOption.closest('.custom-select-container'),
            targetID = selectOption.attr('data-value-id');

        if(!$(e.target).hasClass('custom-select-option')){
            $(e.target).closest('[data-select-name]').find('.custom-select-wrapper').toggleClass('opened');
            clearSearch(container);
            return;
        }

        changeInput(container, targetID, value);
        updateInputsByConditions(selectOption);
    });

    //Поиск в селекте
    $('[name="search-data"]').on('keyup', function (e){
        if(this.hasAttribute('readonly')) return ;

        if(!$(e.target).closest('.custom-select-wrapper').hasClass('opened')){
            $(e.target).closest('.custom-select-wrapper').addClass('opened');
        }

        filterOptions(this);
    });

    $('[data-target-input]').on('click', function (e) {
        removeError(e.target);
    })
});

function openForm(targetForm){
    $(document.body).addClass('modal-open');
    targetForm.fadeIn(200);
}

function filterOptions(that){
    let filter = $(that).val();

    $(that).closest('.custom-select-wrapper').find(".custom-select-option").each(function(){
        if ($(this).text().search(new RegExp(filter, "i")) < 0) {
            $(this).fadeOut();
        } else {
            $(this).show();
        }
    });
}

function changeInput(wrapper, id, value, updateDependedInputs = true){
    const inputSearch = wrapper.find('[name="search-data"]');
    const input = wrapper.find('[data-target-input]');
    const name = wrapper.attr('data-select-name');

    input.val(id);
    inputSearch.val('');
    inputSearch.attr('placeholder', value);
    input.trigger('change');

    if(updateDependedInputs){
        updateConditionsForm(input, name, id);
        //Обнулить зависимые селекты
        clearDependedInputs(input, name);
    }
}

function clearDependedInputs(selector, name){
    const form = selector.closest('form');
    const dependedInputs = form.find(`[data-depend-from-${name}]`);

    dependedInputs.each(function (index, item){
        item = $(item);
        if(item.attr('disabled') !== 'disabled'){
            clearInput(item);
        }
    });
}

function clearSearch(wrapper){
    const inputSearch = wrapper.find('[name="search-data"]');
    inputSearch.val('');
    inputSearch.trigger('keyup');
}

function clearInput(wrapper){
    const input = typeof wrapper.attr('data-target-input') !== 'undefined' ? wrapper : wrapper.find('[data-target-input]');
    const inputSearch = wrapper.find('[name="search-data"]');

    input.val('');

    if(inputSearch){
        const stockPlaceholder = inputSearch.attr('data-placeholder');

        inputSearch.val('');
        inputSearch.attr('placeholder', stockPlaceholder);
    }


    updateConditionsForm(input, input.attr('name'), 0);
}

function hideSelect(form = '', name = '', input = ''){
    let selector = {};

    if(name && form){
        selector = form.find(`[data-select-name="${name}"]`);

        if(selector.length === 0){
            selector = form.find(`[data-input-name="${name}"]`);
        }
    }

    if(input){
        selector = input;
    }

    if(selector.length > 0){
        selector.removeAttr('disabled');
        selector.find('[readonly]').removeAttr('readonly');

        selector.closest('.input-wrapper').addClass('hidden-wrapper');
    }
}

function updateConditionsForm(selector, conditionName, conditionValue){
    const form = selector.closest('form');
    const conditionsInput = form.find('[name="conditions"]');

    const conditions = conditionsInput.val() ? JSON.parse(conditionsInput.val()) : {};

    conditions[conditionName] = conditionValue;
    conditionsInput.val(JSON.stringify(conditions));

    //updateDependedInputs(form, conditionName, conditions);
}

function insertDataToSelect(form, conditionName, data){
    const selectWrapper = form.find(`[data-select-name="${conditionName}"] .custom-select-options-wrapper .custom-select-options`);
    const input = form.find(`[data-input-name="${conditionName}"]`);

    if(selectWrapper.length === 0 && input.length === 0) return ;

    if(selectWrapper.length > 0){
        selectWrapper.html('');

        const wrapper = selectWrapper.closest('.custom-select-container');
        const inputWrapper = wrapper.closest('.input-wrapper');

        inputWrapper.removeClass('hidden-wrapper');

        for(let key in data){
            const div = document.createElement('div');
            div.className = 'custom-select-option';
            div.setAttribute('data-value-id', key);
            div.setAttribute('data-value', data[key]);
            div.innerHTML = data[key];
            selectWrapper.append(div);
        }
    }

    if(input.length > 0){
        input.closest('.input-wrapper').removeClass('hidden-wrapper');
    }
}

async function getSelectData(name, conditions, currentLanguage){
    const formData = new FormData();

    formData.append(yii.getCsrfParam(), yii.getCsrfToken());
    formData.append('name', name);
    formData.append('currentLanguage', currentLanguage);
    formData.append('conditions', JSON.stringify(conditions));

    const fetchInit = {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: formData
    };

    return await fetch( '/ajax/get-custom-select-depended-data/', fetchInit).then((response) => {
        if(!response.ok){
            console.error('error Fetch:', response);
        }

        return response.json();

    }).then((response) => {
        return response.status ? response.data : false;
    }).catch(error => {
        console.error('Backend error:', error);
    });
}

async function updateInputsByConditions(selector, conditions = false){
    const form = selector.closest('form');
    const language = form.find('[name="currentLanguage"]').val();

    const conditionsInput = form.find('[name="conditions"]');

    conditions = conditions ? conditions : JSON.parse(conditionsInput.val());

    for(let conditionName in conditions){
        const conditionValue = conditions[conditionName];

        await getSelectData(conditionName, conditions, language).then((data) => {
            if(data){
                insertDataToSelect(form, conditionName, data);
            }else{
                hideSelect(form, conditionName);
            }
        });
    }
}

function validateForm(form){
    let isValidForm = true;
    const inputs = $(form).find('[data-target-input][data-required]');

    inputs.each(function (index, item){
        item = $(item);

        if(!isValidData(item) && !item.closest('.hidden-wrapper').length){
            item.closest('.input-wrapper').addClass('error-wrapper');
            isValidForm = false;
        }
    });


    if(isValidForm){
        showSendingForm(form);
        sendForm(form).then((data) => {
            if(data){
                //GA4: успешная заявка (дополнительно к существующим событиям)
                if(data.formType !== 'translate' && typeof window.gtag === 'function'){
                    try {
                        window.gtag('event', 'generate_lead', { 'form_type': data.formType });
                    }catch (e) {}
                }

                switch (data.formType){
                    case 'translate':
                        window.location.reload();
                        break;
                    case 'franchise':
                        console.log('test lead send');
                        try {
                            //fbq('track', 'Lead');
                            gtag('event', 'заявка_франшиза', { 'event_category': 'callbackFormFranchise', 'event_action': 'send_form', });
                            fbq('track', 'Lead');
                        }catch (e) {}
                    default:
                        const formWrapper = $('[data-form="'+data.formType+'"]');
                        showSuccessInForm(formWrapper);
                }
            }
        });
    }
}

function showSendingForm(formNative){
    const form = $(formNative);
    const button = form.find('[type="submit"]');
    const sendingInfo = form.find('.sending-info');
    button.hide();
    sendingInfo.show();
}
function hideSendingForm(formNative){
    const form = $(formNative);
    const button = form.find('[type="submit"]');
    const sendingInfo = form.find('.sending-info');
    sendingInfo.hide();
    button.show();
}

function showSuccessInForm(formWrapper){
    const form = formWrapper.find('.international-form');
    const successWindow = formWrapper.find('.success-window');
    form.addClass('hidden');
    successWindow.removeClass('hidden');
}

function isValidData(input){
    const name = input.attr('name');
    const value = input.val();
    const intlTelAttr = input.attr('data-intl-tel');

    if(typeof intlTelAttr !== 'undefined'){
        const country = input.intlTelInput('getSelectedCountryData');

        if(country.iso2 === 'bg'){
            return value.length > 5;
        }

        return input.intlTelInput('isValidNumber');
    }

    //TODO валиадация
    if(value > 0 || value.length > 1){
        return true;
    }

    return false;
}

function removeError(selector){
    if(selector.closest('.error-wrapper')){
        selector.closest('.error-wrapper').classList.remove('error-wrapper');
    }
}

function sendForm(form){
    let formData = new FormData(form);
    const phone = form.querySelector('[name="phone"]');

    //Для полного номера
    if(phone){
        formData.set('phone', $(phone).intlTelInput('getNumber'));
    }

    formData = mixUtmParamsFromLocalStorage(formData);

    //Первая страница сессии (сохраняется в js/parts/analytics-events.js) и страница, с которой отправлена заявка
    let landingUrl = '';
    try {
        landingUrl = sessionStorage.getItem('landingUrl') || '';
    }catch (e) {}
    formData.append('landing_url', landingUrl || window.location.href);
    formData.append('page_url', window.location.href);

    formData.append(yii.getCsrfParam(), yii.getCsrfToken());

    const fetchInit = {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: formData
    };

    return fetch( '/ajax/send-form/', fetchInit).then((response) => {
        if(!response.ok){
            console.error('error Fetch:', response);
        }

        return response.json();

    }).then((response) => {
        if(response.status){
            return response.data;
        }else{
            resolveFormError(form, response.reason)
            return false;
        }
    }).catch(error => {
        console.error('Backend error:', error);
    });
}

function resolveFormError(form, reason){

    hideSendingForm(form);

    const captchaWrapper = $('#captcha').closest('.input-wrapper');

    switch (reason){
        case 'fallCaptchaV3':
            captchaWrapper.removeClass('hidden');
            captchaWrapper.find('input[name="captchaTokenV3"]').val('');

            formCaptchaV2 = grecaptcha.render('captcha', {
                'sitekey': $(form).find('input[name="captchaSiteKeyV2"]').val(),
                'theme': 'light',
                'callback': function (token){
                    $(form).find('input[name="captchaTokenV2"]').val(token)
                }
            });
            break;

        case 'fallCaptchaV2':
            if(formCaptchaV2 !== false){
                grecaptcha.reset(formCaptchaV2);
            }
            break;

        case 'fallCaptcha':
            captchaWrapper.addClass('error-wrapper');
            break;
    }
}