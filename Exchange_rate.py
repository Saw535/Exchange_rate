import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta

async def fetch_exchange_rate(session, date):
    url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date.strftime("%d.%m.%Y")}'
    async with session.get(url) as response:
        data = await response.json()
        exchange_rates = data.get('exchangeRate', [])
        return {
            'date': date.strftime("%d.%m.%Y"),
            'EUR': {
                'sale': next((rate['saleRate'] for rate in exchange_rates if rate['currency'] == 'EUR'), None),
                'purchase': next((rate['purchaseRate'] for rate in exchange_rates if rate['currency'] == 'EUR'), None),
            },
            'USD': {
                'sale': next((rate['saleRate'] for rate in exchange_rates if rate['currency'] == 'USD'), None),
                'purchase': next((rate['purchaseRate'] for rate in exchange_rates if rate['currency'] == 'USD'), None),
            }
        }

async def get_exchange_rates(num_days):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_exchange_rate(session, datetime.now() - timedelta(days=i)) for i in range(num_days)]
        return await asyncio.gather(*tasks)

def format_output(data):
    formatted_data = []
    for item in data:
        formatted_data.append({
            item['date']: {
                'EUR': item['EUR'],
                'USD': item['USD']
            }
        })
    return formatted_data

async def main():
    if len(sys.argv) != 2:
        print("Використання: python main.py <кількість_днів>")
        return

    try:
        num_days = int(sys.argv[1])
        if num_days <= 0 or num_days > 10:
            print("Error: Будь ласка, вкажіть число днів від 1 до 10.")
            return
    except ValueError:
        print("Error: Неправильний ввід. Будь ласка, вкажіть правильне число днів.")
        return

    exchange_rates = await get_exchange_rates(num_days)
    formatted_data = format_output(exchange_rates)
    for item in formatted_data:
        print(item)

if __name__ == '__main__':
    asyncio.run(main())