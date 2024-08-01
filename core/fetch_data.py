import requests
import sys
import json

def fetch_data(from_currency, to_currency):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{from_currency}{to_currency}=X'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        result = data['chart']['result'][0]['meta']
        return {
            'currency_pair': result['symbol'],
            'current_price': result['regularMarketPrice'],
            'high_price': result['regularMarketDayHigh'],
            'low_price': result['regularMarketDayLow']
        }
    else:
        return {'error': 'Failed to fetch data from Yahoo Finance'}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({'error': 'Usage: python fetch_data.py <FROM_CURRENCY> <TO_CURRENCY>'}))
        sys.exit(1)
    
    from_currency = sys.argv[1]
    to_currency = sys.argv[2]

    result = fetch_data(from_currency, to_currency)
    print(json.dumps(result))
