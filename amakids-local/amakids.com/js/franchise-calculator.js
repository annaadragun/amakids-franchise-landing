(function () {
    var format = document.getElementById('calc-format');
    if (!format) return;

    // Illustrative Full Center ranges transcribed from the supplied PDF.
    // They are examples, not a universal or market-approved forecast.
    var assumptions = {
        large: {
            investment: [4000, 10000],
            margin: [0.35, 0.35],
            costs: ['Premises 10%', 'Trainer 15%', 'Marketing 15%', 'Taxes 10%', 'Royalty 10%', 'Other 5%']
        },
        medium: {
            investment: [1500, 8000],
            margin: [0.40, 0.40],
            costs: ['Premises 10%', 'Trainer 15%', 'Marketing 10%', 'Taxes 10%', 'Royalty 10%', 'Other 5%']
        },
        small: {
            investment: [700, 2100],
            margin: [0.45, 0.75],
            costs: ['Premises 0–10%', 'Trainer 0–15%', 'Marketing 0–5%', 'Taxes 10%', 'Royalty 10%', 'Other 5%']
        }
    };

    var city = document.getElementById('calc-city');
    var students = document.getElementById('calc-students');
    var price = document.getElementById('calc-price');
    var studentsValue = document.getElementById('calc-students-value');
    var priceValue = document.getElementById('calc-price-value');
    var studentsField = document.getElementById('calc-students-field');
    var priceField = document.getElementById('calc-price-field');
    var formatNote = document.getElementById('calc-format-note');
    var investmentResult = document.getElementById('calc-investment');
    var profitResult = document.getElementById('calc-profit');
    var paybackResult = document.getElementById('calc-payback');
    var costBreakdown = document.getElementById('calc-cost-breakdown');
    var disclaimer = document.getElementById('calc-disclaimer');
    var euro = new Intl.NumberFormat('en', { maximumFractionDigits: 0 });

    function eur(value) {
        return '€' + euro.format(Math.round(value));
    }

    function update() {
        var isMaster = format.value === 'master';
        var isFullCenter = format.value === 'center';
        var isSupported = isFullCenter;
        var scenario = assumptions[city.value];
        var lowerProfit = Number(students.value) * Number(price.value) * scenario.margin[0];
        var upperProfit = Number(students.value) * Number(price.value) * scenario.margin[1];

        studentsField.hidden = isMaster;
        priceField.hidden = isMaster;
        formatNote.hidden = isSupported;
        formatNote.textContent = isMaster
            ? 'A Master Franchise estimate depends on territory and partner-network assumptions. Request a tailored estimate for this format.'
            : 'A Mono-class estimate depends on course mix and local start-up costs. Request a tailored estimate for this format.';

        studentsValue.textContent = Number(students.value) >= 90 ? '90+' : students.value;
        priceValue.textContent = '€' + price.value;

        if (isSupported) {
            var investmentLow = scenario.investment[0];
            var investmentHigh = scenario.investment[1];
            var paybackLow = investmentLow / upperProfit;
            var paybackHigh = investmentHigh / lowerProfit;

            investmentResult.textContent = '≈ ' + eur(investmentLow) + '–' + eur(investmentHigh);
            profitResult.textContent = lowerProfit === upperProfit
                ? '≈ ' + eur(lowerProfit) + ' / month'
                : '≈ ' + eur(lowerProfit) + '–' + eur(upperProfit) + ' / month';
            var firstMonth = Math.ceil(paybackLow);
            var lastMonth = Math.ceil(paybackHigh);
            paybackResult.textContent = firstMonth === lastMonth
                ? '≈ ' + firstMonth + (firstMonth === 1 ? ' month' : ' months')
                : '≈ ' + firstMonth + '–' + lastMonth + ' months';
            costBreakdown.innerHTML = scenario.costs.map(function (item) { return '<li>' + item + '</li>'; }).join('');
            disclaimer.textContent = 'Illustrative estimate in EUR. Monthly profit applies a city-level margin to your selected course enrollments and price. Simple payback divides the investment range by monthly profit and excludes ramp-up timing, interim cash flow and local market costs.';
        } else {
            investmentResult.textContent = 'Individual estimate';
            profitResult.textContent = 'Individual estimate';
            paybackResult.textContent = 'Individual estimate';
            costBreakdown.innerHTML = '';
            disclaimer.textContent = 'A complete estimate for this format depends on additional local assumptions. Share your details to receive a tailored estimate.';
        }

        var panel = document.querySelector('.calculator-panel');
        panel.dataset.format = format.value;
        panel.dataset.citySize = city.value;
    }

    [format, city, students, price].forEach(function (control) {
        control.addEventListener('input', update);
        control.addEventListener('change', update);
    });

    update();
}());
