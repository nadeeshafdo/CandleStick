document.addEventListener('DOMContentLoaded', function() {
    populateCurrencyOptions();
});

async function populateCurrencyOptions() {
    try {
        const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
        const data = await response.json();
        const currencies = Object.keys(data.rates);
        
        const fromCurrencySelect = document.getElementById('fromCurrency');
        const toCurrencySelect = document.getElementById('toCurrency');
        
        currencies.forEach(currency => {
            const optionFrom = document.createElement('option');
            optionFrom.value = currency;
            optionFrom.textContent = currency;
            fromCurrencySelect.appendChild(optionFrom);

            const optionTo = document.createElement('option');
            optionTo.value = currency;
            optionTo.textContent = currency;
            toCurrencySelect.appendChild(optionTo);
        });
    } catch (error) {
        console.error('Error fetching currencies:', error);
    }
}

async function fetchExchangeRate() {
    const fromCurrency = document.getElementById('fromCurrency').value;
    const toCurrency = document.getElementById('toCurrency').value;

    const log = document.getElementById('log');
    log.innerHTML = '';

    log.innerHTML += `[INFO] Fetching data for ${fromCurrency} to ${toCurrency}<br>`;

    try {
        const response = await fetch(`../core/api.php?fromCurrency=${fromCurrency}&toCurrency=${toCurrency}`, {
            method: 'GET'
        });
        const result = await response.json();

        if (result.error) {
            log.innerHTML += `[ERROR] ${result.error}<br>`;
            return;
        }

        document.getElementById('result').innerHTML = `
            <p>Currency Pair: ${result.currency_pair}</p>
            <p>Current Price: ${result.current_price}</p>
            <p>High Price: ${result.high_price}</p>
            <p>Low Price: ${result.low_price}</p>
        `;
    } catch (error) {
        log.innerHTML += `[ERROR] Failed to fetch data from API<br>`;
        console.error('Error fetching exchange rate:', error);
    }
}
