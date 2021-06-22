import redis
from decimal import Decimal, getcontext
import datetime
from flask_discord_interactions import Response

def fetch_rate(currency: str) -> Decimal:
    """
    Contact the Redis server to fetch the latest conversion rate for this currency.

    Returns a Decimal representing the conversion rate from Euros to this currency.
    A value of 5 for the input USD would mean that 1 EUR = 5 USD.
    
    If currency is "EUR", returns Decimal(1), because a EUR-to-EUR
    conversion is unity by definition.

    If the currency does not exist, raises FileNotFoundError.
    """

    db = redis.Redis('redis_currency')

    if currency.upper() == 'EUR':
        return Decimal(1)
    
    value = db.get(currency.upper())
    if value is None:
        raise FileNotFoundError('no such currency found:', currency.upper())

    return Decimal(value.decode())

def fetch_date() -> datetime.date:
    """
    Contact the Redis server for the date of the latest update.
    """
    db = redis.Redis('redis_currency')

    date = db.get('date').decode()
    if date is None: return None
    
    return datetime.date.fromisoformat(date)

def convert_number(amount, from_currency: str, to_currency: str) -> Decimal:
    """
    Return the number of "to_currency" equal to "amount" of "from_currency".
    """

    from_rate = fetch_rate(from_currency)
    to_rate = fetch_rate(to_currency)
    amt = Decimal(amount)
    amt_in_euros = amt / from_rate
    amt_in_target = amt_in_euros * to_rate
    return amt_in_target

def fetch_currencies() -> [str]:
    """
    Return all the known currencies.
    """
    db = redis.Redis('redis_currency')
    
    currencies = []
    cursor = 0

    loop = 0
    while (currencies == []) or cursor != 0:
        loop += 1
        if loop > 5: return []
        cursor, new_currencies = db.scan(cursor)
        new_currencies = [x.decode() for x in new_currencies]
        try:
            new_currencies.remove('date')
        except ValueError: pass
        currencies.extend(new_currencies)
    currencies = list(set(currencies))
    currencies.append('EUR')
    currencies.sort()
    return currencies


def init(discord):
    @discord.command(name='convert', annotations={'amount': 'The decimal value of the source currency', 'from_currency': 'Source currency name', 'to_currency': 'Target currency name'})
    def convert(ctx, amount: str, from_currency: str, to_currency: str):
        """
        Convert currencies using the latest currency data
        """
        getcontext().prec = 6  # should be enough for currency conversion needs

        try:
            amount = Decimal(amount)
        except:
            return Response(content=f'This is not a valid decimal number: `{amount}`', ephemeral=True)
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        date = fetch_date()
        if date is None:
            return Response(content='No data available now, please try again later or contact this bot\'s maintainer.', ephemeral=True)
        try:
            target_amount = convert_number(amount, from_currency, to_currency)
            return f'{amount} {from_currency} is {target_amount} {to_currency} as of {date.isoformat()}'
        except FileNotFoundError:
            currencies = fetch_currencies()
            if not currencies:
                return Response(content='No data available now, please try again later or contact this bot\'s maintainer.', ephemeral=True)
            currencies = [f'`{i}`' for i in currencies]
            currencies = ', '.join(currencies)
            return Response(content=f'One of the currencies was not recognized. These are the available currencies: {currencies}', ephemeral=True)
    return convert
