import oandapy
import datetime
from BABAReasoning import credentials


class MarketDataSource:

    def __init__(self):
        self.oanda = oandapy.API(environment=credentials.oanda_environment,
                                 access_token=credentials.oanda_access_token)

    # Queries real time market data provider
    # for current best ask price (oanda)
    def request(self, symbol):
        response = self.oanda.get_prices(instruments=symbol)
        prices = response.get("prices")
        time = prices[0].get("time")
        asking_price = prices[0].get("ask")

        return RealTimeTick(time, asking_price)


class RealTimeTick:

    # time and asking_prices arguments are strings
    def __init__(self, time, asking_price):
        self.time = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")
        self.asking_price = float(asking_price)
