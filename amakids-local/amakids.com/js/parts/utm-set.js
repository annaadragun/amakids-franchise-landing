(() => {
    const params = getUrlParams(window.location.href);
    const targetParams = ['admitad_uid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'online', 'promo', 'referrer'];
    const referrer = document.referrer ? (new URL(document.referrer)) : {};
    const targetUtmParams = localStorage.getItem('targetUtmParams') ? JSON.parse(localStorage.getItem('targetUtmParams')) : {};

    if(window.location.hostname !== referrer.hostname && referrer.hostname !== undefined){
        targetUtmParams['referrer'] = referrer.hostname;
    }

    if(Object.keys(params).length > 0){
        for(let param in params){
            if(targetParams.indexOf(param) !== -1){
                targetUtmParams[param] = params[param];
            }
        }
    }

    if(Object.keys(targetUtmParams).length > 0){
        localStorage.setItem('targetUtmParams', JSON.stringify(targetUtmParams));
    }
})();

function mixUtmParamsFromLocalStorage(data){
    const mixedParams = localStorage.getItem('targetUtmParams');

    if(mixedParams){
        data.append('targetUtmParams', encodeURI(mixedParams));
    }

    return data;
}

function getUrlParams(href) {
    const vars = {};
    const parts = href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value
    });
    return vars
}